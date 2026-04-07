from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from core.data_loader import select_view
from core.formatting import round_json, top_records


def run(df: pd.DataFrame) -> Dict[str, Any]:
    """Estimate value left on the table from missed opportunities.

    Why:
        Traders need more than a gap number. They need to know whether value was
        missed at peaks, during charging windows, or both.
    """
    hist = select_view(df, "historical", "cleared")
    perf = select_view(df, "perfect", "cleared")

    merged = hist.merge(
        perf,
        on="START_DATETIME",
        suffixes=("_historical", "_perfect"),
        how="inner",
    )

    merged["NET_historical"] = merged["DISCHARGE_ENERGY_historical"] - merged["CHARGE_ENERGY_historical"]
    merged["NET_perfect"] = merged["DISCHARGE_ENERGY_perfect"] - merged["CHARGE_ENERGY_perfect"]
    merged["REVENUE_DIFF"] = merged["REVENUE_ENERGY_perfect"] - merged["REVENUE_ENERGY_historical"]

    high_price_threshold = float(merged["PRICE_ENERGY_historical"].quantile(0.90))
    low_price_threshold = float(merged["PRICE_ENERGY_historical"].quantile(0.10))

    missed_peak = merged[
        (merged["PRICE_ENERGY_historical"] >= high_price_threshold)
        & (merged["NET_perfect"] > merged["NET_historical"])
    ].copy()

    low_price_positioning = merged[
        (merged["PRICE_ENERGY_historical"] <= low_price_threshold)
        & (merged["NET_perfect"] < merged["NET_historical"])
    ].copy()

    return round_json({
        "missed_peak_discharge_value": float(missed_peak["REVENUE_DIFF"].sum()),
        "low_price_positioning_value": float(low_price_positioning["REVENUE_DIFF"].sum()),
        "missed_peak_discharge_intervals": top_records(
            missed_peak.sort_values("REVENUE_DIFF", ascending=False),
            [
                "START_DATETIME",
                "PRICE_ENERGY_historical",
                "NET_historical",
                "NET_perfect",
                "SOC_historical",
                "SOC_perfect",
                "REVENUE_DIFF",
            ],
            5,
        ),
        "low_price_positioning_intervals": top_records(
            low_price_positioning.sort_values("REVENUE_DIFF", ascending=False),
            [
                "START_DATETIME",
                "PRICE_ENERGY_historical",
                "NET_historical",
                "NET_perfect",
                "SOC_historical",
                "SOC_perfect",
                "REVENUE_DIFF",
            ],
            5,
        ),
    })
