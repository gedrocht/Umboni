"""Copies the newest generated forecast JSON into the Angular public data directory."""

from __future__ import annotations

import shutil
from pathlib import Path


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    generated_forecast_path = (
        repository_root / "artifacts" / "generated" / "new-england-forecast.json"
    )
    frontend_forecast_path = (
        repository_root / "frontend" / "public" / "data" / "new-england-forecast-sample.json"
    )

    if not generated_forecast_path.exists():
        raise FileNotFoundError(
            "The generated forecast JSON does not exist. Run the Fortran simulator before synchronizing."
        )

    frontend_forecast_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(generated_forecast_path, frontend_forecast_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
