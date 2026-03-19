"""Tests for structured logging."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest import TestCase

from new_england_weather_data_fetcher.structured_logging import append_structured_log


class StructuredLoggingTestCase(TestCase):
    """Verifies that JSON-line logs are written in an easy-to-parse format."""

    def test_append_structured_log_writes_one_json_line(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_file_path = Path(temporary_directory) / "weather.log.jsonl"
            append_structured_log(
                str(log_file_path), "INFO", "Testing logging.", state_name="Massachusetts"
            )
            written_line = log_file_path.read_text(encoding="utf-8").strip()

        parsed_line = json.loads(written_line)
        self.assertEqual("INFO", parsed_line["severity_name"])
        self.assertEqual("Testing logging.", parsed_line["message_text"])
        self.assertEqual("Massachusetts", parsed_line["context_values"]["state_name"])
