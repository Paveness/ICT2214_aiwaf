from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, List
from urllib.parse import unquote_plus


def safe_unquote(value: str, max_rounds: int = 2) -> str:
    """
    Decode URL encoding safely a limited number of times.
    Prevents multi-decode bypass tricks.
    """
    out = value
    for _ in range(max_rounds):
        new = unquote_plus(out)
        if new == out:
            break
        out = new
    return out


def normalize_path(path: str) -> str:
    """
    Normalize path:
    - ensure leading /
    - collapse // into /
    - remove /./
    - resolve /../ (dot-segment removal)
    """
    if not path.startswith("/"):
        path = "/" + path

    while "//" in path:
        path = path.replace("//", "/")

    parts: List[str] = []
    for seg in path.split("/"):
        if seg == "" or seg == ".":
            continue
        if seg == "..":
            if parts:
                parts.pop()
            continue
        parts.append(seg)

    return "/" + "/".join(parts)


@dataclass
class NormalizedRequest:
    method: str
    raw_target_wire: str
    decoded_path: str
    normalized_path: str
    query: str
    headers: Dict[str, str]
    client_ip: Optional[str]
    body_len: int
