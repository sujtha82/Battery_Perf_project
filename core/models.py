from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ToolTrace:
    """A record of one tool call executed by the agent."""

    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]


@dataclass
class AgentResult:
    """Final agent output and tool execution trace."""

    final_text: str
    tool_traces: List[ToolTrace]
