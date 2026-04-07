from __future__ import annotations

import os
from typing import Set

import pandas as pd

REQUIRED_COLUMNS: Set[str] = {
    "SCENARIO_NAME",
    "SCHEDULE_TYPE",
    "START_DATETIME",
    "SOC",
    "CHARGE_ENERGY",
    "DISCHARGE_ENERGY",
    "PRICE_ENERGY",
    "REVENUE_ENERGY",
}

EXPECTED_SCENARIOS = {"historical", "perfect"}
EXPECTED_SCHEDULE_TYPES = {"expected", "cleared"}


def load_battery_csv(csv_path: str) -> pd.DataFrame:
    """Load and validate a battery performance CSV.

    Why:
        The agent depends on a stable schema so that tools can stay reusable
        across datasets without code changes.

    Args:
        csv_path: Path to the input CSV.

    Returns:
        A validated dataframe sorted by START_DATETIME.

    Raises:
        FileNotFoundError: If the CSV does not exist.
        ValueError: If required schema elements are missing or invalid.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Alias handling for REVENUE -> REVENUE_ENERGY
    if "REVENUE" in df.columns and "REVENUE_ENERGY" not in df.columns:
        df = df.rename(columns={"REVENUE": "REVENUE_ENERGY"})

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df.copy()
    df["START_DATETIME"] = pd.to_datetime(df["START_DATETIME"], errors="coerce")
    if df["START_DATETIME"].isna().any():
        invalid_rows = int(df["START_DATETIME"].isna().sum())
        raise ValueError(
            f"Could not parse START_DATETIME in {invalid_rows} rows."
        )

    numeric_cols = [
        "SOC",
        "CHARGE_ENERGY",
        "DISCHARGE_ENERGY",
        "PRICE_ENERGY",
        "REVENUE_ENERGY",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["SCENARIO_NAME"] = df["SCENARIO_NAME"].astype(str).str.strip().str.lower()
    df["SCHEDULE_TYPE"] = df["SCHEDULE_TYPE"].astype(str).str.strip().str.lower()

    scenarios_present = set(df["SCENARIO_NAME"].unique())
    schedules_present = set(df["SCHEDULE_TYPE"].unique())

    if not EXPECTED_SCENARIOS.issubset(scenarios_present):
        raise ValueError(
            f"Expected scenarios {sorted(EXPECTED_SCENARIOS)}, found {sorted(scenarios_present)}"
        )

    if not EXPECTED_SCHEDULE_TYPES.issubset(schedules_present):
        raise ValueError(
            f"Expected schedule types {sorted(EXPECTED_SCHEDULE_TYPES)}, found {sorted(schedules_present)}"
        )

    return df.sort_values("START_DATETIME").reset_index(drop=True)


def select_view(df: pd.DataFrame, scenario_name: str, schedule_type: str) -> pd.DataFrame:
    """Return a filtered scenario/schedule slice sorted by time."""
    out = df[
        (df["SCENARIO_NAME"] == scenario_name.lower())
        & (df["SCHEDULE_TYPE"] == schedule_type.lower())
    ].copy()
    return out.sort_values("START_DATETIME").reset_index(drop=True)
