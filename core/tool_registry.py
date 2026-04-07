from __future__ import annotations

from typing import Any, Callable, Dict, List

import pandas as pd

from tools import (
    analyze_state_of_charge,
    compare_dispatch,
    compute_revenue_summary,
    compute_schedule_adherence,
    identify_high_price_intervals,
    identify_missed_opportunities,
)


def build_tool_specs() -> List[Dict[str, Any]]:
    """Return OpenAI function tool definitions in the standard format.

    Why:
        The model needs an explicit, stable contract describing what evidence it
        can request from Python. Using the standard nested format ensures compatibility
        across providers like OpenAI and Groq.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "compute_revenue_summary",
                "description": "Compute total cleared revenue for historical and perfect scenarios and the revenue gap.",
                "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
            }
        },
        {
            "type": "function",
            "function": {
                "name": "identify_high_price_intervals",
                "description": "Analyze top-price intervals and compare monetization between scenarios.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "quantile": {
                            "type": "number",
                            "description": "Quantile threshold for high-price intervals. Example: 0.90 means top 10 percent.",
                        }
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compare_dispatch",
                "description": "Compare cleared dispatch between historical and perfect scenarios on aligned timestamps.",
                "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_state_of_charge",
                "description": "Analyze SOC readiness and SOC gaps between scenarios.",
                "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compute_schedule_adherence",
                "description": "Compare expected vs cleared dispatch for one scenario.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scenario_name": {
                            "type": "string",
                            "enum": ["historical", "perfect"],
                            "description": "Scenario to analyze.",
                        }
                    },
                    "required": ["scenario_name"],
                    "additionalProperties": False,
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "identify_missed_opportunities",
                "description": "Estimate value left on the table from missed peak discharge and weak low-price positioning.",
                "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
            }
        },
    ]


def build_tool_map(df: pd.DataFrame) -> Dict[str, Callable[..., Dict[str, Any]]]:
    """Bind the current dataframe into each tool implementation."""

    def revenue_summary() -> Dict[str, Any]:
        return compute_revenue_summary.run(df)

    def high_price_intervals(quantile: float = 0.90) -> Dict[str, Any]:
        return identify_high_price_intervals.run(df, quantile=quantile)

    def dispatch_compare() -> Dict[str, Any]:
        return compare_dispatch.run(df)

    def soc_analysis() -> Dict[str, Any]:
        return analyze_state_of_charge.run(df)

    def schedule_adherence(scenario_name: str) -> Dict[str, Any]:
        return compute_schedule_adherence.run(df, scenario_name=scenario_name)

    def missed_opportunities() -> Dict[str, Any]:
        return identify_missed_opportunities.run(df)

    return {
        "compute_revenue_summary": revenue_summary,
        "identify_high_price_intervals": high_price_intervals,
        "compare_dispatch": dispatch_compare,
        "analyze_state_of_charge": soc_analysis,
        "compute_schedule_adherence": schedule_adherence,
        "identify_missed_opportunities": missed_opportunities,
    }
