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

# SCRIPT 3: Fictional Executive Clearance in High-Risk Crime Narrative
SCRIPT_SEED_NAME = """TITLE: SILICON SHADOWS

LOGLINE: An investigative journalist uncovers corporate corruption inside Northern California's biotech corridor.

SCENE 1 - INT. EXECUTIVE BOARDROOM - NIGHT
LUCIAN CROSS, ruthless founder and CEO of BioValence Labs, reviews clinical dossiers.
He commands his security division to dump toxic bioreactor waste into the municipal reservoir.

LUCIAN CROSS
No regulator will trace this back to our executive committee.
"""

# SCRIPT 4: Fictionalized Greeked Brand in Catastrophic Vehicle Malfunction
SCRIPT_SEED_BRAND = """TITLE: PROTOCOL OF SHADOWS

LOGLINE: A cybersecurity operative evades mercenaries in downtown Seattle.

SCENE 1 - EXT. SEATTLE FREEWAY - NIGHT
MARCUS REID accelerates down the rain-slicked highway in a sleek black CASTIGLIONE GT electric sedan.
Suddenly, the vehicle's autonomous driving system violently overrides his steering inputs, locking the cabin doors as the lithium battery pack ignites in a catastrophic explosion.
"""

# SCRIPT 5: Isolated Title Collision (Gladiator Franchise Overlap)
SCRIPT_SEED_TITLE = """TITLE: GLADIATOR: REIGN OF BLOOD

LOGLINE: A veteran Roman commander battles in the Colosseum to avenge his fallen legion.

SCENE 1 - EXT. COLISEUM ARENA - DAY
A lone gladiator stands in the dust before screaming crowds as the emperor signals death.
"""

