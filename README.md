# Battery Performance Analysis System

A production-ready, tool-using LLM agent for battery trading performance analysis.

## 📁 Folder Structure

```text
battery_perf_system/
├── agent.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── assets/
│   └── execution_results.png
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── formatting.py
│   ├── models.py
│   ├── prompts.py
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

## 🚀 What it does

The system analyzes battery performance by comparing:
- **Historical** battery operation
- **Perfect Foresight** operation (ideal scenario)

It produces a comprehensive report in [**`output/`**](file:///c:/Users/aknar/Downloads/battery_perf_system/output) detailing:
- Revenue gap in dollars and percent.
- Primary and secondary drivers of the gap.
- Two actionable recommendations for traders.

## 💎 Results

![Execution Summary](file:///c:/Users/aknar/Downloads/battery_perf_system/assets/execution_results.png)

## 🛠 Setup

### 1. Create and activate a Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS / Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your Provider
Copy [**`.env.example`**](file:///c:/Users/aknar/Downloads/battery_perf_system/.env.example) to `.env` and configure your API keys. The system supports both **Groq** and **OpenAI**.

```bash
# Set your preferred provider (openai or groq)
PROVIDER=groq

# Add your keys
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

### 4. Put your CSV in `data/`
Example:
```text
data/Takehome_Problem_Agentic_Battery_Analysis_System_BLYTHB1_20260126.csv
```

### 5. Run the Analysis
```bash
python agent.py --csv data/your_file.csv
```

## 🧠 Architecture

- **Modular Tools**: Each analysis task is isolated in its own file in [**`tools/`**](file:///c:/Users/aknar/Downloads/battery_perf_system/tools).
- **Multi-Provider**: Refactored to work with high-speed LLMs like Groq (Llama 3.3) and GPT-4o.
- **Agentic Loop**: Uses an iterative tool-use loop rather than one-shot prompts.
- **Reliability**: Built-in Windows console encoding support and robust CSV validation.
