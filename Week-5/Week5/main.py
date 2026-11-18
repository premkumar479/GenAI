"""
Main Application — Token Economics & Rate-Limit Budgeting
Week 5: Skilling Session — Pre-Build AI Feature Budgeting
"""

import json
import os
import sys
from token_budget import (
    FeatureTokenSpec,
    TrafficProfile,
    TokenEconomicsEngine,
    PRESET_FEATURES,
    DEFAULT_MODELS,
    DEFAULT_QUOTAS,
)


def print_header(title: str):
    line = "=" * 78
    print(f"\n{line}")
    print(f" {title.upper()}")
    print(f"{line}")


def print_section(title: str):
    line = "-" * 78
    print(f"\n{title}")
    print(line)


def format_table(headers, rows):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    header_str = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
    sep_str = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    print(header_str)
    print(sep_str)
    for row in rows:
        row_str = " | ".join(f"{str(val):<{col_widths[i]}}" for i, val in enumerate(row))
        print(row_str)


def select_feature() -> FeatureTokenSpec:
    print_section("STEP 1: SELECT OR DEFINE FEATURE SPECIFICATION")
    print("1. Academic AI Q&A Assistant (RAG Knowledge Base)")
    print("2. Automated Code Review Agent (Multi-turn Code Analysis)")
    print("3. Customer Support Chatbot (Multi-turn Conversational Support)")
    print("4. Custom Feature Specification (Enter your own token parameters)")

    choice = input("\nSelect an option [1-4] (default=1): ").strip() or "1"

    if choice in PRESET_FEATURES:
        spec = PRESET_FEATURES[choice]
        print(f"\nLoaded preset: '{spec.feature_name}'")
        return spec
    elif choice == "4":
        print("\nEnter custom feature token anatomy:")
        name = input("Feature Name (default='Custom Feature'): ").strip() or "Custom Feature"
        sys_tokens = int(input("System Prompt Tokens (instructions/guardrails) [default=500]: ").strip() or 500)
        schema_tokens = int(input("Tool/Schema Tokens [default=100]: ").strip() or 100)
        user_tokens = int(input("User Prompt Tokens [default=80]: ").strip() or 80)
        ctx_tokens = int(input("Retrieval Context (RAG) Tokens [default=1200]: ").strip() or 1200)
        out_tokens = int(input("Target Output Tokens [default=300]: ").strip() or 300)
        reasoning = int(input("Reasoning/Thinking Headroom Tokens [default=0]: ").strip() or 0)
        turns = int(input("Model calls / turns per user task [default=1]: ").strip() or 1)
        cache_hit = float(input("Prompt Caching Hit Rate (0.0 to 1.0) [default=0.3]: ").strip() or 0.3)

        return FeatureTokenSpec(
            feature_name=name,
            system_prompt_tokens=sys_tokens,
            schema_tokens=schema_tokens,
            user_prompt_tokens=user_tokens,
            retrieval_context_tokens=ctx_tokens,
            output_tokens=out_tokens,
            reasoning_headroom_tokens=reasoning,
            turns_per_session=turns,
            cache_hit_rate=cache_hit,
            cache_discount=0.50,
        )
    else:
        print("Invalid choice, defaulting to Option 1.")
        return PRESET_FEATURES["1"]


def get_traffic_profile() -> TrafficProfile:
    print_section("STEP 2: CONFIGURE SCALE & TRAFFIC PROFILE")
    dau_str = input("Estimated Daily Active Users (DAU) [default=1000]: ").strip() or "1000"
    queries_str = input("Average Queries/Invocations per user/day [default=5]: ").strip() or "5"
    peak_str = input("Peak-Hour Surge Multiplier (e.g., 3.0 = 3x avg load) [default=3.0]: ").strip() or "3.0"

    dau = int(dau_str)
    queries = float(queries_str)
    peak = float(peak_str)

    return TrafficProfile(
        dau=dau,
        queries_per_user_day=queries,
        peak_multiplier=peak,
        active_hours_per_day=16.0,
    )


