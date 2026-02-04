import time
from datetime import datetime
from typing import Any, Dict

from app.db.db_config import get_conn


def _parse_iso_ts(ts: str) -> str:
    """
    Convert ISO timestamp to HH:MM:SS (local display).
    Example input: '2026-02-04T05:48:03.751383+00:00'
    """
    if not ts:
        return "??:??:??"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except Exception:
        return "??:??:??"


def _extract_attack_type(reasons: list[str]) -> str:
    """
    Your reasons look like: 'cmd_injection:query:chain+cmd_or_exec'
    We'll take the first segment as the attack type.
    """
    if not reasons:
        return "None"
    first = reasons[0]
    return first.split(":")[0] if ":" in first else first


def start_monitoring():
    print("🛡️  NEURO-WAF REAL-TIME MONITOR STARTED")
    print("---------------------------------------")
    print("Waiting for security events... (Ctrl+C to stop)")

    conn = get_conn()
    if not conn:
        print("❌ Could not connect to DB.")
        return

    last_seen_id = 0

    try:
        with conn.cursor() as cursor:
            # 1) Start from latest row so we only show NEW events
            cursor.execute("SELECT COALESCE(MAX(log_id), 0) AS last_id FROM event_logs")
            result = cursor.fetchone()
            last_seen_id = int(result["last_id"] or 0)

            while True:
                # 2) Poll new logs (log_id > last_seen_id)
                cursor.execute(
                    """
                    SELECT log_id, raw_log
                    FROM event_logs
                    WHERE log_id > %s
                    ORDER BY log_id ASC
                    """,
                    (last_seen_id,),
                )
                rows = cursor.fetchall() or []

                for row in rows:
                    last_seen_id = row["log_id"]

                    raw: Dict[str, Any] = row["raw_log"] or {}

                    # Extract fields from your JSON structure
                    ts = _parse_iso_ts(raw.get("ts"))
                    ip = raw.get("client_ip", "unknown")
                    method = raw.get("method", "?")
                    path = raw.get("normalized_path") or raw.get("decoded_path") or "?"
                    target = raw.get("raw_target_wire") or path

                    decision = raw.get("decision") or {}
                    action = (decision.get("action") or "unknown").upper()
                    status_code = decision.get("status_code", "")
                    reasons = decision.get("reasons") or []

                    attack_type = _extract_attack_type(reasons)

                    ai = raw.get("ai") or {}
                    ai_score = ai.get("score", None)
                    ai_flagged = ai.get("flagged", False)

                    # Terminal icon based on action
                    icon = "🟢"
                    if action in ("BLOCK", "BLOCKED", "DENY"):
                        icon = "🔴"
                    elif action in ("FLAG", "FLAGGED"):
                        icon = "🟡"

                    # Build a readable line
                    reason_str = reasons[0] if reasons else "none"
                    score_str = f"{ai_score:.3f}" if isinstance(ai_score, (int, float)) else "n/a"
                    ai_str = f"AI={score_str}{'⚠️' if ai_flagged else ''}"

                    print(
                        f"[{ts}] {icon} {action} {status_code} | {attack_type} | {ip} | {method} {target} | {ai_str} | reason={reason_str}"
                    )

                time.sleep(2)

    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped.")
    finally:
        conn.close()
