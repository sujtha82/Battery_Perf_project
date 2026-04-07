from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from core.data_loader import select_view
from core.formatting import round_json, top_records


def run(df: pd.DataFrame) -> Dict[str, Any]:
    """Compare cleared dispatch between historical and perfect scenarios.

    Why:
        Dispatch mismatch shows whether the historical strategy moved energy at
        the wrong times even when facing the same market timeline.
    """
    hist = select_view(df, "historical", "cleared")
    perf = select_view(df, "perfect", "cleared")

    merged = hist.merge(
        perf,
        on="START_DATETIME",
        suffixes=("_historical", "_perfect"),
        how="inner",
    )

    merged["NET_DISPATCH_historical"] = merged["DISCHARGE_ENERGY_historical"] - merged["CHARGE_ENERGY_historical"]
    merged["NET_DISPATCH_perfect"] = merged["DISCHARGE_ENERGY_perfect"] - merged["CHARGE_ENERGY_perfect"]
    merged["DISPATCH_DIFF"] = merged["NET_DISPATCH_perfect"] - merged["NET_DISPATCH_historical"]
    merged["ABS_DISPATCH_DIFF"] = merged["DISPATCH_DIFF"].abs()
    merged["REVENUE_DIFF"] = merged["REVENUE_ENERGY_perfect"] - merged["REVENUE_ENERGY_historical"]

    return round_json({
        "aligned_intervals": len(merged),
        "total_abs_dispatch_diff": float(merged["ABS_DISPATCH_DIFF"].sum()),
        "mean_abs_dispatch_diff": float(merged["ABS_DISPATCH_DIFF"].mean()) if len(merged) else 0.0,
        "total_revenue_diff": float(merged["REVENUE_DIFF"].sum()),
        "largest_dispatch_mismatches": top_records(
            merged.sort_values("ABS_DISPATCH_DIFF", ascending=False),
            [
                "START_DATETIME",
                "PRICE_ENERGY_historical",
                "NET_DISPATCH_historical",
                "NET_DISPATCH_perfect",
                "DISPATCH_DIFF",
                "REVENUE_DIFF",
            ],
            5,
        ),
    })
