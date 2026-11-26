# Token Economics & Pre-Build Budget Report

**Feature Name:** Automated Code Review Agent

## 1. Token Anatomy Breakdown

| Component | Tokens per Turn |
|---|---|
| System Prompt | 800 |
| Tool / Schema | 300 |
| User Prompt | 120 |
| Retrieval Context (RAG) | 3,200 |
| Output Generation | 700 |
| Reasoning Headroom | 250 |
| Turns per Session | 2 |
| **Total Tokens / Invocation** | **10,740** |

## 2. Scale & Traffic Sizing

- **Daily Active Users (DAU):** 1,000
- **Daily Requests:** 5,000
- **Monthly Requests:** 150,000
- **Average RPM:** 5.21
- **Peak RPM:** 15.62
- **Peak TPM Requirement:** 167,812

## 3. Multi-Model Financial Projections

| Model | Provider | Cost / Request | Cost / 1K Req | Monthly Projected Cost |
|---|---|---|---|---|
| Gemini 3.8 Flash | Google AI | $0.001152 | $1.1524 | $172.86 |
| Gemini 3.5 Flash Lite | Google AI | $0.000576 | $0.5762 | $86.43 |
| Gemini 3.8 Pro | Google AI | $0.019206 | $19.2063 | $2,880.94 |
| GPT-4o-mini | OpenAI | $0.002305 | $2.3047 | $345.71 |
| Llama 3.2 (Local Ollama) | Local/Self-hosted | $0.00 | $0.00 | $0.00 (Self-Hosted) |

## 4. Quota Assessment & Safety Headroom

| Provider Tier | Peak RPM | RPM % | Peak TPM | TPM % | Status |
|---|---|---|---|---|---|
| Gemini Free Tier (AI Studio) | 15.6 / 15 | 104.2% | 167,812 / 1,000,000 | 16.8% | BREACH |
| Gemini Pay-As-You-Go (Tier 1) | 15.6 / 1,000 | 1.6% | 167,812 / 4,000,000 | 4.2% | SAFE |
| Gemini Pay-As-You-Go (Tier 2 / Scale) | 15.6 / 4,000 | 0.4% | 167,812 / 10,000,000 | 1.7% | SAFE |

## 5. Architectural Recommendations

- **[CRITICAL]** *Quota & Infrastructure:* Free tier limits breached (Gemini Free Tier (AI Studio)). You must upgrade to a Pay-as-you-go key before deploying to production.
- **[MEDIUM]** *Token Optimization:* Large RAG context (3200 tokens). Implement chunk reranking or top-k truncation to reduce token bloat by 30-50%.
- **[INFO]** *Model Routing:* Gemini Flash saves $2708.08/month compared to Pro. Use Flash as the default tier, and route only complex reasoning queries to Pro.
