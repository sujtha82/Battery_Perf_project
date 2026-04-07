from __future__ import annotations

import os
from datetime import datetime
from typing import List

from core.models import AgentResult


def build_markdown_report(csv_name: str, result: AgentResult) -> str:
    """Build a markdown report from the final agent response and tool trace.

    Why:
        A file artifact makes the system easier to review and aligns with the
        assessment's deliverable expectations.
    """
    lines: List[str] = []
    lines.append(f"# Battery Performance Analysis Report")
    lines.append("")
    lines.append(f"- Generated: {datetime.utcnow().isoformat()}Z")
    lines.append(f"- Source file: `{csv_name}`")
    lines.append("")
    lines.append("## Final Analysis")
    lines.append("")
    lines.append(result.final_text.strip())
    lines.append("")
    lines.append("## Tool Trace")
    lines.append("")
    for idx, trace in enumerate(result.tool_traces, start=1):
        lines.append(f"### Step {idx}: `{trace.tool_name}`")
        lines.append("")
        lines.append("**Arguments**")
        lines.append("")
        lines.append("```json")
        lines.append(__import__("json").dumps(trace.arguments, indent=2))
        lines.append("```")
        lines.append("")
        lines.append("**Result**")
        lines.append("")
        lines.append("```json")
        lines.append(__import__("json").dumps(trace.result, indent=2))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def write_report(output_dir: str, report_name: str, content: str) -> str:
    """Write the markdown report to disk and return the file path."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, report_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
