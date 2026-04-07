from __future__ import annotations

from typing import Any, Dict, Iterable, List

import numpy as np
import pandas as pd
from tabulate import tabulate


def money(value: float) -> str:
    """Format a number as currency for trader-facing output."""
    return f"${value:,.2f}"


def pct(value: float) -> str:
    """Format a decimal fraction as a percentage string."""
    return f"{value * 100:.2f}%"


def round_json(obj: Any) -> Any:
    """Recursively round numeric values to keep tool payloads readable."""
    if isinstance(obj, dict):
        return {k: round_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_json(v) for v in obj]
    if isinstance(obj, np.floating):
        return round(float(obj), 6)
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, np.integer):
        return int(obj)
    return obj


def top_records(df: pd.DataFrame, columns: List[str], n: int = 5) -> List[Dict[str, Any]]:
    """Convert the top dataframe rows into JSON-safe records.

    Why:
        Tool results should be compact and serializable so the LLM sees only
        the most decision-relevant evidence instead of raw tables.
    """
    if df.empty:
        return []

    subset = df.loc[:, columns].head(n).copy()
    records = subset.to_dict(orient="records")
    clean_records: List[Dict[str, Any]] = []

    for record in records:
        clean: Dict[str, Any] = {}
        for key, value in record.items():
            if isinstance(value, pd.Timestamp):
                clean[key] = value.isoformat()
            elif isinstance(value, np.floating):
                clean[key] = round(float(value), 6)
            elif isinstance(value, np.integer):
                clean[key] = int(value)
            else:
                clean[key] = value
        clean_records.append(clean)

    return clean_records


def ascii_table(headers: Iterable[str], rows: Iterable[Iterable[Any]]) -> str:
    """Render a plain ASCII table for clear CLI output."""
    return tabulate(list(rows), headers=list(headers), tablefmt="github")
