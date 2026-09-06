"""
Live Agentic Evaluation Script for GREENLIGHT
Executes end-to-end multi-agent clearance via Google ADK Runner, Gemini 3.5 Flash Lite,
and Parallel Search MCP against live models and live web intelligence.
"""

import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

key = (
    os.environ.get("GOOGLE_GENAI_API_KEY", "").strip() or 
    os.environ.get("GOOGLE_API_KEY", "").strip() or 
    os.environ.get("GEMINI_API_KEY", "").strip()
)
if not key or key.startswith("your_"):
    print("ERROR: Valid GOOGLE_GENAI_API_KEY is required to run live evaluation.")
    sys.exit(1)

os.environ["GOOGLE_API_KEY"] = key
os.environ["GEMINI_API_KEY"] = key
os.environ["GOOGLE_GENAI_API_KEY"] = key
os.environ["GEMINI_MODEL"] = "gemini-3.5-flash-lite"
os.environ["GEMINI_REQUEST_PACING"] = "4.2"

from services.analysis_service import AnalysisService


# SCRIPT 1: Clearance Landmine Script
SCRIPT_LANDMINE = """TITLE: THE APPRENTICE'S REVENGE

LOGLINE: A disgraced biotech executive plots revenge against former corporate partners.

SCENE 1 - EXT. MISSION BAY - DAY
JULIAN DRAKE steps out of a vehicle, adjusting his Rolex Submariner.
He pulls a Glock 19 handgun from his bespoke coat.

SCENE 2 - INT. BIOTECH LAB - CONTINUOUS
DR. VALEN MERCER is pipetting glowing blue peptides into vials.

VALEN
Call my private line at (415) 555-0250 if you want to negotiate.

Julian raises the Glock 19.
FADE TO BLACK.
"""

# SCRIPT 2: Clean Control Script (Fictionalized, no real brands or living persons)
SCRIPT_CLEAN = """TITLE: WHISPERS OF THE MEADOW

LOGLINE: An astronomer seeks solitude in the Pacific Northwest mountains.

SCENE 1 - EXT. MEADOW - DAWN
A gentle morning breeze stirs the high mountain grass.
ELENA THORNE, an observational astronomer in her 40s, adjusts a brass optical telescope.

SCENE 2 - INT. CABIN - NIGHT
Elena pours hot herbal tea from a ceramic kettle into a mug.
She studies handwritten stellar coordinate charts beneath a kerosene lamp.

ELENA
(whispering to herself)
The constellation has shifted.
"""


async def run_live_script_eval(service: AnalysisService, script_text: str, title: str, label: str):
    print(f"\n{'='*70}")
    print(f"🎬 EVALUATING [{label}]: '{title}'")
    print(f"{'='*70}")
    
    start_time = time.time()
    analysis_id = await service.start_analysis(script_text, title)
    print(f"Analysis Job ID: {analysis_id}")
    print(f"Pacing: 4.2s interval | Model: {os.environ.get('GEMINI_MODEL')}")
    print("Streaming live agent execution status...")
    
    last_msg = ""
    while True:
        await asyncio.sleep(3)
        events = service.status_events.get(analysis_id, [])
        if events:
            latest = events[-1]
            msg = latest.get("message", "")
            if msg != last_msg:
                elapsed = time.time() - start_time
                print(f"  [{elapsed:.1f}s] [{latest.get('stage')}]: {msg}")
                last_msg = msg
        
        report = service.get_report(analysis_id)
        if report:
            total_duration = time.time() - start_time
            print(f"\n✅ COMPLETED in {total_duration:.1f}s!")
            print(f"Execution Mode: {report.execution_mode}")
            print(f"Greenlight Score: {report.greenlight_score}/100")
            print(f"Underwriting Verdict: {report.verdict}")
            print(f"Stats: Total Flags={report.stats.total_flags}, High={report.stats.high_severity}, Med={report.stats.medium_severity}, Low={report.stats.low_severity}")
            print(f"\nDetailed Risks Identified ({len(report.risks)} items):")
            for idx, r in enumerate(report.risks, 1):
                print(f"  {idx}. [{r.severity}] [{r.category}] {r.entity}")
                print(f"     Issue: {r.description[:120]}...")
                if r.sources:
                    print(f"     Source: {r.sources[0].title} ({r.sources[0].url})")
            return report, total_duration
        
        if time.time() - start_time > 300:
            print("❌ TIMEOUT: Pipeline did not complete within 300 seconds.")
            return None, 300


async def main():
    service = AnalysisService()
    print("🚀 LAUNCHING LIVE AGENTIC EVALUATION SUITE")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Run Flagship Landmine Script
    report_landmine, dur_landmine = await run_live_script_eval(
        service, SCRIPT_LANDMINE, "THE APPRENTICE'S REVENGE", "FLAGSHIP LANDMINE TEST"
    )
    
    # 2. Run Clean Control Script
    report_clean, dur_clean = await run_live_script_eval(
        service, SCRIPT_CLEAN, "WHISPERS OF THE MEADOW", "CLEAN CONTROL SCRIPT TEST"
    )
    
    # Summary of Empirical Results
    print(f"\n{'='*70}")
    print("📊 LIVE AGENTIC EVALUATION SUMMARY")
    print(f"{'='*70}")
    
    if report_landmine:
        print(f"\n1. FLAGSHIP LANDMINE SCRIPT:")
        print(f"   - Execution Mode: {report_landmine.execution_mode}")
        print(f"   - Wall-Clock Time: {dur_landmine:.1f}s")
        print(f"   - Score / Verdict: {report_landmine.greenlight_score}/100 | {report_landmine.verdict}")
        
        # Check specific category detections
        categories = {r.category.value: r for r in report_landmine.risks}
        entities_text = " ".join([r.entity.lower() for r in report_landmine.risks])
        
        title_caught = "TITLE" in categories or "apprentice" in entities_text
        brand_caught = "BRAND" in categories or "glock" in entities_text or "rolex" in entities_text
        phone_caught = "PROP" in categories or "555" in entities_text or "0250" in entities_text
        name_addressed = "NAME" in categories or "mercer" in entities_text or "drake" in entities_text
        
        print(f"   - Title Collision Detected: {'✅ YES' if title_caught else '❌ NO'}")
        print(f"   - Brand / Weapon Tarnishment Detected: {'✅ YES' if brand_caught else '❌ NO'}")
        print(f"   - Unauthorized Phone Number Flagged: {'✅ YES' if phone_caught else '❌ NO'}")
        print(f"   - Character Clearance Evaluated: {'✅ YES' if name_addressed else '❌ NO'}")
        print(f"   - Live Sources Cited: {sum(len(r.sources) for r in report_landmine.risks)} citations")

    if report_clean:
        print(f"\n2. CLEAN CONTROL SCRIPT:")
        print(f"   - Execution Mode: {report_clean.execution_mode}")
        print(f"   - Wall-Clock Time: {dur_clean:.1f}s")
        print(f"   - Score / Verdict: {report_clean.greenlight_score}/100 | {report_clean.verdict}")
        print(f"   - Total Flags: {len(report_clean.risks)}")
        clean_pass = report_clean.verdict == "GREENLIGHT" and report_clean.greenlight_score >= 85
        print(f"   - Zero False High-Severity Flags: {'✅ YES' if report_clean.stats.high_severity == 0 else '❌ NO'}")
        print(f"   - Clean Underwriting Verdict: {'✅ YES' if clean_pass else '❌ NO'}")


if __name__ == "__main__":
    asyncio.run(main())
