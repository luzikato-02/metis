from __future__ import annotations

"""
Convenience entrypoint for running locally without installation.

Prefer the installed CLI:
  python -m pip install -e .
  data-clean input.csv output.csv
"""

from data_cleaning.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

