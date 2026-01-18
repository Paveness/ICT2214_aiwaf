from __future__ import annotations
from urllib.parse import urlparse
import httpx
from fastapi import Request, Response
from app.settings import settings


HOP_BY_HOP_HEADERS = {
    "host",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


class ProxyService:
    def __init__(self) -> None:
        self.client: httpx.AsyncClient | None = None

    async def startup(self) -> None:
        timeout = httpx.Timeout(connect=5.0, read=60.0, write=60.0, pool=30.0)
        limits = httpx.Limits(max_keepalive_connections=50, max_connections=200)
        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            follow_redirects=False,
        )

    async def shutdown(self) -> None:
        if self.client is not None:
            await self.client.aclose()

    async def forward(self, request: Request) -> Response:
        if self.client is None:
            raise RuntimeError("ProxyService not started")

        raw_path = request.scope.get("raw_path", b"").decode("utf-8", errors="surrogateescape")
        raw_query = request.scope.get("query_string", b"").decode("utf-8", errors="surrogateescape")
        raw_target_wire = raw_path + (("?" + raw_query) if raw_query else "")

        # Copy headers but remove hop-by-hop headers
        headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP_BY_HOP_HEADERS}

        # ✅ IMPORTANT: remove these so httpx sets them correctly
        headers.pop("content-length", None)
        headers.pop("transfer-encoding", None)
        
        # If body was already read by WAF/controller, forward that exact bytes
        cached = getattr(request.state, "cached_body", None)
        if cached is not None:
            content = cached
        else:
            # Otherwise we can stream it (no prior consumption)
            async def body_stream():
                async for chunk in request.stream():
                    yield chunk
            content = body_stream()

        upstream_url = settings.ORIGIN_BASE_URL.rstrip("/") + raw_target_wire

        async with self.client.stream(
            method=request.method,
            url=upstream_url,
            headers=headers,
            content=content,   # <-- either bytes or async generator
        ) as upstream_resp:
            resp_headers = {k: v for k, v in upstream_resp.headers.items() if k.lower() not in HOP_BY_HOP_HEADERS}
            resp_content = await upstream_resp.aread()

            return Response(
                content=resp_content,
                status_code=upstream_resp.status_code,
                headers=resp_headers,
                media_type=upstream_resp.headers.get("content-type"),
            )
