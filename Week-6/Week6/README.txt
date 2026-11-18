WEEK 6 — GOLDEN QUESTION SET & BASELINE RUN (RELEASE v0.1)
Topic: Write the golden question set with expected answers and sources; first baseline run — release v0.1
CO-Mapping: CO1

WHAT THIS PROJECT DOES
In Generative AI application and release engineering, a Golden Question Set (ground-truth
benchmark dataset) is the independent test suite used to evaluate model accuracy,
hallucination resistance, fact retrieval, and safety guardrails before deploying a release.

This project implements:
1. Authoritative ground-truth knowledge base documents in `sources/`:
   - `kl_university_academic_regulations.txt`: Course credits, attendance rules, CIE/SEE grading.
   - `genai_course_policy.txt`: Acceptable AI usage, credential security, free-tier quotas, release gates.
2. A curated Golden Question Set in `golden_dataset.json` with 12 benchmarks across 5 categories:
   - Fact Retrieval (Direct factual lookup)
   - Multi-Hop / Synthesis (Multi-rule reasoning)
   - Numerical Calculation (Grades, penalty percentages, minimum marks)
   - Negative / Out-of-Context (Testing that the model admits missing facts instead of hallucinating)
   - Guardrail & Safety Refusal (Testing prompt injection and credential theft refusal)
3. A provider-agnostic baseline runner (`baseline_runner.py`) supporting:
   - Google Gemini API (`gemini-3.8-flash` / `gemini-3.5-flash-lite`)
   - Local Ollama (`llama3.2`)
   - Offline Mock Provider (for testing and zero-cost CI/CD validation)
4. An automated benchmark evaluation engine (`evaluator.py`) that checks:
   - Required key facts inclusion
   - Forbidden hallucinated keywords
   - Safety refusal triggers
   - Latency (ms), input/output token counts
   - Release Gate v0.1 decision (Pass rate >= 80% and Guardrail Refusal = 100%)
5. Generates release artifacts:
   - `release_v0.1_results.json`: Full structured test-by-test log
   - `release_v0.1_report.md`: Executive release scorecard and category breakdown

FILES
- sources/: Directory containing official reference knowledge base documents
- golden_dataset.json: Curated ground-truth questions, expected answers, and sources
- evaluator.py: Benchmark scoring and release gate evaluation engine
- llm_client.py: Provider-agnostic client (Gemini, Ollama, Mock Baseline)
- baseline_runner.py: Orchestrates prompt framing, inference, evaluation, and report output
- main.py: Interactive CLI to run baseline evaluations or view datasets/reports
- test_evaluator.py: Unit tests validating dataset schema, scoring logic, and release gates
- requirements.txt: Python dependencies
- .env: Gemini API key and model selection
- .gitignore: Standard exclusions

SETUP IN VS CODE (WINDOWS POWERSHELL)
1. Open VS Code -> File -> Open Folder -> select the `Week6` folder.
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
   python -m unittest -v test_evaluator.py
   Or with pytest:
   pytest -v
6. Run the baseline evaluation:
   python main.py
   - Choose Option 1 (Gemini API) using your .env key,
     Option 2 (Local Ollama), or Option 3 (Offline Mock Provider).
   - Review question-by-question verdicts [PASS / FAIL], latency, and token consumption.
   - Review the final Release v0.1 Scorecard and generated release artifacts:
     `release_v0.1_results.json` and `release_v0.1_report.md`.

RELEASE CRITERIA (v0.1)
- Overall Benchmark Pass Rate >= 80%
- Safety Guardrail Refusal Pass Rate = 100%
- Status: APPROVED when both conditions are satisfied, otherwise BLOCKED.
