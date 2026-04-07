from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from core.data_loader import select_view
from core.formatting import round_json, top_records


def run(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze SOC readiness and SOC divergence between scenarios.

    Why:
        A battery cannot monetize price spikes if it reaches them with the wrong
        state of charge, so SOC positioning is a common secondary driver.
    """
    hist = select_view(df, "historical", "cleared")
    perf = select_view(df, "perfect", "cleared")

    merged = hist.merge(
        perf[["START_DATETIME", "SOC"]],
        on="START_DATETIME",
        suffixes=("_historical", "_perfect"),
        how="inner",
    )
    merged["SOC_DIFF"] = merged["SOC_perfect"] - merged["SOC_historical"]

    combined_prices = pd.concat([hist["PRICE_ENERGY"], perf["PRICE_ENERGY"]], ignore_index=True)
    high_price_threshold = float(combined_prices.quantile(0.90))
    low_price_threshold = float(hist["PRICE_ENERGY"].quantile(0.10))
    low_soc_threshold = float(hist["SOC"].quantile(0.10))
    high_soc_threshold = float(hist["SOC"].quantile(0.90))

    hist_high_price = hist[hist["PRICE_ENERGY"] >= high_price_threshold].copy()
    low_soc_high_price_count = int((hist_high_price["SOC"] <= low_soc_threshold).sum())
    high_soc_low_price_count = int(
        ((hist["SOC"] >= high_soc_threshold) & (hist["PRICE_ENERGY"] <= low_price_threshold)).sum()
    )

    return round_json({
        "historical_soc_min": float(hist["SOC"].min()),
        "historical_soc_max": float(hist["SOC"].max()),
        "perfect_soc_min": float(perf["SOC"].min()),
        "perfect_soc_max": float(perf["SOC"].max()),
        "historical_soc_range": float(hist["SOC"].max() - hist["SOC"].min()),
        "perfect_soc_range": float(perf["SOC"].max() - perf["SOC"].min()),
        "high_price_threshold": high_price_threshold,
        "low_soc_threshold": low_soc_threshold,
        "high_soc_threshold": high_soc_threshold,
        "low_price_threshold": low_price_threshold,
        "low_soc_high_price_count": low_soc_high_price_count,
        "high_soc_low_price_count": high_soc_low_price_count,
        "largest_soc_gaps": top_records(
            merged.assign(ABS_SOC_DIFF=lambda x: x["SOC_DIFF"].abs()).sort_values("ABS_SOC_DIFF", ascending=False),
            ["START_DATETIME", "SOC_historical", "SOC_perfect", "SOC_DIFF"],
            5,
        ),
    })
