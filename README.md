# Battery Performance Analysis System

A production-ready, tool-using LLM agent for battery trading performance analysis.

## Folder Structure

```text
battery_perf_system/
├── agent.py
├── requirements.txt
├── .env.example
├── README.md
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── formatting.py
│   ├── models.py
│   ├── report_writer.py
│   └── tool_registry.py
├── tools/
│   ├── __init__.py
│   ├── analyze_state_of_charge.py
│   ├── compare_dispatch.py
│   ├── compute_revenue_summary.py
│   ├── compute_schedule_adherence.py
│   ├── identify_high_price_intervals.py
│   └── identify_missed_opportunities.py
├── data/
│   └── .gitkeep
└── output/
    └── .gitkeep
```

## What it does

The system compares:
- `historical` battery operation
- `perfect` foresight battery operation

It produces:
- revenue gap in dollars and percent
- one primary driver
- one secondary driver
- two actionable recommendations with tradeoffs
- markdown report in `output/`
- console progress with emojis and ASCII tables

## Why this matches the task

The LLM does **not** process raw interval data directly.

Instead:
1. Python loads and validates the CSV
2. The LLM receives a set of tools
3. The LLM decides which tools to call
4. Each tool computes structured evidence from the dataframe
5. The LLM synthesizes the findings into a report

That gives you a real multi-step agent workflow instead of a one-shot prompt.

## Setup

### 1. Create and activate a virtual environment

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
Copy `.env.example` to `.env` and set:

```bash
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-5
```

### 4. Put your CSV in `data/`

Example:
```text
data/Takehome_Problem_Agentic_Battery_Analysis_System_BLYTHB1_20260126.csv
```

### 5. Run
```bash
python agent.py --csv data/Takehome_Problem_Agentic_Battery_Analysis_System_BLYTHB1_20260126.csv
```

Optional:
```bash
python agent.py --csv data/your_file.csv --report-name blyth_report.md
```

## Required Input Schema

The CSV must contain:
- `SCENARIO_NAME`
- `SCHEDULE_TYPE`
- `START_DATETIME`
- `SOC`
- `CHARGE_ENERGY`
- `DISCHARGE_ENERGY`
- `PRICE_ENERGY`
- `REVENUE_ENERGY`

Expected values:
- `SCENARIO_NAME`: `historical`, `perfect`
- `SCHEDULE_TYPE`: `expected`, `cleared`

## Output

### Console
- progress logs with emojis
- compact ASCII summary table
- report path

### File
- markdown report written to `output/`

## Architecture Notes

- Each tool is isolated in its own file
- `agent.py` is the main orchestrator
- `core/` contains shared infrastructure
- `output/` is used for generated reports
- calculations stay in Python tools
- synthesis stays in the LLM

## Recommended Submission Note

You can describe the solution like this:

> I built a modular LLM agent that uses domain-specific Python tools to analyze battery performance rather than passing raw interval data directly into a single prompt. The agent follows a multi-step workflow, computes structured evidence for revenue gap, dispatch mismatch, price-window underperformance, SOC readiness, and schedule adherence, then synthesizes the findings into a trader-facing report with evidence-backed recommendations.
