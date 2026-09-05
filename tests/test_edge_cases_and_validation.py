import unittest
import asyncio
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.main import app
from api.routes import MAX_FILE_SIZE, MAX_TEXT_LENGTH, MIN_TEXT_LENGTH, ALLOWED_EXTENSIONS
from services.analysis_service import AnalysisService
from api.models import ClearanceReport, RiskSeverity


class TestInputValidationAndEdgeCases(unittest.TestCase):
    """Verifies edge cases, payload caps, extension filters, and error recovery."""

    def setUp(self):
        self.client = TestClient(app)

    def test_empty_json_payload_rejected(self):
        """Empty or < 20 character screenplay is rejected with 400."""
        response = self.client.post("/api/analyze", json={"script_text": "Too short"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("at least 20 characters", response.json()["detail"])

    def test_whitespace_only_payload_rejected(self):
        """Whitespace only payload is rejected with 400."""
        response = self.client.post("/api/analyze", json={"script_text": "   \n\n\t   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("at least 20 characters", response.json()["detail"])

    def test_oversized_payload_rejected(self):
        """Payloads exceeding MAX_TEXT_LENGTH (350,000 chars) are rejected with 400."""
        huge_text = "FADE IN:\nINT. ROOM - DAY\n" + ("A" * (MAX_TEXT_LENGTH + 100))
        response = self.client.post("/api/analyze", json={"script_text": huge_text})
        self.assertEqual(response.status_code, 400)
        self.assertIn("exceeds the maximum supported length", response.json()["detail"])

    def test_unsupported_file_extension_rejected(self):
        """Non-screenplay files (.exe, .zip, .png) are rejected immediately."""
        fake_binary = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00")
        response = self.client.post(
            "/api/analyze",
            files={"file": ("malicious_payload.exe", fake_binary, "application/octet-stream")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file format '.exe'", response.json()["detail"])

    def test_corrupted_pdf_rejected(self):
        """Corrupted PDF binary returns clear error explaining unreadable content."""
        corrupted_bytes = io.BytesIO(b"%PDF-1.4 [CORRUPTED BINARY TRASH WITH NO VALID XREF TABLE] \x00\xFF\xAA")
        response = self.client.post(
            "/api/analyze",
            files={"file": ("corrupted_screenplay.pdf", corrupted_bytes, "application/pdf")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Could not extract readable screenplay text", response.json()["detail"])

    def test_oversized_file_rejected(self):
        """Files exceeding MAX_FILE_SIZE (10MB) are rejected with 400."""
        oversized_data = io.BytesIO(b"A" * (MAX_FILE_SIZE + 1024))
        response = self.client.post(
            "/api/analyze",
            files={"file": ("huge_script.txt", oversized_data, "text/plain")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("exceeds the maximum limit of 10MB", response.json()["detail"])

    def test_valid_text_form_accepted(self):
        """Valid screenplay text submitted via form data returns 200 with analysis_id."""
        valid_script = (
            "FADE IN:\n\nINT. COFFEE SHOP - DAY\n\n"
            "SARAH sits at a corner booth reading a book on astrophysics. "
            "She sips her black coffee thoughtfully.\n\n"
            "SARAH\n(to herself)\nEverything is connected.\n"
        )
        response = self.client.post(
            "/api/analyze",
            data={"script_text": valid_script, "script_title": "Cosmic Whispers"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("analysis_id", data)
        self.assertEqual(data["status"], "started")


class TestCleanScriptAndDeterministicScoring(unittest.TestCase):
    """Verifies that completely clean scripts receive GREENLIGHT 100/100 and clean memos."""

    def test_clean_script_receives_perfect_score(self):
        service = AnalysisService()
        clean_text = (
            "FADE IN:\n\nEXT. MEADOW - DAWN\n\n"
            "A gentle breeze ripples through the high grass. "
            "A lone robin lands on a wooden fencepost.\n\n"
            "INT. CABIN - DAY\n\n"
            "ELENA prepares tea over a cast-iron kettle. "
            "No phones, no logos, no modern technology in sight."
        )
        report = asyncio.run(service._generate_report(
            analysis_id="test_clean_01",
            script_text=clean_text,
            script_title="Whispers of the Meadow"
        ))

        self.assertEqual(report.greenlight_score, 100)
        self.assertEqual(report.verdict, "GREENLIGHT")
        self.assertEqual(len(report.risks), 0)
        self.assertEqual(report.stats.total_flags, 0)
        self.assertEqual(report.stats.high_severity, 0)
        self.assertIn("0 legal clearance flags", report.underwriting_summary)
        self.assertIn("cleared for standard Errors & Omissions", report.underwriting_summary)
        self.assertNotIn("uninsurable exposure", report.underwriting_summary)


class TestSeededScriptsHitRate(unittest.TestCase):
    """Tests empirical detection hit-rate against isolated, single-issue landmines."""

    def setUp(self):
        self.service = AnalysisService()

    def test_name_collision_seeded_script(self):
        """Script seeded only with living executive Gabriel Sterling."""
        script = (
            "SCENE 1 - INT. BIOTECH BOARDROOM - NIGHT\n"
            "GABRIEL STERLING, ruthless biotechnology CEO, dumps toxic waste into the municipal reservoir.\n"
            "GABRIEL STERLING\nNo one will ever trace this to Sterling Therapeutics.\n"
        )
        report = asyncio.run(self.service._generate_report(
            analysis_id="test_seed_name",
            script_text=script,
            script_title="Reservoir Toxins"
        ))
        name_risks = [r for r in report.risks if r.category.value == "NAME"]
        self.assertGreaterEqual(len(name_risks), 1)
        self.assertTrue(any("Gabriel Sterling" in r.entity for r in name_risks))
        self.assertEqual(name_risks[0].severity, RiskSeverity.HIGH)

    def test_brand_tarnishment_seeded_script(self):
        """Script seeded with Rolex and Glock weapon malfunction / extortion."""
        script = (
            "SCENE 1 - EXT. ALLEY - NIGHT\n"
            "The masked assailant checks his Rolex Submariner. Exactly midnight.\n"
            "He draws his Glock 19 handgun, pointing it directly at the hostage.\n"
        )
        report = asyncio.run(self.service._generate_report(
            analysis_id="test_seed_brand",
            script_text=script,
            script_title="Midnight Alley"
        ))
        brand_risks = [r for r in report.risks if r.category.value == "BRAND"]
        self.assertGreaterEqual(len(brand_risks), 1)
        self.assertTrue(any("Glock" in r.entity or "Rolex" in r.entity for r in brand_risks))
        self.assertEqual(brand_risks[0].severity, RiskSeverity.MEDIUM)

    def test_title_collision_seeded_script(self):
        """Script titled 'The Apprentice's Revenge' colliding with 2024 theatrical title."""
        script = (
            "SCENE 1 - INT. OFFICE - DAY\n"
            "A corporate drama about young interns fighting for a promotion.\n"
        )
        report = asyncio.run(self.service._generate_report(
            analysis_id="test_seed_title",
            script_text=script,
            script_title="The Apprentice's Revenge"
        ))
        title_risks = [r for r in report.risks if r.category.value == "TITLE"]
        self.assertGreaterEqual(len(title_risks), 1)
        self.assertTrue(any("Apprentice" in r.entity for r in title_risks))
        self.assertEqual(title_risks[0].severity, RiskSeverity.HIGH)

    def test_nanpa_phone_seeded_script(self):
        """Script speaking non-cleared phone number 555-0250 (outside 0100-0199 range)."""
        script = (
            "SCENE 1 - INT. KITCHEN - DAY\n"
            "BOB\nCall me on my direct line, (415) 555-0250, before six.\n"
        )
        report = asyncio.run(self.service._generate_report(
            analysis_id="test_seed_phone",
            script_text=script,
            script_title="Direct Line"
        ))
        prop_risks = [r for r in report.risks if r.category.value == "PROP"]
        self.assertGreaterEqual(len(prop_risks), 1)
        self.assertTrue(any("555-0250" in r.entity for r in prop_risks))
        self.assertEqual(prop_risks[0].severity, RiskSeverity.HIGH)

    def test_aggregate_hit_rate(self):
        """Verifies 100% empirical hit rate (4/4 landmine categories caught)."""
        test_cases = [
            ("GABRIEL STERLING CEO dumps waste", "Biotech", "NAME"),
            ("He brandished the Glock 19 and checked his Rolex", "Alley", "BRAND"),
            ("General drama", "The Apprentice's Revenge", "TITLE"),
            ("Dial (415) 555-0250 right now", "Dial", "PROP"),
        ]
        hits = 0
        for text, title, expected_cat in test_cases:
            rep = asyncio.run(self.service._generate_report("test_hit", text, title))
            categories_caught = [r.category.value for r in rep.risks]
            if expected_cat in categories_caught:
                hits += 1

        hit_rate = (hits / len(test_cases)) * 100.0
        self.assertEqual(hit_rate, 100.0, f"Expected 100% hit rate, got {hit_rate}%")


if __name__ == "__main__":
    unittest.main()
