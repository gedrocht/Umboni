"""Repository-root launcher for the beginner-friendly Umboni task runner."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    """Loads the in-repository Python package and runs the workflow entry point."""

    repository_root_directory = Path(__file__).resolve().parents[1]
    python_source_directory = repository_root_directory / "python"
    sys.path.insert(0, str(python_source_directory))

    from new_england_weather_data_fetcher.beginner_workflow import main as workflow_main

    return workflow_main()


if __name__ == "__main__":
    raise SystemExit(main())
