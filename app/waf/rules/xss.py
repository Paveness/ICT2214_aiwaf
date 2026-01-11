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
    r"on\w+\s*=",

    # common HTML injection vectors
    r"<\s*(img|svg|iframe|object|embed)\b",
]

# Compile once with IGNORECASE (DO NOT use inline (?i))
XSS_RE = re.compile("|".join(XSS_PATTERNS), re.IGNORECASE)


def xss_checks(req) -> Decision | None:
    """
    Detect reflected XSS attempts in query string.
    Conservative by design to avoid false positives.
    """
    query = req.query or ""
    if not query:
        return None

    if XSS_RE.search(query):
        return Decision(
            Action.BLOCK,
            ["xss:query"],
            status_code=403,
        )

    return None
