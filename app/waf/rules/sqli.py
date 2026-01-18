from __future__ import annotations
import re
from app.waf.decisions import Decision, Action

SQLI_PATTERNS = [
    # Boolean tautology
    r"(?:'|\")\s*or\s+1\s*=\s*1",

    # UNION SELECT
    r"union\s+select",

    # Comment truncation
    r"(?:--|#)\s*$",

    # Stacked queries
    r";\s*(select|insert|update|delete|drop)",

    # Time-based
    r"sleep\s*\(\s*\d+\s*\)",
]

SQLI_RE = re.compile("|".join(SQLI_PATTERNS), re.IGNORECASE)


def sqli_checks(req) -> Decision | None:
    query = (req.query or "")
    body  = (req.body_text or "")

    # Nothing to inspect
    if not query and not body:
        return None

    # Check query first
    if query and SQLI_RE.search(query):
        return Decision(
            Action.BLOCK,
            ["sqli:query"],
            status_code=403,
        )

    # Check body (POST/PUT/PATCH payload)
    if body and SQLI_RE.search(body):
        return Decision(
            Action.BLOCK,
            ["sqli:body"],
            status_code=403,
        )

    return None

