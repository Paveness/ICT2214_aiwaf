from __future__ import annotations
import re
from app.waf.decisions import Decision, Action

# Conservative command injection detection (query only)
# We REQUIRE:
#   - a chaining/operator indicator   AND
#   - a suspicious command / execution primitive
#
# This avoids blocking innocent strings like "a&b" in normal text.

CHAIN_RE = re.compile(r"(?:;|\|\||&&|\||\n|\r)")
EXEC_PRIMITIVE_RE = re.compile(r"(?:\$\(|`[^`]{1,200}`)")  # $(...) or `...`

# Common OS commands often used in injection payloads
# (Keep this list conservative for V1)
COMMAND_WORD_RE = re.compile(
    r"\b(?:"
    r"cat|ls|pwd|whoami|id|uname|"
    r"curl|wget|nc|netcat|"
    r"bash|sh|powershell|cmd|"
    r"python|perl|php|ruby"
    r")\b",
    re.IGNORECASE,
)


def command_injection_checks(req) -> Decision | None:
    query = req.query or ""
    if not query:
        return None

    has_chain = CHAIN_RE.search(query) is not None
    has_exec = EXEC_PRIMITIVE_RE.search(query) is not None
    has_cmd = COMMAND_WORD_RE.search(query) is not None

    # Require "chain + (cmd OR exec primitive)" to reduce false positives
    if has_chain and (has_cmd or has_exec):
        return Decision(
            Action.BLOCK,
            ["cmd_injection:query"],
            status_code=403,
        )

    # Also block if exec primitive exists even without chain (high confidence)
    if has_exec:
        return Decision(
            Action.BLOCK,
            ["cmd_injection:exec_primitive"],
            status_code=403,
        )

    return None
