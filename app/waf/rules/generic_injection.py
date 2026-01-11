from __future__ import annotations
import re
from app.waf.decisions import Decision, Action

GENERIC_INJECTION_PATTERNS = [
    # Expression/templating injection markers
    r"\$\{[^}]{1,200}\}",     # ${...}
    r"\{\{[^}]{1,200}\}\}",   # {{...}}

    # LDAP injection operators (common forms)
    r"\(\|\(",                # (|(
    r"\(&\(",                 # (&(

    # JNDI-style payload marker (often used in exploit strings)
    r"\$\{jndi\s*:",
]

GENERIC_RE = re.compile("|".join(GENERIC_INJECTION_PATTERNS), re.IGNORECASE)


def generic_injection_checks(req) -> Decision | None:
    query = req.query or ""
    if not query:
        return None

    if GENERIC_RE.search(query):
        return Decision(
            Action.BLOCK,
            ["generic_injection:query"],
            status_code=403,
        )

    return None
