# 🎬 GREENLIGHT — Autonomous Pre-Production Clearance & E&O Risk Copilot

> Built for the **Google Cloud Blockbuster Hackathon: Agentic Cinema** (Parallel Track)  
> Powered by **Google Agent Development Kit (ADK)**, **Gemini 2.0/2.5 Flash**, and **Parallel Web Search MCP**.

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Partner: Parallel](https://img.shields.io/badge/Partner-Parallel%20MCP-06B6D4.svg)](https://docs.parallel.ai)
[![Platform: Google Cloud](https://img.shields.io/badge/Google%20Cloud-Gemini%20ADK-blue.svg)](https://github.com/google/adk-python)

---

## 💡 Executive Summary & The Problem Space

Before any commercial feature film, television pilot, or streaming series can secure **Errors & Omissions (E&O) insurance**—a mandatory legal prerequisite for theatrical release, financing drawdowns, and distributor delivery—production counsel must commission an exhaustive **Script Clearance Report**.

In traditional film financing:
- Manual clearance bureaus (e.g., Entertainment Clearances Inc., Marshall/Plumb, IndieClear) charge **\$1,500–\$4,000+** per screenplay (with comprehensive title searches adding \$600–\$1,200).
- Turnaround takes **5–10 business days** (or 3–5 days with steep rush fees).
- Once clearance is submitted, **insurance underwriting requires another 3–5+ business days** before policy binding.
- Any unresolved red flag (defamation of a living person, trademark disparagement, title collision) **halts production financing and freezes shooting dates**.

**GREENLIGHT** transforms this costly, multi-day bottleneck into a **source-cited, prioritized legal clearance dossier in minutes**.

---

## 🏛️ Architecture: Multi-Agent Pipeline

GREENLIGHT uses Google's code-first **Agent Development Kit (ADK)** to orchestrate a deterministic `SequentialAgent` wrapping a concurrent `ParallelAgent` fan-out, grounded in live web intelligence via **Parallel's hosted Model Context Protocol (MCP)** server (`search-mcp.parallel.ai/mcp`):

```
                                  ┌───────────────────────────────┐
                                  │      Screenplay Ingestion     │
                                  │   (PDF / Fountain / Text)     │
                                  └──────────────┬────────────────┘
                                                 │
                                                 ▼
                          ┌───────────────────────────────────────────────┐
                          │   1️⃣ Stage 1: SCRIPT PARSER AGENT (ADK)       │
                          │   Extracts Characters, Brands, Titles, Props  │
                          │   Output: session.state["parsed_script"]      │
                          └──────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
        ┌─────────────────────────────────────────────────────────────────────────────────┐
        │             2️⃣ Stage 2: PARALLEL CLEARANCE TEAM (ParallelAgent Fan-Out)          │
        │                                                                                 │
        │   ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────┐   │
        │   │  Character & Defamation │ │   Brand & Trademark     │ │ Title Collision │   │
        │   │     Clearance Agent     │ │    Clearance Agent      │ │ Clearance Agent │   │
        │   │ (session.state["names"])│ │(session.state["brands"])│ │(session["titles)│   │
        │   └────────────┬────────────┘ └────────────┬────────────┘ └────────┬────────┘   │
        └────────────────┼───────────────────────────┼───────────────────────┼────────────┘
                         │                           │                       │
                         └───────────────────────────┼───────────────────────┘
                                                     │ (web_search / web_fetch)
                                                     ▼
                                       ┌───────────────────────────┐
                                       │    PARALLEL SEARCH MCP    │
                                       │ search-mcp.parallel.ai/mcp│
                                       └─────────────┬─────────────┘
                                                     │
                                                     ▼
                          ┌───────────────────────────────────────────────┐
                          │   3️⃣ Stage 3: RISK SYNTHESIZER AGENT (ADK)    │
                          │   Deduplication, Greenlight Score (0-100),    │
                          │   and E&O Insurance Underwriting Memorandum   │
                          └──────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                          ┌───────────────────────────────────────────────┐
                          │     Cinematic Executive Clearance Suite       │
                          │     Interactive Dashboard + 1-Click Export    │
                          └───────────────────────────────────────────────┘
```

---

## 🎯 Scoring Criteria Alignment

| Judging Criterion | How GREENLIGHT Dominates |
| :--- | :--- |
| **Technological Implementation** | Not a wrapper or single-prompt chatbot. Uses real Google ADK multi-agent primitives (`SequentialAgent` + `ParallelAgent` concurrent fan-out) and actively calls the official **Parallel Search MCP** (`search-mcp.parallel.ai/mcp`) at runtime for live web grounding. |
| **Design** | A purpose-built, responsive Hollywood executive clearance dashboard: live Server-Sent Events (SSE) agent execution progress, color-coded severity cards (HIGH / MEDIUM / LOW), source-cited legal evidence, and one-click printable E&O underwriting memorandums. |
| **Potential Impact** | Solves a documented, high-dollar bottleneck in film production financing. Directly targets independent producers, line producers, and entertainment insurance underwriters with quantifiable savings (5–10 business days saved per draft). |
| **Quality of the Idea** | Highly original and non-obvious. Avoids the crowded "AI script generator / video generator" tropes by tackling the critical, unglamorous legal infrastructure required to actually make a movie. |

---

## 🚀 Quickstart & Local Development

### 1. Prerequisites
- Python 3.10+
- (Optional) `GOOGLE_GENAI_API_KEY` for live Gemini 2.0/2.5 Flash execution
- (Optional) `PARALLEL_API_KEY` to lift anonymous rate limits on the Parallel MCP

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/your-repo/GREENLIGHT.git
cd GREENLIGHT

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials (Optional for Demo Mode)
```bash
cp .env.example .env
# Edit .env with your keys if available:
# GOOGLE_GENAI_API_KEY="AIzaSy..."
# PARALLEL_API_KEY="par_live_..."
```

### 4. Run the Studio Server
```bash
python -m api.main
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

Click **"⚡ Load Landmine Demo Script"** and hit **"🎬 Run Multi-Agent Clearance Audit"** to see the full multi-agent pipeline in action!

---

## 🧪 Deliberate Clearance Landmines (Demo Script)

GREENLIGHT includes `docs/sample_scripts/landmine_script.txt` with realistic pre-production legal landmines:
1. **Title Collision**: Confusing overlap with the 2024 Cannes Competition theatrical release *"The Apprentice"* and registered MPAA titles.
2. **Defamation & California Right of Publicity (§ 3344)**: Living former Uber CEO portrayed running lethal, fraudulent bioweapons trials.
3. **Trademark Disparagement (Lanham Act § 43(c))**: Catastrophic autonomous failure and battery fire attributed to a registered commercial vehicle mark (*Tesla Cybertruck*).
4. **Privacy & Tort Liability**: Active residential address and non-555 active telephone number broadcast in dialogue.

---

## 📦 Cloud Run Deployment

GREENLIGHT is architected as a single, containerized service with zero CORS complexity:

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/greenlight
gcloud run deploy greenlight \
  --image gcr.io/YOUR_PROJECT_ID/greenlight \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 📄 Open Source License
This project is licensed under the [MIT License](LICENSE).
