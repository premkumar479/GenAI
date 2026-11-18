"""
Main CLI Application — Golden Question Set & Baseline Evaluation (Release v0.1)
Week 6: Skilling Session — CO1
"""

import json
import os
import sys
from dotenv import load_dotenv

from baseline_runner import BaselineRunner
from llm_client import GeminiProvider, OllamaProvider, MockBaselineProvider


def print_banner():
    print("=" * 78)
    print(" WEEK 6 — GOLDEN QUESTION SET & BASELINE EVALUATION (RELEASE v0.1)")
    print(" Benchmark Evaluation Engine for Ground Truth Validation & Release Sign-Off")
    print("=" * 78)


def view_golden_dataset():
    path = "golden_dataset.json"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\nGOLDEN QUESTION DATASET ({len(data)} Benchmarks)")
    print("-" * 78)
    for item in data:
        print(f"[{item['id']}] Category: {item['category']}")
        print(f"  Q : {item['question']}")
        print(f"  A : {item['expected_answer']}")
        print(f"  Src: {item['source_doc']}")
        print(f"  Key Facts: {', '.join(item.get('key_facts', []))}")
        print()


def view_latest_report():
    md_path = "release_v0.1_report.md"
    if not os.path.exists(md_path):
        print("\nNo baseline evaluation run found yet. Run Option 1, 2, or 3 first.")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        print("\n" + f.read())


def main():
    load_dotenv(override=True)
    print_banner()

    print("\nSelect an action:")
    print("1. Run Baseline Evaluation with Google Gemini (Hosted API)")
    print("2. Run Baseline Evaluation with Ollama (Local Llama 3.2)")
    print("3. Run Baseline Evaluation in Offline Mock Mode (Zero-cost/Testing)")
    print("4. View Golden Question Dataset")
    print("5. View Latest Release v0.1 Report")

    choice = input("\nEnter choice [1-5] (default=3): ").strip() or "3"

    if choice == "1":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("ERROR: GEMINI_API_KEY is not set in .env!")
            return
        model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        print(f"\nInitializing Gemini Provider ({model})...")
        provider = GeminiProvider(api_key=api_key, model=model)
    elif choice == "2":
        print("\nInitializing Ollama Provider (llama3.2)...")
        provider = OllamaProvider(model="llama3.2")
    elif choice == "3":
        print("\nInitializing Offline Mock Provider for baseline run...")
        provider = MockBaselineProvider()
    elif choice == "4":
        view_golden_dataset()
        return
    elif choice == "5":
        view_latest_report()
        return
    else:
        print("Invalid choice. Running default Offline Mock mode...")
        provider = MockBaselineProvider()

    runner = BaselineRunner(provider=provider)
    output = runner.run_baseline(verbose=True)

    summary = output["summary"]
    print("\n" + "=" * 78)
    print(" BASELINE RUN COMPLETE — RELEASE v0.1 SCORECARD")
    print("=" * 78)
    print(f" Overall Pass Rate  : {summary['pass_rate_pct']}% ({summary['passed_questions']}/{summary['total_questions']})")
    print(f" Average Latency    : {summary['average_latency_ms']} ms")
    print(f" Total Tokens Used  : {summary['total_tokens']:,}")
    print(f" Release Gate Decision: [{summary['release_gate']['status']}]")
    print("=" * 78)


if __name__ == "__main__":
    main()
