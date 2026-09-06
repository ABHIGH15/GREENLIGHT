# 🎬 GREENLIGHT — Autonomous Pre-Production Clearance & E&O Risk Copilot

> Built for the **Google Cloud Blockbuster Hackathon: Agentic Cinema** (Parallel Track)  
> Powered by **Google Agent Development Kit (ADK)**, **Gemini 3.5 Flash Lite**, and **Parallel Web Search MCP**.

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Partner: Parallel](https://img.shields.io/badge/Partner-Parallel%20MCP-06B6D4.svg)](https://docs.parallel.ai)
[![Platform: Google Cloud](https://img.shields.io/badge/Google%20Cloud-Gemini%20ADK-blue.svg)](https://github.com/google/adk-python)

---

## 💡 Executive Summary & The Problem Space

Before any commercial feature film, television pilot, or streaming series can secure **Errors & Omissions (E&O) insurance**—a mandatory legal prerequisite for theatrical release, financing drawdowns, and distributor delivery—production counsel must commission an exhaustive **Script Clearance Report**.

In traditional film financing:
- Manual clearance bureaus (e.g., Entertainment Clearances Inc., Marshall/Plumb, IndieClear) require specialized legal retainers and labor-intensive line-by-line vetting.
- Turnaround takes **5–10 business days** (or 3–5 days with steep rush fees).
- Once clearance is submitted, **insurance underwriting requires another 3–5+ business days** before policy binding.
- Any unresolved red flag (defamation of a living person, trademark disparagement, title collision) **halts production financing and freezes shooting dates**.

**GREENLIGHT** transforms this multi-day bottleneck into a **source-cited, prioritized legal clearance dossier in minutes**.

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
- (Optional) `GOOGLE_GENAI_API_KEY` for live Gemini 3.5 Flash Lite multi-agent execution (high-capacity free tier: 1,500 RPD, 15 RPM)
- (Optional) `PARALLEL_API_KEY` to unlock dedicated throughput on the Parallel Search MCP

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
# GEMINI_MODEL="gemini-3.5-flash-lite"
```

### 4. Run the Studio Server
```bash
python -m api.main
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

Click **"⚡ Load Landmine Demo Script"** and hit **"🎬 Run Multi-Agent Clearance Audit"** to see the full multi-agent pipeline in action!

---

## 🧪 Empirical Live Evaluation & Benchmark Matrix

GREENLIGHT separates testing into two distinct, verifiable layers:
1. **Local Regression Suite (`tests/`):** 23 automated tests running in **0.33s** verifying local deterministic algorithms (Soundex phonetic screening, direct living figure collision detection, MPAA title fuzzy matching, Greeking catalog lookup, NANPA 555 reservation blocks, input validation, and PDF parsing).
2. **Live Agentic Evaluation Benchmark (`scripts/evaluate_live_agents.py`):** Full end-to-end multi-agent execution invoking the live Google ADK `Runner.run_async()` against `gemini-3.5-flash-lite` and Parallel Search MCP across 5 test screenplays.

### 5-Script Live Benchmark Results:

| Benchmark Script | Test Category / Focus | Live Wall-Clock | Target Clearance Evaluation | Live Detection Status | Final Score & Formula | Underwriting Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **The Apprentice's Revenge** | Full Pipeline (4 Categories) | 66.2s | Title (*The Apprentice*), Glock 19, (415) 555-0250 phone, Rolex | ✅ **4/4 Landmines Caught** + Julian Drake cleared | **12/100** ($100 - 3{\times}25 - 1{\times}10 - 1{\times}3$) | `RED FLAG - ACTION REQUIRED` |
| **Whispers of the Meadow** | Clean Control Script | 60.0s | Unbranded rustic set, fictional astronomer | ✅ **0 False Positives** (0 High, 0 Med) | **88/100** ($100 - 4{\times}3$) | `GREENLIGHT` |
| **Silicon Shadows** | Fictional Character Clearance | 54.0s | Fictional CEO Lucian Cross in toxic dumping | ✅ **Affirmatively Cleared (LOW)** + Direct living figure test passes (HIGH) | **91/100** ($100 - 3{\times}3$) | `GREENLIGHT` |
| **Protocol of Shadows** | Greeked Brand Malfunction | 69.0s | Fictional Castiglione GT battery explosion | ✅ **Zero Real Trademarks Disparaged** (Greeking defense evaluated) | **62/100** ($100 - 1{\times}25 - 1{\times}10 - 1{\times}3$) | `CONDITIONAL GREENLIGHT` |
| **Gladiator: Reign of Blood** | Isolated Title Collision | 42.0s | Franchise collision with *Gladiator* (2000/2024) | ✅ **Caught (HIGH)** (Lanham Act § 43(a) / TRB) | **72/100** ($100 - 1{\times}25 - 1{\times}3$) | `CONDITIONAL GREENLIGHT` |

### Deterministic Underwriting Scoring Rubric:
$$\text{Score} = \max\Big(0, \min\big(100, 100 - (25 \times \text{High}) - (10 \times \text{Med}) - (3 \times \text{Low})\big)\Big)$$
- **Score $\ge 85$**: `GREENLIGHT` (Standard E&O underwriting bound)
- **Score $60 - 84$**: `CONDITIONAL GREENLIGHT` (Clearance rider required)
- **Score $< 60$**: `RED FLAG - ACTION REQUIRED` (Policy binding withheld pending script remediation)

---

## 📦 Cloud Run Deployment

GREENLIGHT is containerized with a production `Dockerfile` and configured for Google Cloud Run:

```bash
# Build container image via Google Cloud Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/greenlight

# Deploy to Cloud Run with Gemini 3.5 Flash Lite environment configuration
gcloud run deploy greenlight \
  --image gcr.io/YOUR_PROJECT_ID/greenlight \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_MODEL=gemini-3.5-flash-lite,GEMINI_REQUEST_PACING=4.2
```

---

## 📄 Open Source License
This project is licensed under the [MIT License](LICENSE).
