from __future__ import annotations

import argparse
from pathlib import Path

from .batch import BatchConfig, run_batch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate BDHEI from SPEI and STI station files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compute = subparsers.add_parser("compute", help="Batch-calculate BDHEI for station files.")
    compute.add_argument("--spei-dir", required=True, type=Path)
    compute.add_argument("--sti-dir", required=True, type=Path)
    compute.add_argument("--output-dir", required=True, type=Path)
    compute.add_argument("--months", nargs="+", type=int, default=[6, 7, 8])
    compute.add_argument("--spei-column", default="SPEI_3")
    compute.add_argument("--sti-column", default="STI")
    compute.add_argument("--date-column", default="date")
    compute.add_argument("--output-column", default="BDHEI")
    compute.add_argument("--sti-suffix", default="_STI_M_03.xlsx")
    compute.add_argument("--spei-glob", default="*.xlsx")
    compute.add_argument("--eps", type=float, default=1e-6)
    compute.add_argument("--grid-m", type=int, default=20)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "compute":
        config = BatchConfig(
            spei_dir=args.spei_dir,
            sti_dir=args.sti_dir,
            output_dir=args.output_dir,
            months=tuple(args.months),
            spei_column=args.spei_column,
            sti_column=args.sti_column,
            date_column=args.date_column,
            output_column=args.output_column,
            sti_suffix=args.sti_suffix,
            spei_glob=args.spei_glob,
            eps=args.eps,
            grid_m=args.grid_m,
        )
        run_batch(config)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
