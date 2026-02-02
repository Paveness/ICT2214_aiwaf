import time
from datetime import datetime
from db_config import get_db_connection

def start_monitoring():
    print("🛡️  NEURO-WAF REAL-TIME MONITOR STARTED")
    print("---------------------------------------")
    print("Waiting for security events...")

    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            # 1. Get the last log ID so we only show NEW events
            cursor.execute("SELECT MAX(id) as last_id FROM event_logs")
            result = cursor.fetchone()
            last_seen_id = result['last_id'] if result['last_id'] else 0

            while True:
                # 2. Poll the database for any ID greater than what we last saw
                sql = """
                    SELECT * FROM event_logs 
                    WHERE id > %s 
                    ORDER BY id ASC
                """
                cursor.execute(sql, (last_seen_id,))
                new_logs = cursor.fetchall()

                # 3. Process new logs
                for log in new_logs:
                    last_seen_id = log['id']
                    timestamp = log['timestamp'].strftime('%H:%M:%S')
                    ip = log['source_ip']
                    attack = log['attack_type']
                    action = log['action_taken']
                    
                    # Color coding for terminal output
                    icon = "🟢" if action == "ALLOWED" else "🔴"
                    if action == "FLAGGED": icon = "🟡"

                    print(f"[{timestamp}] {icon} {action}: {attack} detected from {ip}")

                # 4. Wait before next check (Short Polling)
                time.sleep(2)

    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped.")
    finally:
        conn.close()

if __name__ == "__main__":
    start_monitoring()