def display_results(results: dict):
    feat = results["feature"]
    traf = results["traffic"]

    # 1. Token Anatomy Breakdown
    print_header(f"TOKEN ANATOMY & BUDGET REPORT: {feat['name']}")
    print_section("1. TOKEN CONSUMPTION PER INVOCATION")
    print(f"  * Static System Prompt Tokens   : {feat['system_prompt_tokens']:,}")
    print(f"  * Tool / Schema Tokens          : {feat['schema_tokens']:,}")
    print(f"  * User Query Tokens             : {feat['user_prompt_tokens']:,}")
    print(f"  * Retrieval Context (RAG) Tokens: {feat['retrieval_context_tokens']:,}")
    print(f"  * Base Output Tokens            : {feat['output_tokens']:,}")
    print(f"  * Reasoning Headroom Tokens     : {feat['reasoning_headroom_tokens']:,}")
    print(f"  * Calls/Turns per Task Session  : {feat['turns_per_session']}")
    print(f"  -> Total Input Tokens           : {feat['total_input_tokens']:,}")
    print(f"  -> Total Output Tokens          : {feat['total_output_tokens']:,}")
    print(f"  => TOTAL TOKENS / INVOCATION    : {feat['total_tokens_per_invocation']:,}")
    print(f"  * Prompt Cache Hit Rate         : {feat['cache_hit_rate']*100:.0f}% (50% discount on cached tokens)")

    # 2. Traffic Profile
    print_section("2. TRAFFIC & CONCURRENCY PROFILE")
    print(f"  * Daily Active Users (DAU)      : {traf['dau']:,}")
    print(f"  * Queries / User / Day          : {traf['queries_per_user_day']}")
    print(f"  * Daily Requests                : {traf['daily_requests']:,}")
    print(f"  * Monthly Requests (30 days)    : {traf['monthly_requests']:,}")
    print(f"  * Average Requests / Minute     : {traf['avg_rpm']:.2f} RPM")
    print(f"  * Peak Requests / Minute (Surge): {traf['peak_rpm']:.2f} RPM")
    print(f"  * Peak Tokens / Minute (TPM Req): {traf['peak_tpm']:,.0f} TPM")
    print(f"  * Projected Monthly Tokens      : {traf['monthly_tokens']:,}")

    # 3. Model Cost Comparison Table
    print_section("3. MULTI-MODEL COST COMPARISON (UNIT & MONTHLY BUDGET)")
    econ_headers = ["Model", "Provider", "Cost / Req", "Cost / 1K Req", "Monthly Cost", "Cache Savings"]
    econ_rows = []
    for e in results["economics"]:
        cost_req = f"${e['cost_per_request']:.6f}" if not e["is_local"] else "$0.000000"
        cost_k = f"${e['cost_per_1k_requests']:.4f}" if not e["is_local"] else "$0.00"
        cost_mo = f"${e['monthly_cost']:,.2f}" if not e["is_local"] else "$0.00 (Local)"
        savings = f"${e['monthly_cache_savings']:,.2f}" if e['monthly_cache_savings'] > 0 else "-"
        econ_rows.append([e["model"], e["provider"], cost_req, cost_k, cost_mo, savings])
    format_table(econ_headers, econ_rows)

    # 4. Quota & Rate-Limit Evaluation Table
    print_section("4. PROVIDER RATE-LIMIT & QUOTA ASSESSMENT")
    quota_headers = ["Provider Tier", "Peak RPM / Limit", "RPM %", "Peak TPM / Limit", "TPM %", "Daily Req / RPD", "Status"]
    quota_rows = []
    for q in results["quotas"]:
        rpm_str = f"{q['peak_rpm']:.1f} / {q['rpm_limit']:,}"
        tpm_str = f"{q['peak_tpm']:,.0f} / {q['tpm_limit']:,}"
        rpd_str = f"{q['daily_requests']:,} / {q['rpd_limit']:,}"
        status_str = f"[{q['status']}]"
        quota_rows.append([
            q["tier_name"],
            rpm_str,
            f"{q['rpm_usage_pct']}%",
            tpm_str,
            f"{q['tpm_usage_pct']}%",
            rpd_str,
            status_str,
        ])
    format_table(quota_headers, quota_rows)

    # 5. Pre-Build Architectural Recommendations
    print_section("5. PRE-BUILD ARCHITECTURAL RECOMMENDATIONS")
    for rec in results["recommendations"]:
        badge = f"[{rec['severity']}]"
        print(f"  {badge:<10} ({rec['category']}): {rec['message']}")


