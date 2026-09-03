import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOG_FILE = Path(__file__).resolve().parents[2] / "data" / "audit_logs.jsonl"


def log_decision(event: dict[str, Any]) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event,
    }

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, default=str) + "\n")