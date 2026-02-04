# app/controllers/logs_controller.py
from __future__ import annotations

import json

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone

from app.models.logs_model import LogsModel


class LogsController:
    @staticmethod
    def _preset_to_since(preset: str) -> Optional[datetime]:
        now = datetime.now(timezone.utc)
        preset = (preset or "").lower()

        if preset == "5m":
            return now - timedelta(minutes=5)
        if preset == "1h":
            return now - timedelta(hours=1)
        if preset == "24h":
            return now - timedelta(hours=24)
        if preset == "7d":
            return now - timedelta(days=7)
        if preset == "all":
            return None
        return now - timedelta(hours=24)

    @staticmethod
    def _to_display_row(log_id: int, raw):
        # raw_log might be JSON string from MySQL
        if isinstance(raw, (str, bytes, bytearray)):
            try:
                raw = json.loads(raw)
            except Exception:
                raw = {}

        if not isinstance(raw, dict):
            raw = {}

        decision = raw.get("decision") or {}
        reasons = decision.get("reasons") or []

        # ---- attack type ----
        attack_type = "None"
        if reasons:
            first = str(reasons[0])
            attack_type = first.split(":")[0] if ":" in first else first

        # ---- action taken ----
        action = (decision.get("action") or "allow").lower()
        if action == "block":
            action_taken = "BLOCKED"
        elif action == "flag":
            action_taken = "FLAGGED"
        else:
            action_taken = "ALLOWED"

        # ---- method ----
        http_method = (raw.get("method") or "—").upper()

        # ---- request params (querystring) ----
        # Prefer raw["query"] if present, else extract from raw_target_wire
        request_params = raw.get("query") or ""
        raw_target_wire = raw.get("raw_target_wire") or ""

        if not request_params and isinstance(raw_target_wire, str):
            qidx = raw_target_wire.find("?")
            if qidx != -1 and qidx < len(raw_target_wire) - 1:
                request_params = raw_target_wire[qidx + 1 :]

        if not request_params:
            request_params = "—"

        # ---- request path ----
        request_path = (
            raw.get("raw_target_wire")
            or raw.get("normalized_path")
            or raw.get("decoded_path")
            or "/"
        )

        return {
            "id": log_id,
            "timestamp": raw.get("ts"),                 # keep ISO string
            "source_ip": raw.get("client_ip", "unknown"),
            "destination_ip": raw.get("destination_ip", "waf"),
            "geo_location": raw.get("geo_location", "N/A"),

            # ✅ new fields for your table
            "http_method": http_method,
            "request_params": request_params,

            "attack_type": attack_type,
            "action_taken": action_taken,
            "request_path": request_path,

            # optional for inspector modal
            "raw_log": raw,
        }

    @staticmethod
    def get_logs(
        search: str,
        attack_type: str,
        limit: int,
        page: int,
        time_mode: str,
        time_preset: str,
        start_date: Optional[str],
        end_date: Optional[str],
        cursor_id: Optional[int] = None,   # ✅ add this
    ) -> Dict[str, Any]:
        since_utc: Optional[datetime] = None
        until_utc: Optional[datetime] = None

        # ✅ NEW: live uses cursor_id, not datetime
        live_cursor_id: Optional[int] = None
        if time_mode == "preset":
            if time_preset == "live":
                live_cursor_id = cursor_id  # can be None -> means "from newest"
            else:
                since_utc = LogsController._preset_to_since(time_preset)

        elif time_mode == "after" and start_date:
            since_utc = LogsModel.parse_datetime_to_utc(start_date)

        elif time_mode == "before" and end_date:
            until_utc = LogsModel.parse_datetime_to_utc(end_date)

        elif time_mode == "between" and start_date and end_date:
            since_utc = LogsModel.parse_datetime_to_utc(start_date)
            until_utc = LogsModel.parse_datetime_to_utc(end_date)

        rows, total = LogsModel.fetch_logs(
            search=search,
            attack_type=attack_type,
            since_utc=since_utc,
            until_utc=until_utc,
            limit=limit,
            page=page,

            # ✅ pass cursor to model
            cursor_id=live_cursor_id,
            is_live=(time_mode == "preset" and time_preset == "live"),
        )

        logs = [LogsController._to_display_row(r["log_id"], r["raw_log"]) for r in rows]
        total_pages = max(1, (total + limit - 1) // limit)

        return {
            "logs": logs,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
            },
        }

    @staticmethod
    def get_attack_types():
        return LogsModel.fetch_attack_types()
