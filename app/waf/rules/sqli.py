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
    query = req.query or ""
    if not query:
        return None

    if SQLI_RE.search(query):
        return Decision(
            Action.BLOCK,
            ["sqli:query"],
            status_code=403,
        )

    return None