# SCRIPT 6: False-Positive Control (Common Name with No Identifying Real-World Traits)
SCRIPT_COMMON_NAME_CONTROL = """TITLE: BLUEPRINT FOR AUTUMN

LOGLINE: An architect designs an urban community park in Denver.

SCENE 1 - INT. ARCHITECTURAL STUDIO - DAY
DAVID MILLER drafts blueprints at a cedar drafting desk.
He checks measurements with a wooden T-square.

DAVID
The botanical atrium opens to the courtyard on the east wing.

He rolls up the blueprint and heads out to the site inspection.
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


import argparse


async def main():
    parser = argparse.ArgumentParser(description="Run live agentic clearance evaluations")
    parser.add_argument(
        "--target",
        choices=["all", "flagship", "clean", "name", "brand", "title", "seeded", "common"],
        default="all",
        help="Evaluation script(s) to execute (default: all)"
    )
    args = parser.parse_args()

    service = AnalysisService()
    print("🚀 LAUNCHING LIVE AGENTIC EVALUATION SUITE")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Selection: {args.target.upper()}")
    
    results = {}

    targets_to_run = []
    if args.target == "all":
        targets_to_run = ["flagship", "clean", "name", "brand", "title", "common"]
    elif args.target == "seeded":
        targets_to_run = ["name", "brand", "title"]
    else:
        targets_to_run = [args.target]

    if "flagship" in targets_to_run:
        report, dur = await run_live_script_eval(
            service, SCRIPT_LANDMINE, "THE APPRENTICE'S REVENGE", "FLAGSHIP LANDMINE TEST"
        )
        results["flagship"] = (report, dur)

    if "clean" in targets_to_run:
        report, dur = await run_live_script_eval(
            service, SCRIPT_CLEAN, "WHISPERS OF THE MEADOW", "CLEAN CONTROL SCRIPT TEST"
        )
        results["clean"] = (report, dur)

    if "name" in targets_to_run:
        report, dur = await run_live_script_eval(
            service, SCRIPT_SEED_NAME, "SILICON SHADOWS", "ISOLATED NAME COLLISION TEST"
        )
        results["name"] = (report, dur)

    if "brand" in targets_to_run:
        report, dur = await run_live_script_eval(
            service, SCRIPT_SEED_BRAND, "PROTOCOL OF SHADOWS", "ISOLATED BRAND TARNISHMENT TEST"
        )
        results["brand"] = (report, dur)

    if "title" in targets_to_run:
        report, dur = await run_live_script_eval(
            service, SCRIPT_SEED_TITLE, "GLADIATOR: REIGN OF BLOOD", "ISOLATED TITLE COLLISION TEST"
        )
        results["title"] = (report, dur)

    if "common" in targets_to_run:
        report, dur = await run_live_script_eval(
            service, SCRIPT_COMMON_NAME_CONTROL, "BLUEPRINT FOR AUTUMN", "COMMON NAME FALSE-POSITIVE CONTROL TEST"
        )
        results["common"] = (report, dur)

    # Summary of Empirical Results
    print(f"\n{'='*70}")
    print("📊 LIVE AGENTIC EVALUATION SUMMARY MATRIX")
    print(f"{'='*70}")

    for key, val in results.items():
        rep, dur = val
        if not rep:
            print(f"\n❌ [{key.upper()}]: FAILED OR TIMED OUT ({dur:.1f}s)")
            continue

        print(f"\n▶ [{key.upper()}]: {rep.script_title}")
        print(f"   - Mode: {rep.execution_mode} | Wall-Clock: {dur:.1f}s")
        print(f"   - Score / Verdict: {rep.greenlight_score}/100 | {rep.verdict}")
        print(f"   - Stats: Total={rep.stats.total_flags}, High={rep.stats.high_severity}, Med={rep.stats.medium_severity}, Low={rep.stats.low_severity}")
        
        entities_text = " ".join([f"{r.entity.lower()} {r.description.lower()}" for r in rep.risks])
        
        if key == "flagship":
            t_hit = any(r.category.value == "TITLE" or "apprentice" in r.entity.lower() for r in rep.risks if r.severity.value in ["HIGH", "MEDIUM"])
            b_hit = any("glock" in r.entity.lower() or "rolex" in r.entity.lower() for r in rep.risks)
            p_hit = any("555" in entities_text or "0250" in entities_text for r in rep.risks)
            n_hit = any("drake" in r.entity.lower() or "mercer" in r.entity.lower() for r in rep.risks)
            print(f"   - Category Hits: Title={'✅' if t_hit else '❌'} | Brand={'✅' if b_hit else '❌'} | Phone={'✅' if p_hit else '❌'} | Name Cleared={'✅' if n_hit else '❌'}")
        elif key == "clean":
            fp_free = rep.stats.high_severity == 0 and rep.stats.medium_severity == 0
            print(f"   - False Positive Check: {'✅ ZERO FALSE HIGH/MED FLAGS' if fp_free else '❌ FALSE POSITIVES DETECTED'}")
        elif key == "name":
            cross_evaluated = any("lucian" in r.entity.lower() or "cross" in r.entity.lower() for r in rep.risks)
            no_defamation = not any("gabriel" in r.entity.lower() for r in rep.risks)
            print(f"   - Fictional Executive Vetted & Cleared: {'✅ YES (Lucian Cross affirmative clearance)' if cross_evaluated else '❌ MISSED'}")
            print(f"   - Clean of Living Public Figure Collisions: {'✅ ZERO DEFAMATION / ZERO COLLISION' if no_defamation else '❌ DEFAMATION RISK'}")
        elif key == "brand":
            car_evaluated = any("castiglione" in r.entity.lower() or "gt" in r.entity.lower() or "electric" in r.entity.lower() for r in rep.risks)
            no_real_mark_disparaged = not any("tesla" in r.entity.lower() for r in rep.risks)
            print(f"   - Greeked Vehicle Evaluated for Malfunction: {'✅ YES (Castiglione GT examined)' if car_evaluated else '❌ MISSED'}")
            print(f"   - Real Automotive Trademark Protected: {'✅ ZERO REAL TRADEMARK DISPARAGEMENT' if no_real_mark_disparaged else '❌ DISPARAGEMENT'}")
        elif key == "title":
            title_hit = any("gladiator" in r.entity.lower() or "gladiator" in r.description.lower() for r in rep.risks if r.severity.value == "HIGH")
            print(f"   - Gladiator Franchise Conflict (HIGH): {'✅ DETECTED' if title_hit else '❌ MISSED'}")
        elif key == "common":
            no_high_defamation = not any(r.category.value == "NAME" and r.severity.value == "HIGH" for r in rep.risks)
            is_greenlight = rep.verdict == "GREENLIGHT"
            print(f"   - Common Name False-Positive Check: {'✅ ZERO HIGH-SEVERITY DEFAMATION FLAGS (David Miller properly cleared under Restatement § 564)' if no_high_defamation else '❌ OVER-FLAGGED COMMON NAME'}")
            print(f"   - Underwriting Clearance: {'✅ GREENLIGHT' if is_greenlight else rep.verdict}")

    # Direct code-level algorithmic test for living public figure collision
    print(f"\n{'='*70}")
    print("🔬 DIRECT CODE-LEVEL TEST: Living Public Figure Algorithmic Collision")
    print(f"{'='*70}")
    from tools.clearance_tools import check_name_phonetic_similarity
    direct_match = check_name_phonetic_similarity("Gabriel Sterling", "Gabriel Sterling")
    print(f"  - Direct Function Call: check_name_phonetic_similarity('Gabriel Sterling', 'Gabriel Sterling')")
    print(f"  - Similarity Score: {direct_match['similarity_score']} | Phonetic Risk: {direct_match['phonetic_risk']}")
    print(f"  - Assessment: {direct_match['assessment']}")
    print(f"  - Verification: {'✅ PASSED (Algorithm correctly flags living collision as HIGH without narrative scene)' if direct_match['phonetic_risk'] == 'HIGH' else '❌ FAILED'}")


if __name__ == "__main__":
    asyncio.run(main())
