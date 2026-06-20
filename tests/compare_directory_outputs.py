from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare new BDHEI workbooks with legacy reference workbooks.")
    parser.add_argument("--reference-dir", required=True, type=Path)
    parser.add_argument("--reference-pattern", required=True)
    parser.add_argument("--reference-sheet", required=True)
    parser.add_argument("--reference-column", required=True)
    parser.add_argument("--new-dir", required=True, type=Path)
    parser.add_argument("--tolerance", type=float, default=1e-3)
    args = parser.parse_args()

    rows = []
    for new_path in sorted(args.new_dir.glob("*_BDHEI_BestCopula.xlsx")):
        station_id = new_path.name.removesuffix("_BDHEI_BestCopula.xlsx")
        old_path = args.reference_dir / args.reference_pattern.format(station_id=station_id)
        if not old_path.exists():
            rows.append((station_id, "missing_old", np.nan, np.nan, "", ""))
            continue

        old_data = pd.read_excel(old_path, sheet_name=args.reference_sheet)
        new_data = pd.read_excel(new_path, sheet_name="BDHEI")
        diff = np.abs(old_data[args.reference_column].to_numpy() - new_data["BDHEI"].to_numpy())
        rows.append(
            (
                station_id,
                "ok",
                float(diff.max()),
                float(diff.mean()),
                str(old_data["Copula_Type"].iloc[0]),
                str(new_data["Copula_Type"].iloc[0]),
            )
        )

    summary = pd.DataFrame(
        rows,
        columns=["station", "status", "max_abs_diff", "mean_abs_diff", "old_copula", "new_copula"],
    )
    if summary.empty:
        print("No new BDHEI workbooks found.")
        return 1

    copula_mismatch = summary[summary["old_copula"] != summary["new_copula"]]
    over_tolerance = summary[summary["max_abs_diff"] > args.tolerance]

    print(f"compared={len(summary)}")
    print("status_counts=")
    print(summary["status"].value_counts().to_string())
    print(f"copula_mismatches={len(copula_mismatch)}")
    print(f"max_abs_diff_overall={summary['max_abs_diff'].max():.12g}")
    print(f"stations_over_tolerance={len(over_tolerance)}")
    print("largest_differences=")
    print(summary.sort_values("max_abs_diff", ascending=False).head(10).to_string(index=False))

    if len(copula_mismatch) > 0:
        return 1
    if len(over_tolerance) > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
