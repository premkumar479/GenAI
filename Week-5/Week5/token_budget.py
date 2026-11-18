"""
Token Economics & Rate-Limit Budget Engine
Week 5: Skilling Session — Token Economics & Pre-Build Budgeting
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass
class FeatureTokenSpec:
    feature_name: str
    system_prompt_tokens: int
    schema_tokens: int
    user_prompt_tokens: int
    retrieval_context_tokens: int
    output_tokens: int
    reasoning_headroom_tokens: int = 0
    turns_per_session: int = 1
    cache_hit_rate: float = 0.0  # Fraction of prompt tokens cached (0.0 - 1.0)
    cache_discount: float = 0.5  # Discount rate on cached tokens (e.g., 50%)

    @property
    def base_input_tokens_per_turn(self) -> int:
        return (
            self.system_prompt_tokens
            + self.schema_tokens
            + self.user_prompt_tokens
            + self.retrieval_context_tokens
        )

    @property
    def base_output_tokens_per_turn(self) -> int:
        return self.output_tokens + self.reasoning_headroom_tokens

    @property
    def total_input_tokens(self) -> int:
        return self.base_input_tokens_per_turn * self.turns_per_session

    @property
    def total_output_tokens(self) -> int:
        return self.base_output_tokens_per_turn * self.turns_per_session

    @property
    def total_tokens_per_invocation(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    @property
    def effective_billable_input_tokens(self) -> float:
        # Static tokens eligible for caching: system prompt + schemas + context
        cacheable_tokens = (
            self.system_prompt_tokens
            + self.schema_tokens
            + self.retrieval_context_tokens
        ) * self.turns_per_session
        non_cacheable_tokens = self.user_prompt_tokens * self.turns_per_session

        cached_tokens = cacheable_tokens * self.cache_hit_rate
        uncached_tokens = cacheable_tokens * (1.0 - self.cache_hit_rate) + non_cacheable_tokens

        # Billable equivalent: uncached at 1.0 + cached at (1.0 - cache_discount)
        billable_cached = cached_tokens * (1.0 - self.cache_discount)
        return uncached_tokens + billable_cached


@dataclass
class TrafficProfile:
    dau: int  # Daily Active Users
    queries_per_user_day: float  # Invocations per user per day
    peak_multiplier: float = 3.0  # Peak surge multiplier over average
    active_hours_per_day: float = 16.0  # Daily active operating window

    @property
    def daily_requests(self) -> int:
        return int(round(self.dau * self.queries_per_user_day))

    @property
    def monthly_requests(self) -> int:
        return self.daily_requests * 30

    @property
    def avg_rpm(self) -> float:
        total_active_minutes = self.active_hours_per_day * 60.0
        if total_active_minutes <= 0:
            return 0.0
        return self.daily_requests / total_active_minutes

    @property
    def peak_rpm(self) -> float:
        return self.avg_rpm * self.peak_multiplier


@dataclass
class ModelPricing:
    name: str
    provider: str
    input_price_per_m: float  # $ per 1,000,000 input tokens
    output_price_per_m: float  # $ per 1,000,000 output tokens
    is_local: bool = False


@dataclass
class ProviderQuota:
    tier_name: str
    rpm_limit: int  # Requests Per Minute
    tpm_limit: int  # Tokens Per Minute
    rpd_limit: int  # Requests Per Day


DEFAULT_MODELS: List[ModelPricing] = [
    ModelPricing(
        name="Gemini 3.8 Flash",
        provider="Google AI",
        input_price_per_m=0.075,
        output_price_per_m=0.300,
    ),
    ModelPricing(
        name="Gemini 3.5 Flash Lite",
        provider="Google AI",
        input_price_per_m=0.0375,
        output_price_per_m=0.150,
    ),
    ModelPricing(
        name="Gemini 3.8 Pro",
        provider="Google AI",
        input_price_per_m=1.250,
        output_price_per_m=5.000,
    ),
    ModelPricing(
        name="GPT-4o-mini",
        provider="OpenAI",
        input_price_per_m=0.150,
        output_price_per_m=0.600,
    ),
    ModelPricing(
        name="Llama 3.2 (Local Ollama)",
        provider="Local/Self-hosted",
        input_price_per_m=0.000,
        output_price_per_m=0.000,
        is_local=True,
    ),
]

DEFAULT_QUOTAS: List[ProviderQuota] = [
    ProviderQuota(
        tier_name="Gemini Free Tier (AI Studio)",
        rpm_limit=15,
        tpm_limit=1_000_000,
        rpd_limit=1_500,
    ),
    ProviderQuota(
        tier_name="Gemini Pay-As-You-Go (Tier 1)",
        rpm_limit=1_000,
        tpm_limit=4_000_000,
        rpd_limit=50_000,
    ),
    ProviderQuota(
        tier_name="Gemini Pay-As-You-Go (Tier 2 / Scale)",
        rpm_limit=4_000,
        tpm_limit=10_000_000,
        rpd_limit=500_000,
    ),
]


class TokenEconomicsEngine:
    def __init__(
        self,
        models: Optional[List[ModelPricing]] = None,
        quotas: Optional[List[ProviderQuota]] = None,
    ):
        self.models = models or DEFAULT_MODELS
        self.quotas = quotas or DEFAULT_QUOTAS

    def calculate_cost_per_request(
        self, spec: FeatureTokenSpec, model: ModelPricing
    ) -> float:
        if model.is_local:
            return 0.0
        input_cost = (spec.effective_billable_input_tokens / 1_000_000.0) * model.input_price_per_m
        output_cost = (spec.total_output_tokens / 1_000_000.0) * model.output_price_per_m
        return input_cost + output_cost

    def evaluate_feature(
        self, spec: FeatureTokenSpec, traffic: TrafficProfile
    ) -> Dict:
        # Token metrics
        input_tokens = spec.total_input_tokens
        output_tokens = spec.total_output_tokens
        total_tokens = spec.total_tokens_per_invocation

        # Monthly load metrics
        daily_req = traffic.daily_requests
        monthly_req = traffic.monthly_requests
        daily_tokens = daily_req * total_tokens
        monthly_tokens = monthly_req * total_tokens

        # Rate metrics
        avg_rpm = traffic.avg_rpm
        peak_rpm = traffic.peak_rpm
        peak_tpm = peak_rpm * total_tokens

        # Model economics
        economics_by_model = []
        for m in self.models:
            unit_cost = self.calculate_cost_per_request(spec, m)
            cost_per_k = unit_cost * 1_000.0
            daily_cost = unit_cost * daily_req
            monthly_cost = unit_cost * monthly_req

            # Calculate savings from prompt caching
            unoptimized_input_cost = (input_tokens / 1_000_000.0) * m.input_price_per_m
            unoptimized_unit_cost = unoptimized_input_cost + (output_tokens / 1_000_000.0) * m.output_price_per_m
            monthly_savings = max(0.0, (unoptimized_unit_cost - unit_cost) * monthly_req)

            economics_by_model.append({
                "model": m.name,
                "provider": m.provider,
                "cost_per_request": unit_cost,
                "cost_per_1k_requests": cost_per_k,
                "daily_cost": daily_cost,
                "monthly_cost": monthly_cost,
                "monthly_cache_savings": monthly_savings,
                "is_local": m.is_local,
            })

        # Quota checks
        quota_evaluations = []
        for q in self.quotas:
            rpm_ratio = peak_rpm / q.rpm_limit if q.rpm_limit else 0.0
            tpm_ratio = peak_tpm / q.tpm_limit if q.tpm_limit else 0.0
            rpd_ratio = daily_req / q.rpd_limit if q.rpd_limit else 0.0

            max_ratio = max(rpm_ratio, tpm_ratio, rpd_ratio)
            if max_ratio > 1.0:
                status = "BREACH"
            elif max_ratio >= 0.75:
                status = "WARNING"
            else:
                status = "SAFE"

            headroom_rpm = max(0, q.rpm_limit - int(round(peak_rpm)))
            headroom_tpm = max(0, q.tpm_limit - int(round(peak_tpm)))
            headroom_rpd = max(0, q.rpd_limit - daily_req)

            quota_evaluations.append({
                "tier_name": q.tier_name,
                "rpm_limit": q.rpm_limit,
                "peak_rpm": round(peak_rpm, 2),
                "rpm_usage_pct": round(rpm_ratio * 100, 1),
                "tpm_limit": q.tpm_limit,
                "peak_tpm": round(peak_tpm, 0),
                "tpm_usage_pct": round(tpm_ratio * 100, 1),
                "rpd_limit": q.rpd_limit,
                "daily_requests": daily_req,
                "rpd_usage_pct": round(rpd_ratio * 100, 1),
                "status": status,
                "headroom": {
                    "rpm": headroom_rpm,
                    "tpm": headroom_tpm,
                    "rpd": headroom_rpd,
                },
            })

        # Architectural recommendations
        recommendations = self._generate_recommendations(
            spec, traffic, quota_evaluations, economics_by_model
        )

        return {
            "feature": {
                "name": spec.feature_name,
                "system_prompt_tokens": spec.system_prompt_tokens,
                "schema_tokens": spec.schema_tokens,
                "user_prompt_tokens": spec.user_prompt_tokens,
                "retrieval_context_tokens": spec.retrieval_context_tokens,
                "output_tokens": spec.output_tokens,
                "reasoning_headroom_tokens": spec.reasoning_headroom_tokens,
                "turns_per_session": spec.turns_per_session,
                "total_input_tokens": input_tokens,
                "total_output_tokens": output_tokens,
                "total_tokens_per_invocation": total_tokens,
                "cache_hit_rate": spec.cache_hit_rate,
                "cache_discount": spec.cache_discount,
            },
            "traffic": {
                "dau": traffic.dau,
                "queries_per_user_day": traffic.queries_per_user_day,
                "peak_multiplier": traffic.peak_multiplier,
                "daily_requests": daily_req,
                "monthly_requests": monthly_req,
                "avg_rpm": round(avg_rpm, 2),
                "peak_rpm": round(peak_rpm, 2),
                "peak_tpm": round(peak_tpm, 0),
                "daily_tokens": daily_tokens,
                "monthly_tokens": monthly_tokens,
            },
            "economics": economics_by_model,
            "quotas": quota_evaluations,
            "recommendations": recommendations,
        }

    def _generate_recommendations(
        self,
        spec: FeatureTokenSpec,
        traffic: TrafficProfile,
        quota_evals: List[Dict],
        economics: List[Dict],
    ) -> List[Dict]:
        recs = []

        # 1. Free tier feasibility
        free_tier = next((q for q in quota_evals if "Free" in q["tier_name"]), None)
        if free_tier:
            if free_tier["status"] == "BREACH":
                recs.append({
                    "category": "Quota & Infrastructure",
                    "severity": "CRITICAL",
                    "message": f"Free tier limits breached ({free_tier['tier_name']}). You must upgrade to a Pay-as-you-go key before deploying to production.",
                })
            elif free_tier["status"] == "WARNING":
                recs.append({
                    "category": "Quota & Infrastructure",
                    "severity": "HIGH",
                    "message": f"Free tier near capacity ({free_tier['rpm_usage_pct']}% RPM or {free_tier['tpm_usage_pct']}% TPM). Peak surges will produce 429 ResourceExhausted errors.",
                })

        # 2. Token Anatomy & Prompt Optimization
        if spec.retrieval_context_tokens > 2000:
            recs.append({
                "category": "Token Optimization",
                "severity": "MEDIUM",
                "message": f"Large RAG context ({spec.retrieval_context_tokens} tokens). Implement chunk reranking or top-k truncation to reduce token bloat by 30-50%.",
            })

        if spec.cache_hit_rate < 0.2 and spec.system_prompt_tokens + spec.schema_tokens > 500:
            recs.append({
                "category": "Prompt Caching",
                "severity": "MEDIUM",
                "message": "Static prompts (system + schemas) exceed 500 tokens. Place static context at the prefix of prompts to enable API Prompt Caching and save ~50% on input costs.",
            })

        # 3. Model Routing
        flash_econ = next((e for e in economics if "Flash" in e["model"]), None)
        pro_econ = next((e for e in economics if "Pro" in e["model"]), None)
        if flash_econ and pro_econ:
            diff = pro_econ["monthly_cost"] - flash_econ["monthly_cost"]
            if diff > 10.0:
                recs.append({
                    "category": "Model Routing",
                    "severity": "INFO",
                    "message": f"Gemini Flash saves ${diff:.2f}/month compared to Pro. Use Flash as the default tier, and route only complex reasoning queries to Pro.",
                })

        # 4. Rate-Limiting & Buffering
        if traffic.peak_rpm > 50:
            recs.append({
                "category": "Concurrency & Rate-Limiting",
                "severity": "HIGH",
                "message": f"High peak concurrency ({traffic.peak_rpm:.1f} RPM). Implement a token-bucket rate limiter and exponential backoff retry queue to smooth traffic bursts.",
            })

        return recs


PRESET_FEATURES = {
    "1": FeatureTokenSpec(
        feature_name="Academic AI Q&A Assistant (RAG)",
        system_prompt_tokens=450,
        schema_tokens=150,
        user_prompt_tokens=80,
        retrieval_context_tokens=1400,
        output_tokens=350,
        reasoning_headroom_tokens=100,
        turns_per_session=1,
        cache_hit_rate=0.40,
        cache_discount=0.50,
    ),
    "2": FeatureTokenSpec(
        feature_name="Automated Code Review Agent",
        system_prompt_tokens=800,
        schema_tokens=300,
        user_prompt_tokens=120,
        retrieval_context_tokens=3200,
        output_tokens=700,
        reasoning_headroom_tokens=250,
        turns_per_session=2,
        cache_hit_rate=0.25,
        cache_discount=0.50,
    ),
    "3": FeatureTokenSpec(
        feature_name="Customer Support Chatbot",
        system_prompt_tokens=350,
        schema_tokens=100,
        user_prompt_tokens=50,
        retrieval_context_tokens=600,
        output_tokens=180,
        reasoning_headroom_tokens=0,
        turns_per_session=3,
        cache_hit_rate=0.50,
        cache_discount=0.50,
    ),
}
