# GREENLIGHT — Official Devpost Submission Package
**Google Cloud Blockbuster Hackathon: Agentic Cinema (Parallel Track)**

---

## 1. Submission Metadata
- **Project Title:** GREENLIGHT: Autonomous Pre-Production Script Clearance & E&O Risk Copilot
- **Tagline:** Autonomous multi-agent legal clearance for screenplays — cross-referencing trademark dilution, character defamation, and title exclusivity against live web registries in seconds.
- **Track:** Parallel Track (Agentic Cinema)
- **GitHub Repository:** https://github.com/ABHIGH15/GREENLIGHT
- **Cover Image / Thumbnail:** `docs/greenlight_devpost_thumbnail.jpg` (Saved in repo)

---

## 2. Devpost Form Markdown (Copy & Paste Directly into Devpost)

### 💡 Inspiration
Before any commercial film, television pilot, or streaming series can secure financing or begin principal photography, production counsel must secure **Errors & Omissions (E&O) insurance**. 

Securing this policy requires an exhaustive line-by-line legal clearance audit of the screenplay. Traditionally, manual legal clearance bureaus take **5 to 10 business days** of manual vetting, costing thousands of dollars per draft. A single missed landmine—a living person defamation hazard, trademark tarnishment under Lanham Act § 43(c), an unreserved dialogue phone number, or a title collision—can halt financing drawdowns, trigger costly litigation, or prompt a distribution injunction.

We built **GREENLIGHT** to transform this multi-day pre-production bottleneck into an autonomous, source-grounded, and auditable clearance dossier in under 75 seconds.

---

### ⚙️ What It Does
GREENLIGHT is an autonomous legal clearance copilot that ingests standard screenplay drafts (PDF, Fountain, TXT) and executes an end-to-end multi-agent clearance cross-examination:

1. **Screenplay Entity Ingestion**: Google ADK's `ScriptParserAgent` extracts all characters, commercial brands, weapons, vehicles, referenced titles, and dialogue phone numbers.
2. **Concurrent Multi-Agent Fan-Out**: Dispatches 3 specialist clearance agents simultaneously using Google ADK's `ParallelAgent`:
   - **TitleClearanceAgent**: Cross-examines working titles against MPAA Title Registration Bureau standards, recent theatrical releases (e.g. *The Apprentice* 2024 collision), and common-law marks via Parallel Search MCP.
   - **BrandClearanceAgent**: Audits trademarks under Lanham Act § 43(c) (dilution by tarnishment in crime/violence scenes) and Lanham Act § 43(a) (false endorsement), recommending vetted fictional prop replacements ("Greeking") and vetting phone numbers against FCC/NANPA safe entertainment blocks (555-0100 to 555-0199).
   - **NameClearanceAgent**: Screens character names against living executives, public officials, and criminal registries under the Restatement (Second) of Torts, avoiding false-positive over-flagging on common names.
3. **Live Web Intelligence Grounding**: Every specialist queries live public registries (Justia Trademarks, Wikipedia, NANPA, news archives) via **Parallel's hosted Model Context Protocol (MCP)** server (`search-mcp.parallel.ai/mcp`).
4. **Deterministic Auditable Scoring**: The `RiskSynthesizerAgent` calculates a transparent Greenlight Index score via a deterministic formula ($100 - 25\text{H} - 10\text{M} - 3\text{L}$), completely free from LLM scoring hallucinations.
5. **Executive E&O Underwriting Dossier**: Renders a tactile 35mm Hollywood Studio Terminal report with live camera telemetry, physical rubber stamp verdicts, and one-click PDF memo export.

---

### 🛠️ How We Built It
- **Google Agent Development Kit (ADK)**: Structured as a hierarchical pipeline combining a top-level `SequentialAgent` orchestrator with an inner `ParallelAgent` concurrent fan-out team.
- **Gemini 3.5 Flash Lite**: Powers high-speed multi-agent reasoning, entity parsing, and legal synthesis.
- **Adaptive Request Pacemaker**: A custom non-blocking rate limiter with an exponential backoff pacing mechanism, ensuring reliable agent orchestration under quota constraints.
- **Parallel Search MCP**: Grounding every clearance claim in verifiable live web sources using Parallel's hosted MCP interface (`https://search-mcp.parallel.ai/mcp`).
- **FastAPI & Server-Sent Events (SSE)**: Streams real-time agent lifecycle events, teleprinter logs, and live stopwatch telemetry to the browser.
- **Bespoke Archival Studio UI**: Designed to break out of generic "AI dark dashboard" cliches. Features an authentic tactile screenplay manuscript page with metallic brass brad fasteners, Hollywood draft revision selectors (Pink, Blue, Goldenrod), rubber stamp clearance marks, and a continuous call-sheet data strip.

---

### 🧗 Challenges We Ran Into
- **Parallel API Parameter Schema**: The hosted Parallel Search MCP expects a strict schema (`objective`, `search_queries`, `mode`). Passing unsupported parameters caused `422 Unprocessable Entity` responses. We solved this by creating a robust Python-level MCP adapter that strips unsupported parameters and slices results locally.
- **False-Positive Common Name Control**: Initial LLM prompts risked over-flagging common fictional names (e.g. *David Miller*, an ordinary architect in Denver). We implemented strict Restatement (Second) of Torts jurisdictional filtering and verified it with an automated test suite achieving **97/100 GREENLIGHT** with zero false flags.
- **Deterministic Math Consistency**: We enforced a strict post-processing formula ($100 - 25\text{H} - 10\text{M} - 3\text{L}$) directly in Pydantic models to guarantee that underwriting scores are 100% mathematically verifiable by human auditors.

---

### 🏆 Accomplishments That We're Proud Of
- **Sub-Minute Clearance Turnaround**: Reduced a 5 to 10 business day manual legal process into a **48 to 75-second** autonomous multi-agent clearance scan.
- **100% Primary Source Grounding**: Every single flagged risk cites authoritative sources (USPTO filings, Justia, Wikipedia, NANPA FCC standards).
- **False-Positive Precision**: Successfully tested against both extreme landmine screenplays (*The Apprentice's Revenge*, Score: 0/100 RED FLAG) and common-name control scripts (*Blueprint for Autumn*, Score: 97/100 GREENLIGHT).
- **Comprehensive Automated Test Suite**: 24/24 unit tests passing across pipeline architecture, rate limiting, and legal tool logic.

---

### 📚 What We Learned
- How to effectively compose `SequentialAgent` and `ParallelAgent` within the Google ADK Python framework.
- The power of Model Context Protocol (MCP) in grounding multi-agent LLM teams in live, external real-world databases.
- The nuance of entertainment legal clearance doctrines (nominative fair use vs. trademark tarnishment, Rogers v. Grimaldi artistic relevance, and FCC entertainment phone numbering blocks).

---

### 🚀 What's Next for GREENLIGHT
- **Direct Screenwriting Software Plugins**: Native extensions for Final Draft (.fdx), Celtx, and WriterDuet to provide real-time clearance highlighting as writers type dialogue.
- **Direct Underwriter API Integration**: Instant programmatic submission to entertainment insurance underwriting portals (e.g., Chubb, Hiscox, Front Row Insurance) for automated conditional binder generation.
- **Script Revision Delta Auditing**: Autonomous comparison between draft revisions (e.g., White Draft to Blue Revision) that only re-audits modified scenes to save API tokens and compute.

---

### 🏷️ Built With
`google-adk`, `gemini-3.5-flash-lite`, `parallel-search-mcp`, `python`, `fastapi`, `pydantic`, `html5`, `css3`, `javascript`, `uvicorn`