def save_reports(results: dict):
    # Save JSON Report
    json_path = "budget_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Save Markdown Report
    md_path = "budget_report.md"
    feat = results["feature"]
    traf = results["traffic"]

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Token Economics & Pre-Build Budget Report\n\n")
        f.write(f"**Feature Name:** {feat['name']}\n\n")

        f.write("## 1. Token Anatomy Breakdown\n\n")
        f.write("| Component | Tokens per Turn |\n|---|---|\n")
        f.write(f"| System Prompt | {feat['system_prompt_tokens']:,} |\n")
        f.write(f"| Tool / Schema | {feat['schema_tokens']:,} |\n")
        f.write(f"| User Prompt | {feat['user_prompt_tokens']:,} |\n")
        f.write(f"| Retrieval Context (RAG) | {feat['retrieval_context_tokens']:,} |\n")
        f.write(f"| Output Generation | {feat['output_tokens']:,} |\n")
        f.write(f"| Reasoning Headroom | {feat['reasoning_headroom_tokens']:,} |\n")
        f.write(f"| Turns per Session | {feat['turns_per_session']} |\n")
        f.write(f"| **Total Tokens / Invocation** | **{feat['total_tokens_per_invocation']:,}** |\n\n")

        f.write("## 2. Scale & Traffic Sizing\n\n")
        f.write(f"- **Daily Active Users (DAU):** {traf['dau']:,}\n")
        f.write(f"- **Daily Requests:** {traf['daily_requests']:,}\n")
        f.write(f"- **Monthly Requests:** {traf['monthly_requests']:,}\n")
        f.write(f"- **Average RPM:** {traf['avg_rpm']:.2f}\n")
        f.write(f"- **Peak RPM:** {traf['peak_rpm']:.2f}\n")
        f.write(f"- **Peak TPM Requirement:** {traf['peak_tpm']:,.0f}\n\n")

        f.write("## 3. Multi-Model Financial Projections\n\n")
        f.write("| Model | Provider | Cost / Request | Cost / 1K Req | Monthly Projected Cost |\n|---|---|---|---|---|\n")
        for e in results["economics"]:
            cost_req = f"${e['cost_per_request']:.6f}" if not e["is_local"] else "$0.00"
            cost_k = f"${e['cost_per_1k_requests']:.4f}" if not e["is_local"] else "$0.00"
            cost_mo = f"${e['monthly_cost']:,.2f}" if not e["is_local"] else "$0.00 (Self-Hosted)"
            f.write(f"| {e['model']} | {e['provider']} | {cost_req} | {cost_k} | {cost_mo} |\n")

        f.write("\n## 4. Quota Assessment & Safety Headroom\n\n")
        f.write("| Provider Tier | Peak RPM | RPM % | Peak TPM | TPM % | Status |\n|---|---|---|---|---|---|\n")
        for q in results["quotas"]:
            f.write(f"| {q['tier_name']} | {q['peak_rpm']:.1f} / {q['rpm_limit']:,} | {q['rpm_usage_pct']}% | {q['peak_tpm']:,.0f} / {q['tpm_limit']:,} | {q['tpm_usage_pct']}% | {q['status']} |\n")

        f.write("\n## 5. Architectural Recommendations\n\n")
        for rec in results["recommendations"]:
            f.write(f"- **[{rec['severity']}]** *{rec['category']}:* {rec['message']}\n")

    print(f"\nSaved budget report to:\n  - {os.path.abspath(json_path)}\n  - {os.path.abspath(md_path)}")


def main():
    print_header("WEEK 5 — TOKEN ECONOMICS & RATE-LIMIT BUDGET LAB")
    print("Pre-Build Unit Economics, Traffic Sizing, and API Quota Defense Engine")

    spec = select_feature()
    traffic = get_traffic_profile()

    engine = TokenEconomicsEngine()
    results = engine.evaluate_feature(spec, traffic)

    display_results(results)
    save_reports(results)


if __name__ == "__main__":
    main()
