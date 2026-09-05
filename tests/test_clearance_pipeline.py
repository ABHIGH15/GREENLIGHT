import unittest
import asyncio
from tools.clearance_tools import (
    calculate_string_similarity,
    soundex,
    check_name_phonetic_similarity,
    suggest_greeking_alternatives,
    check_mpaa_title_rules,
    check_nanpa_phone_number,
    GREEKING_CATALOG
)
from agents.pipeline import build_greenlight_pipeline
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner


class TestClearanceTools(unittest.TestCase):
    """Verifies algorithmic accuracy of local clearance screening tools."""

    def test_name_phonetic_similarity(self):
        # 1. Exact match
        exact = check_name_phonetic_similarity("Gabriel Sterling", "Gabriel Sterling")
        self.assertEqual(exact["phonetic_risk"], "HIGH")
        self.assertEqual(exact["similarity_score"], 1.0)

        # 2. Homophone / near-miss
        homophone = check_name_phonetic_similarity("Gabrielle Sterlin", "Gabriel Sterling")
        self.assertEqual(homophone["phonetic_risk"], "HIGH")
        self.assertTrue(homophone["last_name_soundex_match"])

        # 3. Clean fictional name
        clean = check_name_phonetic_similarity("Valen Mercer", "Gabriel Sterling")
        self.assertEqual(clean["phonetic_risk"], "LOW")
        self.assertLess(clean["similarity_score"], 0.40)

    def test_suggest_greeking_alternatives(self):
        # Firearms
        res = suggest_greeking_alternatives("firearms_tactical", "Glock 19")
        self.assertEqual(res["category"], "firearms_tactical")
        self.assertGreaterEqual(len(res["available_alternatives"]), 1)
        self.assertIn("Sleekcraft/Polaroid", res["clearance_advisory"])
        
        # Verify all alternatives have low similarity
        for alt in res["available_alternatives"]:
            self.assertLess(alt["string_similarity_to_original"], 0.35)
            self.assertEqual(alt["heuristic_check"], "PASS (Low orthographic similarity < 0.35)")

        # Luxury watches
        res_watch = suggest_greeking_alternatives("luxury_goods_watches", "Rolex Submariner")
        self.assertEqual(res_watch["category"], "luxury_goods_watches")
        self.assertIn("Belmont & Co.", [a["fictional_brand"] for a in res_watch["available_alternatives"]])

    def test_check_mpaa_title_rules_collision(self):
        # Flagship collision: "The Apprentice's Revenge" vs 2024 "The Apprentice"
        res = check_mpaa_title_rules("The Apprentice's Revenge")
        self.assertEqual(res["overall_risk"], "HIGH")
        self.assertTrue(res["has_collisions"])
        
        colliding_titles = [c["competing_work"] for c in res["collisions"]]
        self.assertTrue(any("The Apprentice" in t for t in colliding_titles))
        
        # Verify 2-3 pre-cleared alternatives are provided
        self.assertGreaterEqual(len(res["verified_alternative_titles"]), 2)
        for alt in res["verified_alternative_titles"]:
            # Confirm each alternative is clean
            alt_res = check_mpaa_title_rules(alt)
            self.assertFalse(alt_res["has_collisions"])

    def test_check_mpaa_title_rules_generic_word(self):
        # Single-word generic warning
        res = check_mpaa_title_rules("Revenge")
        self.assertEqual(res["overall_risk"], "MEDIUM")
        self.assertTrue(any("generic single-word" in f["issue"] for f in res["flags"]))

    def test_check_nanpa_phone_number(self):
        # 1. Non-reserved 555 number outside 0100-0199 block
        unauthorized = check_nanpa_phone_number("(415) 555-0250")
        self.assertEqual(unauthorized["status"], "UNAUTHORIZED_555_NUMBER")
        self.assertEqual(unauthorized["severity"], "HIGH")
        self.assertFalse(unauthorized["is_cleared"])
        self.assertIn("OUTSIDE the reserved NANPA/FCC fictional sub-block", unauthorized["issue"])
        self.assertIn("555-0142", unauthorized["recommended_action"])

        # 2. Cleared fictional entertainment block (0100-0199)
        cleared = check_nanpa_phone_number("(212) 555-0142")
        self.assertEqual(cleared["status"], "CLEARED_FICTIONAL_BLOCK")
        self.assertEqual(cleared["severity"], "LOW")
        self.assertTrue(cleared["is_cleared"])

        # 3. Real non-555 phone number
        real_num = check_nanpa_phone_number("(415) 867-5309")
        self.assertEqual(real_num["status"], "NON_555_REAL_NUMBER_RISK")
        self.assertEqual(real_num["severity"], "HIGH")
        self.assertFalse(real_num["is_cleared"])


