from __future__ import annotations
from app.waf.decisions import Decision, Action

DEFAULT_ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}

MAX_URL_LEN = 2048
MAX_HEADER_BYTES = 16_384
MAX_BODY_BYTES = 1_000_000  # 1MB


def header_bytes(headers: dict[str, str]) -> int:
    return sum(len(k) + len(v) + 4 for k, v in headers.items())


def protocol_checks(req) -> Decision | None:
    if req.method.upper() not in DEFAULT_ALLOWED_METHODS:
        return Decision(Action.BLOCK, [f"method_not_allowed:{req.method}"], status_code=405)

    # ✅ IMPORTANT: check wire target length (includes query & preserves %xx)
    if len(req.raw_target_wire) > MAX_URL_LEN:
        return Decision(Action.BLOCK, ["url_too_long"], status_code=414)

    if header_bytes(req.headers) > MAX_HEADER_BYTES:
        return Decision(Action.BLOCK, ["headers_too_large"], status_code=431)

    if req.body_len > MAX_BODY_BYTES:
        return Decision(Action.BLOCK, ["body_too_large"], status_code=413)

    return None
