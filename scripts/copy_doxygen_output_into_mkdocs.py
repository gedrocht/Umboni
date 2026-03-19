"""Copies generated Doxygen HTML into the MkDocs site input tree."""

from __future__ import annotations

import shutil
from pathlib import Path


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    doxygen_html_directory = repository_root / "build" / "doxygen" / "html"
    mkdocs_target_directory = repository_root / "docs" / "generated-fortran-reference"

    if mkdocs_target_directory.exists():
        shutil.rmtree(mkdocs_target_directory)

    if not doxygen_html_directory.exists():
        raise FileNotFoundError(
            "The Doxygen HTML directory does not exist. Run Doxygen before copying the reference output."
        )

    shutil.copytree(doxygen_html_directory, mkdocs_target_directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