class TestPipelineArchitecture(unittest.TestCase):
    """Verifies ADK agent topology, output keys, and tool registrations."""

    def test_pipeline_composition(self):
        pipeline = build_greenlight_pipeline()
        self.assertEqual(pipeline.name, "GreenlightClearancePipeline")
        self.assertEqual(len(pipeline.sub_agents), 3)

        parser, clearance_team, synthesizer = pipeline.sub_agents
        self.assertEqual(parser.name, "ScriptParserAgent")
        self.assertEqual(clearance_team.name, "ParallelClearanceTeam")
        self.assertEqual(synthesizer.name, "RiskSynthesizerAgent")

        # Verify parallel specialists
        specialists = clearance_team.sub_agents
        self.assertEqual(len(specialists), 3)
        
        name_agent, brand_agent, title_agent = specialists
        self.assertEqual(name_agent.name, "NameClearanceAgent")
        self.assertEqual(name_agent.output_key, "name_risks")
        self.assertTrue(any(callable(t) and t.__name__ == "check_name_phonetic_similarity" for t in name_agent.tools))

        self.assertEqual(brand_agent.name, "BrandClearanceAgent")
        self.assertEqual(brand_agent.output_key, "brand_risks")
        self.assertTrue(any(callable(t) and t.__name__ == "suggest_greeking_alternatives" for t in brand_agent.tools))
        self.assertTrue(any(callable(t) and t.__name__ == "check_nanpa_phone_number" for t in brand_agent.tools))

        self.assertEqual(title_agent.name, "TitleClearanceAgent")
        self.assertEqual(title_agent.output_key, "title_risks")
        self.assertTrue(any(callable(t) and t.__name__ == "check_mpaa_title_rules" for t in title_agent.tools))

    def test_runner_initialization(self):
        pipeline = build_greenlight_pipeline()
        session_service = InMemorySessionService()
        runner = Runner(agent=pipeline, app_name="greenlight", session_service=session_service)
        self.assertIsNotNone(runner)
        self.assertEqual(runner.agent.name, "GreenlightClearancePipeline")

    def test_schema_normalization(self):
        from api.models import RiskItem, SummaryStats, ClearanceReport, RiskCategory, RiskSeverity

        # 1. RiskItem normalizes issue and recommendation aliases
        item = RiskItem(
            id="RISK-NAME-01",
            entity="Test Person",
            category="NAME",
            severity="HIGH",
            issue="Real person collision with living official",
            recommendation="Rename to fictional surname"
        )
        self.assertEqual(item.description, "Real person collision with living official")
        self.assertEqual(item.recommended_action, "Rename to fictional surname")
        self.assertEqual(item.issue, item.description)
        self.assertEqual(item.recommendation, item.recommended_action)

        # 2. SummaryStats normalizes total_risks / high_risks aliases
        stats = SummaryStats.model_validate({
            "total_risks": 4,
            "high_risks": 2,
            "medium_risks": 1,
            "low_risks": 1
        })
        self.assertEqual(stats.total_flags, 4)
        self.assertEqual(stats.high_severity, 2)
        self.assertEqual(stats.medium_severity, 1)
        self.assertEqual(stats.low_severity, 1)

    def test_rate_limiter_setup(self):
        from services.rate_limiter import setup_adk_rate_limiter
        from google.adk.models.google_llm import Gemini

        setup_adk_rate_limiter()
        # Verify patched method name
        self.assertEqual(Gemini.generate_content_async.__name__, "paced_generate_content_async")


if __name__ == "__main__":
    unittest.main()
