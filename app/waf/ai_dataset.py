import json, time
from pathlib import Path

DATA_DIR = Path("app/ai_models/data")
DATA_DIR.mkdir(exist_ok=True)
AI_FILE = DATA_DIR / "ai_requests.jsonl"

def append_request_row(features: dict) -> None:
    row = {"ts": time.time(), "label": "baseline", "features": features}
    with AI_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
