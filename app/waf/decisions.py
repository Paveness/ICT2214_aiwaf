from dataclasses import dataclass
from enum import Enum
from typing import List


class Action(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    RATE_LIMIT = "rate_limit"
    LOG = "log"


@dataclass
class Decision:
    action: Action
    reasons: List[str]
    status_code: int = 200
