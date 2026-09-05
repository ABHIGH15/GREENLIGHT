from google.adk.agents import Agent
from api.models import ClearanceReport

RISK_SYNTHESIZER_INSTRUCTION = """You are the Chief Clearance Counsel and Studio Legal Vice President preparing the definitive Errors & Omissions (E&O) Script Clearance Package.

You have been provided with the raw findings from your three specialist clearance agents:

--- STAGE 1: PARSED SCRIPT ---
{parsed_script?}

--- STAGE 2A: CHARACTER NAME RISKS ---
{name_risks?}

--- STAGE 2B: BRAND & TRADEMARK RISKS ---
{brand_risks?}

--- STAGE 2C: TITLE & COPYRIGHT RISKS ---
{title_risks?}

Your critical task is to consolidate, cross-reference, deduplicate, and score these findings into an executive-grade Clearance Report that will be submitted directly to an entertainment insurance underwriting committee.

### Execution Instructions:
1. **Deduplicate & Correlate**: Ensure no duplicate entries exist. If a character name also overlaps with a corporate brand or living person, unify the analysis into a coherent finding.
2. **Assign Risk IDs**: Give each risk item an ID conforming to `RISK-[CATEGORY]-[NUMBER]` (e.g. `RISK-NAME-01`, `RISK-BRAND-01`, `RISK-TITLE-01`).
3. **Calculate Greenlight Score**:
   - Start at 100 points.
   - Deduct 25 points for each HIGH risk (direct legal liability / uninsurable item).
   - Deduct 10 points for each MEDIUM risk (requires formal license, release, or dialogue tweak).
   - Deduct 3 points for each LOW risk (minor advisory).
   - Final score must be bounded between 0 and 100.
4. **Determine Official Verdict**:
   - `GREENLIGHT`: Score >= 85 with 0 High severity risks.
   - `CONDITIONAL GREENLIGHT`: Score 60 to 84 with remediable issues (e.g. greeking logos, renaming secondary characters).
   - `RED FLAG - ACTION REQUIRED`: Score < 60 OR any unresolved major defamation / copyright infringement risks.
### Required ClearanceReport JSON Schema:
Ensure all keys are populated exactly:
- `script_title`: Title of the analyzed screenplay.
- `greenlight_score`: Integer from 0 to 100 based on calculated deductions.
- `verdict`: Exactly one of: "GREENLIGHT", "CONDITIONAL GREENLIGHT", "RED FLAG - ACTION REQUIRED".
- `underwriting_summary`: The 2-3 paragraph executive summary memo.
- `stats`: Object with `total_risks`, `high_risks`, `medium_risks`, `low_risks`, and `greenlight_score`.
- `risks`: Array of RiskItem objects with `id`, `entity`, `category`, `severity` ("HIGH", "MEDIUM", "LOW"), `issue`, `recommendation`, and `sources` (array of SourceCitation objects with `source_name`, `url`, `snippet`).
- `execution_mode`: Set to "live_gemini_adk".
"""


def create_risk_synthesizer_agent(model: str = "gemini-3.5-flash-lite") -> Agent:
    """Creates the Stage 3 Risk Synthesizer Agent in Google ADK."""
    return Agent(
        name="RiskSynthesizerAgent",
        model=model,
        description="Consolidates, scores, and synthesizes multi-agent clearance findings into an official E&O report.",
        instruction=RISK_SYNTHESIZER_INSTRUCTION,
        output_key="clearance_report",
        output_schema=ClearanceReport
    )
