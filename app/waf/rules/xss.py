from __future__ import annotations
import re
from app.waf.decisions import Decision, Action

# High-confidence reflected XSS patterns (QUERY STRING ONLY)
XSS_PATTERNS = [
    # <script> tags
    r"<\s*script\b",

    # javascript: URIs
    r"javascript\s*:",

    # inline event handlers (onerror=, onclick=, etc.)
    r"(?:<|\s|\"|\')on\w+\s*=",

    # common HTML injection vectors
    r"<\s*(img|svg|iframe|object|embed)\b",
]

# Compile once with IGNORECASE (DO NOT use inline (?i))
XSS_RE = re.compile("|".join(XSS_PATTERNS), re.IGNORECASE)


def xss_checks(req) -> Decision | None:
    """
    Detect reflected XSS attempts in query string and request body.
    Conservative by design to avoid false positives.
    """
    query = (req.query or "")
    body  = (req.body_text or "")

    # Nothing to inspect
    if not query and not body:
        return None

    # Query-based XSS
    if query and XSS_RE.search(query):
        return Decision(
            Action.BLOCK,
            ["xss:query"],
            status_code=403,
        )

    # Body-based XSS (POST/PUT/PATCH)
    if body and XSS_RE.search(body):
        return Decision(
            Action.BLOCK,
            ["xss:body"],
            status_code=403,
        )

    return None

