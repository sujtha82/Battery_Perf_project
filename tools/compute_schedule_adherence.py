from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from core.data_loader import select_view
from core.formatting import round_json, top_records


def run(df: pd.DataFrame, scenario_name: str) -> Dict[str, Any]:
    """Measure expected-vs-cleared dispatch deviation for one scenario.

    Why:
        This separates strategy quality from execution slippage. A good plan can
        still underperform if it does not clear as intended.
    """
    expected = select_view(df, scenario_name, "expected")
    cleared = select_view(df, scenario_name, "cleared")

    merged = expected.merge(
        cleared,
        on="START_DATETIME",
        suffixes=("_expected", "_cleared"),
        how="inner",
    )

    merged["NET_expected"] = merged["DISCHARGE_ENERGY_expected"] - merged["CHARGE_ENERGY_expected"]
    merged["NET_cleared"] = merged["DISCHARGE_ENERGY_cleared"] - merged["CHARGE_ENERGY_cleared"]
    merged["ABS_DIFF"] = (merged["NET_cleared"] - merged["NET_expected"]).abs()

    return round_json({
        "scenario_name": scenario_name,
        "aligned_intervals": len(merged),
        "mean_abs_dispatch_deviation": float(merged["ABS_DIFF"].mean()) if len(merged) else 0.0,
        "total_abs_dispatch_deviation": float(merged["ABS_DIFF"].sum()),
        "largest_expected_vs_cleared_mismatches": top_records(
            merged.sort_values("ABS_DIFF", ascending=False),
            ["START_DATETIME", "NET_expected", "NET_cleared", "ABS_DIFF", "PRICE_ENERGY_expected"],
            5,
        ),
    })
