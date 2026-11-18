# Token Economics & Pre-Build Budget Report

**Feature Name:** Academic AI Q&A Assistant (RAG)

## 1. Token Anatomy Breakdown

| Component | Tokens per Turn |
|---|---|
| System Prompt | 450 |
| Tool / Schema | 150 |
| User Prompt | 80 |
| Retrieval Context (RAG) | 1,400 |
| Output Generation | 350 |
| Reasoning Headroom | 100 |
| Turns per Session | 1 |
| **Total Tokens / Invocation** | **2,530** |

## 2. Scale & Traffic Sizing

- **Daily Active Users (DAU):** 1,000
- **Daily Requests:** 5,000
- **Monthly Requests:** 150,000
- **Average RPM:** 5.21
- **Peak RPM:** 15.62
- **Peak TPM Requirement:** 39,531

## 3. Multi-Model Financial Projections

| Model | Provider | Cost / Request | Cost / 1K Req | Monthly Projected Cost |
|---|---|---|---|---|
| Gemini 3.8 Flash | Google AI | $0.000261 | $0.2610 | $39.15 |
| Gemini 3.5 Flash Lite | Google AI | $0.000131 | $0.1305 | $19.57 |
| Gemini 3.8 Pro | Google AI | $0.004350 | $4.3500 | $652.50 |
| GPT-4o-mini | OpenAI | $0.000522 | $0.5220 | $78.30 |
| Llama 3.2 (Local Ollama) | Local/Self-hosted | $0.00 | $0.00 | $0.00 (Self-Hosted) |

## 4. Quota Assessment & Safety Headroom

| Provider Tier | Peak RPM | RPM % | Peak TPM | TPM % | Status |
|---|---|---|---|---|---|
| Gemini Free Tier (AI Studio) | 15.6 / 15 | 104.2% | 39,531 / 1,000,000 | 4.0% | BREACH |
| Gemini Pay-As-You-Go (Tier 1) | 15.6 / 1,000 | 1.6% | 39,531 / 4,000,000 | 1.0% | SAFE |
| Gemini Pay-As-You-Go (Tier 2 / Scale) | 15.6 / 4,000 | 0.4% | 39,531 / 10,000,000 | 0.4% | SAFE |

## 5. Architectural Recommendations

- **[CRITICAL]** *Quota & Infrastructure:* Free tier limits breached (Gemini Free Tier (AI Studio)). You must upgrade to a Pay-as-you-go key before deploying to production.
- **[INFO]** *Model Routing:* Gemini Flash saves $613.35/month compared to Pro. Use Flash as the default tier, and route only complex reasoning queries to Pro.
