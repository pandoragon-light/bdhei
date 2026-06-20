from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from bdhei.batch import BatchConfig, process_station


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare new BDHEI output with a legacy reference workbook.")
    parser.add_argument("--spei-file", required=True, type=Path)
    parser.add_argument("--sti-file", required=True, type=Path)
    parser.add_argument("--reference-output", required=True, type=Path)
    parser.add_argument("--reference-sheet", required=True)
    parser.add_argument("--reference-column", required=True)
    parser.add_argument("--station-id", required=True)
    parser.add_argument("--tolerance", type=float, default=1e-4)
    args = parser.parse_args()

    config = BatchConfig(
        spei_dir=args.spei_file.parent,
        sti_dir=args.sti_file.parent,
        output_dir=Path("."),
        months=(6, 7, 8),
    )
    new_data, score_df = process_station(args.spei_file, args.sti_file, config)
    old_data = pd.read_excel(args.reference_output, sheet_name=args.reference_sheet)

    if len(new_data) != len(old_data):
        print(f"Row count mismatch: new={len(new_data)} old={len(old_data)}")
        return 1

    diff = np.abs(new_data["BDHEI"].to_numpy() - old_data[args.reference_column].to_numpy())
    max_diff = float(diff.max())
    mean_diff = float(diff.mean())
    old_copula = str(old_data["Copula_Type"].iloc[0])
    new_copula = str(new_data["Copula_Type"].iloc[0])

    print(f"station_id={args.station_id}")
    print(f"rows={len(new_data)}")
    print(f"old_copula={old_copula}")
    print(f"new_copula={new_copula}")
    print(f"max_abs_diff={max_diff:.12g}")
    print(f"mean_abs_diff={mean_diff:.12g}")
    print("candidate_scores=")
    print(score_df.to_string(index=False))

    if old_copula != new_copula:
        print("Copula type mismatch.")
        return 1
    if max_diff > args.tolerance:
        print(f"Maximum difference exceeds tolerance {args.tolerance}.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
