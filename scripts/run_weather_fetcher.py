"""Repository-root launcher for the Python weather fetcher."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    python_source_directory = repository_root / "python"
    sys.path.insert(0, str(python_source_directory))

    from new_england_weather_data_fetcher.command_line_interface import main as fetcher_main

    return fetcher_main()


if __name__ == "__main__":
    raise SystemExit(main())
