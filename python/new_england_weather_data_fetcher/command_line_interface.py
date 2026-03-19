"""Command-line entry point for the free weather data fetcher."""

from __future__ import annotations

import argparse
import sys

from .comma_separated_values_output import write_normalized_records_to_csv
from .provider_clients import fetch_all_normalized_weather_records
from .structured_logging import append_structured_log


def build_argument_parser() -> argparse.ArgumentParser:
    """Builds the command-line interface for beginners and automation tools."""

    argument_parser = argparse.ArgumentParser(
        description=(
            "Fetch 24 hours of free weather data for representative New England locations "
            "and write a normalized CSV file for the Fortran simulator."
        )
    )
    argument_parser.add_argument(
        "--output-csv",
        default="artifacts/generated/provider-observations.csv",
        help="Path where the normalized provider CSV file should be written.",
    )
    argument_parser.add_argument(
        "--log-file",
        default="artifacts/logs/python-fetcher.log.jsonl",
        help="Path where structured JSON-line logs should be written.",
    )
    argument_parser.add_argument(
        "--maximum-hours",
        type=int,
        default=24,
        help="How many forecast hours should be retained from each provider.",
    )
    return argument_parser


def main() -> int:
    """Runs the end-to-end fetch and normalization pipeline."""

    parsed_arguments = build_argument_parser().parse_args()

    append_structured_log(
        parsed_arguments.log_file,
        "INFO",
        "The Python weather fetcher is starting.",
        output_csv_path=parsed_arguments.output_csv,
        maximum_hours=parsed_arguments.maximum_hours,
    )

    try:
        if parsed_arguments.maximum_hours < 1:
            raise ValueError("The --maximum-hours argument must be at least 1.")

        normalized_weather_records = fetch_all_normalized_weather_records(
            maximum_hours=parsed_arguments.maximum_hours,
            log_file_path=parsed_arguments.log_file,
        )
        write_normalized_records_to_csv(parsed_arguments.output_csv, normalized_weather_records)
    except (
        Exception
    ) as raised_exception:  # pragma: no cover - kept intentionally broad for CLI robustness.
        append_structured_log(
            parsed_arguments.log_file,
            "ERROR",
            "The Python weather fetcher failed.",
            exception_type=type(raised_exception).__name__,
            exception_message=str(raised_exception),
        )
        print(str(raised_exception), file=sys.stderr)
        return 1

    append_structured_log(
        parsed_arguments.log_file,
        "INFO",
        "The Python weather fetcher completed successfully.",
        record_count=len(normalized_weather_records),
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
