from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

from openai import OpenAI

from core.config import load_settings
from core.data_loader import load_battery_csv
from core.formatting import ascii_table, money, pct
from core.models import AgentResult, ToolTrace
from core.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from core.report_writer import build_markdown_report, write_report
from core.tool_registry import build_tool_map, build_tool_specs


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Battery performance analysis agent")
    parser.add_argument("--csv", required=True, help="Path to the battery CSV")
    parser.add_argument("--prompt", default=USER_PROMPT_TEMPLATE, help="User prompt for the agent")
    parser.add_argument("--report-name", default="battery_report.md", help="Markdown report filename")
    parser.add_argument("--output-dir", default="output", help="Directory for markdown reports")
    return parser.parse_args()


def run_agent(client: OpenAI, model: str, prompt: str, tool_specs: List[Dict], tool_map: Dict) -> AgentResult:
    """Run the multi-step tool-using LLM workflow.

    Why:
        Refactored to use standard Chat Completions API for provider-agnostic compatibility (OpenAI, Groq, etc.).
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    traces: List[ToolTrace] = []
    
    # The tool_specs already include {"type": "function", ...}
    api_tools = tool_specs

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=api_tools,
            tool_choice="auto",
        )
        
        message = response.choices[0].message
        messages.append(message)
        
        if not message.tool_calls:
            return AgentResult(final_text=message.content or "", tool_traces=traces)
            
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            raw_args = tool_call.function.arguments
            
            try:
                function_args = json.loads(raw_args) if raw_args else {}
                if not isinstance(function_args, dict):
                    function_args = {}
            except json.JSONDecodeError:
                function_args = {}
            
            if function_name not in tool_map:
                raise ValueError(f"Model called unknown tool: {function_name}")
                
            result = tool_map[function_name](**function_args)
            traces.append(ToolTrace(tool_name=function_name, arguments=function_args, result=result))
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(result),
            })


def print_progress(message: str) -> None:
    """Print a progress line suitable for CLI runs."""
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        # Fallback to plain text if the console cannot handle emojis/unicode
        cleaned = message.encode("ascii", "ignore").decode("ascii")
        print(cleaned, flush=True)


def print_summary_table(report_text: str) -> None:
    """Print a small status table after the run.

    Why:
        Fast visual confirmation makes the CLI easier to use during take-home
        iteration, especially before opening the full markdown report.
    """
    lines = [line.strip() for line in report_text.splitlines() if line.strip()]
    gap_line = next((line for line in lines if "Total gap" in line or "gap:" in line.lower()), "See report")
    rows = [
        ["Status", "Complete ✅"],
        ["Summary", gap_line[:100]],
    ]
    try:
        print(ascii_table(["Field", "Value"], rows))
    except UnicodeEncodeError:
        # Fallback for Windows consoles that don't support the checkmark emoji
        rows[0][1] = "Complete"
        print(ascii_table(["Field", "Value"], rows))


def main() -> int:
    """Program entry point with production-style error handling."""
    try:
        args = parse_args()

        print_progress("🔧 Loading settings...")
        settings = load_settings()

        print_progress("📥 Loading and validating CSV...")
        df = load_battery_csv(args.csv)

        print_progress("🧰 Building tool registry...")
        tool_specs = build_tool_specs()
        tool_map = build_tool_map(df)

        print_progress(f"🤖 Starting LLM agent using {settings.provider}...")
        
        if settings.provider == "groq":
            client = OpenAI(
                api_key=settings.get_api_key(),
                base_url="https://api.groq.com/openai/v1"
            )
        else:
            client = OpenAI(api_key=settings.get_api_key())
            
        result = run_agent(
            client=client,
            model=settings.get_model(),
            prompt=args.prompt,
            tool_specs=tool_specs,
            tool_map=tool_map,
        )

        print_progress("📝 Writing markdown report...")
        report_md = build_markdown_report(os.path.basename(args.csv), result)
        report_path = write_report(args.output_dir, args.report_name, report_md)

        print_progress("")
        print_progress("🎯 Analysis complete")
        print_summary_table(result.final_text)
        print_progress("")
        print_progress(f"📄 Markdown report: {report_path}")

        return 0

    except Exception as exc:  # pragma: no cover
        try:
            print(f"Error: {exc}", file=sys.stderr)
        except UnicodeEncodeError:
            print(f"Error: {str(exc).encode('ascii', 'ignore').decode('ascii')}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
