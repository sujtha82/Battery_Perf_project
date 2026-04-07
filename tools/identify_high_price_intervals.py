from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from core.data_loader import select_view
from core.formatting import round_json, top_records


def run(df: pd.DataFrame, quantile: float = 0.90) -> Dict[str, Any]:
    """Compare monetization in top-price intervals.

    Why:
        Underperformance often comes from failing to discharge when prices are
        highest, so this isolates the most valuable windows.
    """
    hist = select_view(df, "historical", "cleared")
    perf = select_view(df, "perfect", "cleared")

    combined_prices = pd.concat([hist["PRICE_ENERGY"], perf["PRICE_ENERGY"]], ignore_index=True)
    threshold = float(combined_prices.quantile(quantile))

    hist_hp = hist[hist["PRICE_ENERGY"] >= threshold].copy()
    perf_hp = perf[perf["PRICE_ENERGY"] >= threshold].copy()

    hist_hp["NET_DISPATCH"] = hist_hp["DISCHARGE_ENERGY"] - hist_hp["CHARGE_ENERGY"]
    perf_hp["NET_DISPATCH"] = perf_hp["DISCHARGE_ENERGY"] - perf_hp["CHARGE_ENERGY"]

    return round_json({
        "quantile": quantile,
        "price_threshold": threshold,
        "historical_high_price_revenue": float(hist_hp["REVENUE_ENERGY"].sum()),
        "perfect_high_price_revenue": float(perf_hp["REVENUE_ENERGY"].sum()),
        "high_price_revenue_gap": float(perf_hp["REVENUE_ENERGY"].sum() - hist_hp["REVENUE_ENERGY"].sum()),
        "historical_high_price_discharge": float(hist_hp["DISCHARGE_ENERGY"].sum()),
        "perfect_high_price_discharge": float(perf_hp["DISCHARGE_ENERGY"].sum()),
        "missed_peak_discharge": float(perf_hp["DISCHARGE_ENERGY"].sum() - hist_hp["DISCHARGE_ENERGY"].sum()),
        "top_historical_high_price_intervals": top_records(
            hist_hp.sort_values("PRICE_ENERGY", ascending=False),
            ["START_DATETIME", "PRICE_ENERGY", "CHARGE_ENERGY", "DISCHARGE_ENERGY", "REVENUE_ENERGY"],
            5,
        ),
        "top_perfect_high_price_intervals": top_records(
            perf_hp.sort_values("PRICE_ENERGY", ascending=False),
            ["START_DATETIME", "PRICE_ENERGY", "CHARGE_ENERGY", "DISCHARGE_ENERGY", "REVENUE_ENERGY"],
            5,
        ),
    })
