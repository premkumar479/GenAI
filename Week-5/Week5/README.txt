WEEK 5 — TOKEN ECONOMICS & RATE-LIMIT BUDGET LAB
Topic: Token economics: cost and rate-limit budget for a feature before building it
CO-Mapping: CO1

WHAT THIS PROJECT DOES
In Generative AI application engineering, features operate on purchase-per-request unit
economics. Before writing backend code or deploying an LLM feature, engineers must calculate
token consumption, unit cost per invocation, monthly projected expenditure, and peak
rate-limit limits (RPM and TPM) to prevent surprise bills and 429 ResourceExhausted outages.

This project provides an automated Token Economics & Quota Defense Engine that:
1. Deconstructs feature token anatomy (system prompt, function schemas, dynamic user query,
   retrieval context / RAG chunks, model response, and hidden reasoning headroom).
2. Computes unit economics ($/request) and scale projections (DAU, monthly volume, monthly spend).
3. Analyzes Prompt Caching discounts for static prefixes (50% input discount).
4. Models traffic concurrency: Average RPM, Peak Surge RPM, and Peak Tokens Per Minute (TPM).
5. Validates against Google Gemini Free Tier and Paid Tier 1/2 quotas (flagging SAFE, WARNING, BREACH).
6. Generates pre-build architectural recommendations and exports JSON and Markdown budget reports.

FILES
- token_budget.py: Core modeling classes (FeatureTokenSpec, TrafficProfile, TokenEconomicsEngine)
- main.py: Interactive CLI budgeting tool with presets, live tables, and report generator
- test_budget.py: Comprehensive unit tests for token math, caching, and quota breach detection
- requirements.txt: Python dependencies
- .env: Optional price rate overrides
- .gitignore: Standard Python git exclusion rules

MATHEMATICAL FORMULAS
1. Total Input Tokens per Turn:
   T_in = System_Prompt + Tool_Schemas + User_Query + RAG_Context

2. Total Output Tokens per Turn:
   T_out = Target_Output + Reasoning_Headroom

3. Total Tokens per Invocation:
   T_total = (T_in + T_out) * Turns_per_Session

4. Unit Cost per Request:
   Cost = (T_in_billable / 1,000,000 * Input_Price) + (T_out / 1,000,000 * Output_Price)

5. Peak Requests per Minute (RPM):
   RPM_avg = Daily_Requests / (Active_Hours * 60)
   RPM_peak = RPM_avg * Peak_Surge_Multiplier

6. Peak Tokens per Minute (TPM):
   TPM_peak = RPM_peak * T_total

SETUP IN VS CODE (WINDOWS POWERSHELL)
1. Open VS Code -> File -> Open Folder -> select the `Week5` folder.
2. Open Terminal -> New Terminal (ensure PowerShell is selected).
3. (Optional) Create and activate a virtual environment:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   If script execution is disabled, run:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
4. Install dependencies:
   python -m pip install -r requirements.txt
5. Run the unit test suite:
   python -m unittest -v test_budget.py
   Or with pytest:
   pytest -v
6. Run the budgeting tool:
   python main.py
   - Select a preset feature (e.g., 1. Academic AI Q&A Assistant) or build a custom feature.
   - Enter your projected Daily Active Users (DAU) and queries per user per day.
   - Review the Token Anatomy, Multi-Model Cost Matrix, and Rate-Limit Budget tables.
   - Generated reports will be saved as `budget_report.json` and `budget_report.md`.

ARCHITECTURAL DEFENSE CHECKLIST (PRE-BUILD)
- If Free Tier TPM/RPM is breached: upgrade to Paid tier before production launch.
- If RAG context > 2000 tokens: apply semantic reranking or chunk pruning to reduce costs.
- If static instructions > 500 tokens: enable prompt caching to save ~50% on input fees.
- If peak RPM > 50: deploy a token-bucket rate limiter with exponential backoff retries.
