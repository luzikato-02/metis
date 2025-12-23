from __future__ import annotations

import argparse

from .app import run_cleaning_job
from .config import DataCleaningConfig


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="data-clean", description="Clean production data for analysis.")
    p.add_argument("input", help="Input file path (.csv/.xlsx/.parquet)")
    p.add_argument("output", help="Output file path (.csv/.xlsx/.parquet)")

    p.add_argument("--input-format", default=None, help="Override input format (csv/xlsx/xls/parquet)")
    p.add_argument("--output-format", default=None, help="Override output format (csv/xlsx/xls/parquet)")

    p.add_argument("--rpm-max", type=float, default=10_000)
    p.add_argument("--eff-min", type=float, default=75.0)
    p.add_argument("--eff-max", type=float, default=100.0)
    p.add_argument("--spindles", type=int, default=84)
    p.add_argument("--shift-hours", type=float, default=8.0)
    p.add_argument(
        "--keep-multi-style-shifts",
        action="store_true",
        help="Do not drop shifts where >1 style ran on same (date, shift, machine).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    cfg = DataCleaningConfig(
        rpm_max=args.rpm_max,
        efficiency_min=args.eff_min,
        efficiency_max=args.eff_max,
        spindles_per_side=args.spindles,
        shift_hours=args.shift_hours,
        drop_multi_style_shifts=not args.keep_multi_style_shifts,
    )

    run_cleaning_job(
        args.input,
        args.output,
        config=cfg,
        input_format=args.input_format,
        output_format=args.output_format,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

