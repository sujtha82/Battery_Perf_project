from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from core.data_loader import select_view
from core.formatting import round_json


def run(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute total cleared revenue for historical and perfect scenarios.

    Why:
        The revenue gap is the anchor metric for the rest of the analysis. It
        tells the agent how much value was left on the table.
    """
    hist = select_view(df, "historical", "cleared")
    perf = select_view(df, "perfect", "cleared")

    historical_revenue = float(hist["REVENUE_ENERGY"].sum())
    perfect_revenue = float(perf["REVENUE_ENERGY"].sum())
    gap = perfect_revenue - historical_revenue
    gap_pct_vs_historical = (gap / historical_revenue) if abs(historical_revenue) > 1e-12 else None

    return round_json({
        "historical_revenue": historical_revenue,
        "perfect_revenue": perfect_revenue,
        "gap": gap,
        "gap_pct_vs_historical": gap_pct_vs_historical,
        "historical_intervals": len(hist),
        "perfect_intervals": len(perf),
    })
