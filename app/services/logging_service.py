from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

from app.settings import settings
from app.db.mysql import get_conn

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

        # Extract request_id
        request_id = event.get("request_id")
        if not request_id:
            raise ValueError("Missing request_id in log event")

        sql = """
        INSERT INTO logs (request_id, log)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
          log = VALUES(log)
        """

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (request_id, json.dumps(event, ensure_ascii=False)),
                )
        finally:
            conn.close()