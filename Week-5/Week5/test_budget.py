"""
Unit Tests for Week 5 — Token Economics Engine
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from token_budget import (
    FeatureTokenSpec,
    TrafficProfile,
    ModelPricing,
    ProviderQuota,
    TokenEconomicsEngine,
)


class TestTokenEconomics(unittest.TestCase):
    def setUp(self):
        self.spec = FeatureTokenSpec(
            feature_name="Test RAG Bot",
            system_prompt_tokens=500,
            schema_tokens=100,
            user_prompt_tokens=100,
            retrieval_context_tokens=1300,
            output_tokens=400,
            reasoning_headroom_tokens=100,
            turns_per_session=1,
            cache_hit_rate=0.0,
            cache_discount=0.5,
        )

        self.traffic = TrafficProfile(
            dau=1000,
            queries_per_user_day=4.0,
            peak_multiplier=3.0,
            active_hours_per_day=16.0,
        )

        self.engine = TokenEconomicsEngine()

    def test_token_sums(self):
        # Input = 500 + 100 + 100 + 1300 = 2000
        self.assertEqual(self.spec.total_input_tokens, 2000)
        # Output = 400 + 100 = 500
        self.assertEqual(self.spec.total_output_tokens, 500)
        # Total per invocation = 2500
        self.assertEqual(self.spec.total_tokens_per_invocation, 2500)

    def test_multi_turn_multiplier(self):
        multi_spec = FeatureTokenSpec(
            feature_name="Agent Multi-Turn",
            system_prompt_tokens=500,
            schema_tokens=100,
            user_prompt_tokens=100,
            retrieval_context_tokens=1300,
            output_tokens=400,
            turns_per_session=3,
        )
        self.assertEqual(multi_spec.total_input_tokens, 2000 * 3)
        self.assertEqual(multi_spec.total_output_tokens, 400 * 3)
        self.assertEqual(multi_spec.total_tokens_per_invocation, 2400 * 3)

    def test_prompt_caching_discount(self):
        # 1900 cacheable tokens (500+100+1300), 100 non-cacheable
        # 50% hit rate, 50% discount on cached
        cached_spec = FeatureTokenSpec(
            feature_name="Cached Bot",
            system_prompt_tokens=500,
            schema_tokens=100,
            user_prompt_tokens=100,
            retrieval_context_tokens=1300,
            output_tokens=400,
            cache_hit_rate=0.50,
            cache_discount=0.50,
        )
        # cached = 1900 * 0.5 = 950
        # uncached = 950 + 100 = 1050
        # billable = 1050 + (950 * 0.5) = 1050 + 475 = 1525
        self.assertEqual(cached_spec.effective_billable_input_tokens, 1525.0)

    def test_unit_cost_calculation(self):
        model = ModelPricing(
            name="Test Model",
            provider="TestProvider",
            input_price_per_m=1.00,  # $1 per 1M tokens
            output_price_per_m=2.00,  # $2 per 1M tokens
        )
        # 2000 input tokens -> (2000 / 1M) * 1 = 0.002
        # 500 output tokens -> (500 / 1M) * 2 = 0.001
        # Total cost per request = 0.003
        cost = self.engine.calculate_cost_per_request(self.spec, model)
        self.assertAlmostEqual(cost, 0.003, places=6)

    def test_traffic_scaling(self):
        self.assertEqual(self.traffic.daily_requests, 4000)
        self.assertEqual(self.traffic.monthly_requests, 120000)

        # 4000 requests / (16 hours * 60 min) = 4000 / 960 = 4.1667 RPM avg
        self.assertAlmostEqual(self.traffic.avg_rpm, 4.166666, places=3)
        # Peak RPM = 4.1667 * 3.0 = 12.5 RPM
        self.assertAlmostEqual(self.traffic.peak_rpm, 12.5, places=3)

    def test_quota_evaluation_breach_detection(self):
        # Peak RPM is 12.5, peak TPM is 12.5 * 2500 = 31,250 TPM
        # Free Tier: 15 RPM, 1500 RPD
        # Daily requests = 4000, which exceeds 1500 RPD -> BREACH
        results = self.engine.evaluate_feature(self.spec, self.traffic)
        free_tier = next(q for q in results["quotas"] if "Free" in q["tier_name"])
        self.assertEqual(free_tier["status"], "BREACH")
        self.assertGreater(free_tier["rpd_usage_pct"], 100.0)

    def test_local_ollama_zero_cost(self):
        local_model = ModelPricing(
            name="Llama 3.2",
            provider="Local",
            input_price_per_m=0.0,
            output_price_per_m=0.0,
            is_local=True,
        )
        cost = self.engine.calculate_cost_per_request(self.spec, local_model)
        self.assertEqual(cost, 0.0)


if __name__ == "__main__":
    unittest.main()
