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

        ## ✅ EXACT request target as received: raw_path + raw query_string (no decoding/normalization)
        raw_path = request.scope.get("raw_path", b"").decode("utf-8", errors="surrogateescape")
        raw_query = request.scope.get("query_string", b"").decode("utf-8", errors="surrogateescape")

        raw_target_wire = raw_path + (("?" + raw_query) if raw_query else "")

        # 🔐 LOOP PROTECTION: prevent origin == proxy host:port
        parsed = urlparse(settings.ORIGIN_BASE_URL)
        origin_host = parsed.hostname
        origin_port = parsed.port or (443 if parsed.scheme == "https" else 80)

        incoming_host = request.headers.get("host", "")
        if ":" in incoming_host:
            in_host, in_port_str = incoming_host.split(":", 1)
            try:
                in_port = int(in_port_str)
            except ValueError:
                in_port = 80
        else:
            in_host, in_port = incoming_host, 80

        if in_host == origin_host and in_port == origin_port:
            return Response(
                content="Proxy loop detected: ORIGIN_BASE_URL points to the proxy itself.",
                status_code=500,
                media_type="text/plain",
            )

        upstream_url = settings.ORIGIN_BASE_URL.rstrip("/") + raw_target_wire

        # Copy headers but remove hop-by-hop headers
        headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP_BY_HOP_HEADERS}

        # Stream request body to upstream
        async def body_stream():
            async for chunk in request.stream():
                yield chunk

        async with self.client.stream(
            method=request.method,
            url=upstream_url,
            headers=headers,
            content=body_stream(),
        ) as upstream_resp:
            resp_headers = {k: v for k, v in upstream_resp.headers.items() if k.lower() not in HOP_BY_HOP_HEADERS}
            content = await upstream_resp.aread()

            return Response(
                content=content,
                status_code=upstream_resp.status_code,
                headers=resp_headers,
                media_type=upstream_resp.headers.get("content-type"),
            )
