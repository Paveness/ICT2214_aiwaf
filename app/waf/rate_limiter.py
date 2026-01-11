from __future__ import annotations
import time
from dataclasses import dataclass
from threading import Lock
from typing import Dict, Tuple

from app.waf.decisions import Decision, Action


@dataclass
class TokenBucket:
    capacity: int
    tokens: float
    refill_rate: float  # tokens per second
    last_refill: float


class RateLimiter:
    """
    Token-bucket rate limiter.
    Keyed by (client_ip, path).
    """

    def __init__(self) -> None:
        self.buckets: Dict[Tuple[str, str], TokenBucket] = {}
        self.lock = Lock()

        # Defaults (safe V1 values)
        self.capacity = 60           # max burst
        self.refill_rate = 1.0       # 1 token/sec = 60/min

    def _refill(self, bucket: TokenBucket, now: float) -> None:
        elapsed = now - bucket.last_refill
        if elapsed <= 0:
            return

        added = elapsed * bucket.refill_rate
        bucket.tokens = min(bucket.capacity, bucket.tokens + added)
        bucket.last_refill = now

    def check(self, client_ip: str | None, path: str) -> Decision | None:
        if not client_ip:
            return None  # cannot rate-limit unknown client

        key = (client_ip, path)
        now = time.monotonic()

        with self.lock:
            bucket = self.buckets.get(key)
            if not bucket:
                bucket = TokenBucket(
                    capacity=self.capacity,
                    tokens=self.capacity,
                    refill_rate=self.refill_rate,
                    last_refill=now,
                )
                self.buckets[key] = bucket

            self._refill(bucket, now)

            if bucket.tokens < 1:
                return Decision(
                    Action.RATE_LIMIT,
                    ["rate_limit:exceeded"],
                    status_code=429,
                )

            bucket.tokens -= 1

        return None
