"""Writes JSON-line logs that can be consumed by Grafana Loki through Promtail."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def append_structured_log(
    log_file_path: str,
    severity_name: str,
    message_text: str,
    **context_values: object,
) -> None:
    """Appends one structured log entry to a JSON-lines log file."""

    log_path = Path(log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    serialized_entry = {
        "timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
        "severity_name": severity_name,
        "message_text": message_text,
        "context_values": context_values,
    }

    with log_path.open("a", encoding="utf-8") as output_stream:
        output_stream.write(json.dumps(serialized_entry, sort_keys=True))
        output_stream.write("\n")
