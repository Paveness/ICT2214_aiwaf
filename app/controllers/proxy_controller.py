import time
import uuid
import httpx
from urllib.parse import unquote_plus
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from app.waf.engine import WAFEngine
from app.waf.decisions import Action
from app.settings import settings
from app.proxy.normalization import NormalizedRequest, safe_unquote, normalize_path

router = APIRouter()
waf = WAFEngine()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def handle_all(request: Request, path: str):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    # ===== RAW PATH (ASGI, untouched) =====
    raw_path_bytes = request.scope.get("raw_path", b"")
    raw_path_wire = raw_path_bytes.decode("utf-8", errors="surrogateescape")

    # ===== DECODE + NORMALIZE PATH =====
    decoded_path = safe_unquote(raw_path_wire)
    normalized_path = normalize_path(decoded_path)

    # ===== QUERY =====
    raw_query = request.scope.get("query_string", b"").decode("utf-8", errors="surrogateescape")
    decoded_query = unquote_plus(raw_query)

    # ===== BODY SIZE ONLY (no body read yet) =====
    content_length = request.headers.get("content-length")
    body_len = int(content_length) if content_length and content_length.isdigit() else 0

    # ===== BUILD NORMALIZED REQUEST =====
    req_norm = NormalizedRequest(
        method=request.method,
        raw_target_wire=raw_path_wire + (("?" + raw_query) if raw_query else ""),
        decoded_path=decoded_path,
        normalized_path=normalized_path,
        query=decoded_query,
        headers=dict(request.headers),
        client_ip=request.client.host if request.client else None,
        body_len=body_len,
    )

    # ===== WAF DECISION =====
    decision = waf.evaluate(req_norm)
    effective_action = decision.action

    if settings.WAF_MODE == "shadow" and effective_action != Action.ALLOW:
        effective_action = Action.ALLOW

    logger = request.app.state.logging_service

    # ===== BLOCK =====
    if effective_action == Action.BLOCK:
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.log_event({
            "request_id": request_id,
            "mode": settings.WAF_MODE,
            "client_ip": req_norm.client_ip,
            "method": req_norm.method,
            "raw_target_wire": req_norm.raw_target_wire,
            "decoded_path": req_norm.decoded_path,
            "normalized_path": req_norm.normalized_path,
            "query": req_norm.query,
            "body_len": req_norm.body_len,
            "decision": {
                "action": decision.action,
                "reasons": decision.reasons,
                "status_code": decision.status_code,
            },
            "latency_ms": latency_ms,
        })
        return PlainTextResponse("Blocked by WAF", status_code=decision.status_code or 403)

    # ===== RATE LIMIT =====
    if effective_action == Action.RATE_LIMIT:
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.log_event({
            "request_id": request_id,
            "mode": settings.WAF_MODE,
            "client_ip": req_norm.client_ip,
            "method": req_norm.method,
            "raw_target_wire": req_norm.raw_target_wire,
            "decision": {
                "action": decision.action,
                "reasons": decision.reasons,
                "status_code": 429,
            },
            "latency_ms": latency_ms,
        })
        return PlainTextResponse("Too Many Requests", status_code=429)

    # ===== FORWARD =====
    proxy = request.app.state.proxy_service
    upstream_status = None
    error = None

    try:
        resp = await proxy.forward(request)
        upstream_status = resp.status_code
        return resp
    except httpx.RequestError as e:
        error = f"{type(e).__name__}: {e}"
        return PlainTextResponse("Upstream error", status_code=502)
    finally:
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.log_event({
            "request_id": request_id,
            "mode": settings.WAF_MODE,
            "client_ip": req_norm.client_ip,
            "method": req_norm.method,
            "raw_target_wire": req_norm.raw_target_wire,
            "decision": {
                "action": decision.action,
                "effective_action": effective_action,
                "reasons": decision.reasons,
                "status_code": decision.status_code,
            },
            "upstream": {
                "status_code": upstream_status,
                "error": error,
            },
            "latency_ms": latency_ms,
        })
