from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

from app.settings import settings


class LoggingService:
    """
    Writes JSON Lines (JSONL): 1 JSON object per line.
    Easy to inspect, easy to ingest later.
    """

    def __init__(self) -> None:
        os.makedirs(settings.LOG_DIR, exist_ok=True)
        self.log_path = os.path.join(settings.LOG_DIR, settings.ACCESS_LOG_FILE)

    def log_event(self, event: Dict[str, Any]) -> None:
        event.setdefault("ts", datetime.now(timezone.utc).isoformat())
        line = json.dumps(event, ensure_ascii=False)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
