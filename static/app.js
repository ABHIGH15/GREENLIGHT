let currentAnalysisId = null;
let currentReportData = null;
let activeCategoryFilter = "ALL";
let selectedFile = null;
let auditStartTime = null;
let timerInterval = null;
let currentPresetKey = "flagship";

const PRESET_SCRIPTS = {
  flagship: {
    id: "btnPresetFlagship",
    name: "The Apprentice's Revenge",
    badge: "⚡ Flagship Landmine Demo",
    note: "4 Clearance Landmines: Title collision, Glock 19 gun violence, Rolex watch, and unauthorized (415) 555-0250 phone number",
    text: `TITLE: THE APPRENTICE'S REVENGE

WRITTEN BY: ANONYMOUS PRODUCER

LOGLINE: A disgraced Silicon Valley biotech executive launches a covert corporate sabotage campaign against former partners, using autonomous drone swarms to blackmail Fortune 500 board members in San Francisco.

========================================================================

SCENE 1 - EXT. MISSION BAY TECH DISTRICT - DAY

A gleaming glass-and-steel skyscraper rises over the San Francisco waterfront. A bold neon emblem reads: "NEXODYNE GENOMICS - GLOBAL RESEARCH CENTER".

A sleek matte-black luxury electric sports sedan pulls aggressively into the VIP drop-off lane. The vehicle's autonomous guidance system violently GLITCHES, accelerating unexpectedly into the revolving glass doors. 

Glass SHATTERS across the granite courtyard. Commuters SCREAM.

The driver side door swings open. Out steps JULIAN DRAKE (40s), bespoke charcoal suit, Rolex Submariner on his wrist, knuckles grazed with blood.

JULIAN
(muttering to his smartwatch)
Tell me the autonomous guidance column didn't override again. That's two sensor failures this month. If our firmware leaks to the press, our NASDAQ valuation evaporates before Monday.

SCENE 2 - INT. BIOMEDICAL LAB - CONTINUOUS

Julian kicks open the reinforced security doors. He storms past rows of stainless steel bioreactor pods.

At the central terminal stands DR. VALEN MERCER (50s), chief scientific founder turned rogue biotech executive. He is feverishly pipetting glowing blue synthetic peptides into refrigerated cryogenic vials.

JULIAN
Valen! The patent assignment papers were supposed to be filed with the USPTO yesterday.

VALEN
The FDA sent a preliminary inspection notice this morning, Julian. The Phase II trial cohort in Zurich developed acute toxicity. 

JULIAN
Then pull the clinical dossiers and seal the archives! If the underwriters at Chubb or Lloyd's get a look at those adverse reaction tables, our Series B bridge loan is dead in the water.

Valen grabs a bottle of PERRIER SPARKLING WATER from the lab bench, takes a slow drink, and places the bottle beside an autoclave.

VALEN
You think this is about financing? If you want to renegotiate the IP split, call my direct private line at (415) 555-0250. Or come by my private research retreat at 404 Skyline Crest Way, Suite 800. But don't threaten me in my own laboratory.

JULIAN
(pulling a GLOCK 19 pistol from his jacket)
You won't leave this cleanroom alive without those cryptographic master keys, Valen.

VALEN
(smirks, tapping his chest)
Go ahead. My telemetry monitor is tethered to a private cloud instance. The moment my vitals flatline, the raw trial data automatically broadcasts to the SEC, the Wall Street Journal, and federal investigators.

JULIAN
You bluffing bastard.

Julian raises the weapon.

FADE TO BLACK.`
  },
  common: {
    id: "btnPresetCommon",
    name: "Blueprint for Autumn",
    badge: "👤 Common Name Control",
    note: "False-Positive Control: David Miller (Generic architect in Denver — verifies pipeline avoids indiscriminate name flagging, Score: 97/100)",
    text: `TITLE: BLUEPRINT FOR AUTUMN

LOGLINE: An architect designs an urban community park in Denver.

SCENE 1 - INT. ARCHITECTURAL STUDIO - DAY
DAVID MILLER drafts blueprints at a cedar drafting desk.
He checks measurements with a wooden T-square.

DAVID
The botanical atrium opens to the courtyard on the east wing.

He rolls up the blueprint and heads out to the site inspection.`
  },
  clean: {
    id: "btnPresetClean",
    name: "Whispers of the Meadow",
    badge: "🌿 Clean Control Script",
    note: "Clean Benchmark: Elena Thorne (Fictional rustic astronomer — verifies 95+ Greenlight score and 0 clearance flags)",
    text: `TITLE: WHISPERS OF THE MEADOW

LOGLINE: An astronomer seeks solitude in the Pacific Northwest mountains.

SCENE 1 - EXT. MEADOW - DAWN
A gentle morning breeze stirs the high mountain grass.
ELENA THORNE, an observational astronomer in her 40s, adjusts a brass optical telescope.

SCENE 2 - INT. CABIN - NIGHT
Elena pours hot herbal tea from a ceramic kettle into a mug.
She studies handwritten stellar coordinate charts beneath a kerosene lamp.

ELENA
(whispering to herself)
The constellation has shifted.`
  }
};

function selectPreset(key) {
  const preset = PRESET_SCRIPTS[key];
  if (!preset) return;
  currentPresetKey = key;

  document.querySelectorAll(".preset-pill").forEach(btn => btn.classList.remove("active"));
  const activeBtn = document.getElementById(preset.id);
  if (activeBtn) activeBtn.classList.add("active");

  const scriptInput = document.getElementById("scriptInput");
  if (scriptInput) scriptInput.value = preset.text;
  selectedFile = null;

  const dropZone = document.getElementById("dropZone");
  if (dropZone) {
    const icon = dropZone.querySelector(".upload-icon");
    const titleDiv = dropZone.querySelector(".drop-primary-text") || dropZone.querySelector("div:nth-child(2)");
    const subDiv = dropZone.querySelector(".drop-sub-text") || dropZone.querySelector("div:nth-child(3)");
    if (icon) icon.textContent = key === "flagship" ? "⚡" : (key === "common" ? "👤" : "🌿");
    if (titleDiv) titleDiv.textContent = `${preset.badge}: "${preset.name}"`;
    if (subDiv) subDiv.textContent = preset.note;
  }
}


function startLiveTimer() {
  auditStartTime = Date.now();
  const timerElem = document.getElementById("liveTimer");
  if (timerInterval) clearInterval(timerInterval);
  if (timerElem) timerElem.textContent = "0.0s";
  timerInterval = setInterval(() => {
    if (timerElem && auditStartTime) {
      const elapsed = ((Date.now() - auditStartTime) / 1000).toFixed(1);
      timerElem.textContent = `${elapsed}s`;
    }
  }, 100);
}

function stopLiveTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  if (auditStartTime) {
    return ((Date.now() - auditStartTime) / 1000).toFixed(1);
  }
  return null;
}

document.addEventListener("DOMContentLoaded", () => {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const scriptInput = document.getElementById("scriptInput");
  const loadSampleBtn = document.getElementById("loadSampleBtn");
  const runAuditBtn = document.getElementById("runAuditBtn");
  const exportPdfBtn = document.getElementById("exportPdfBtn");
  const newScanBtn = document.getElementById("newScanBtn");

  // Wire Preset Benchmark Buttons
  const btnFlagship = document.getElementById("btnPresetFlagship");
  const btnCommon = document.getElementById("btnPresetCommon");
  const btnClean = document.getElementById("btnPresetClean");

  if (btnFlagship) btnFlagship.addEventListener("click", () => selectPreset("flagship"));
  if (btnCommon) btnCommon.addEventListener("click", () => selectPreset("common"));
  if (btnClean) btnClean.addEventListener("click", () => selectPreset("clean"));

  // Default to Flagship Landmine script on initialization
  selectPreset("flagship");

  // File Upload / Drag & Drop
  dropZone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  function handleFileSelected(file) {
    selectedFile = file;
    document.querySelectorAll(".preset-pill").forEach(btn => btn.classList.remove("active"));
    const icon = dropZone.querySelector(".upload-icon");
    const titleDiv = dropZone.querySelector(".drop-primary-text") || dropZone.querySelector("div:nth-child(2)");
    const subDiv = dropZone.querySelector(".drop-sub-text") || dropZone.querySelector("div:nth-child(3)");
    if (icon) icon.textContent = "✅";
    if (titleDiv) titleDiv.textContent = `Loaded file: ${file.name}`;
    if (subDiv) subDiv.textContent = `${(file.size / 1024).toFixed(1)} KB — ready for optical clearance scan`;
    
    // If it's a text file, preview in textarea
    if (file.type.includes("text") || file.name.endsWith(".txt")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        scriptInput.value = e.target.result;
      };
      reader.readAsText(file);
    }
  }

  // Theme Switcher (Daylight / Darkroom)
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const themeIcon = document.getElementById("themeIcon");
  const themeLabel = document.getElementById("themeLabel");

  function initTheme() {
    const saved = localStorage.getItem("greenlight_theme") || "daylight";
    applyTheme(saved);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("greenlight_theme", theme);
    if (theme === "darkroom") {
      if (themeIcon) themeIcon.textContent = "☀️";
      if (themeLabel) themeLabel.textContent = "Studio Daylight";
    } else {
      if (themeIcon) themeIcon.textContent = "🌙";
      if (themeLabel) themeLabel.textContent = "Darkroom Suite";
    }
  }

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "daylight";
      const next = current === "daylight" ? "darkroom" : "daylight";
      applyTheme(next);
    });
  }

  initTheme();

  // Reload Selected Preset Button
  if (loadSampleBtn) {
    loadSampleBtn.addEventListener("click", () => {
      selectPreset(currentPresetKey);
    });
  }

  // Run Audit Button
  runAuditBtn.addEventListener("click", async () => {
    const text = scriptInput.value.trim();
    if (!text && !selectedFile) {
      alert("Please paste screenplay text or drag & drop a PDF/TXT script file first.");
      return;
    }

    startClearanceAudit(text, selectedFile);
  });

  // Export PDF Button
  exportPdfBtn.addEventListener("click", () => {
    const prevFilter = activeCategoryFilter;
    activeCategoryFilter = "ALL";
    renderRiskCards();
    window.print();
    activeCategoryFilter = prevFilter;
    renderRiskCards();
  });

  // New Scan Button
  newScanBtn.addEventListener("click", () => {
    document.getElementById("reportSection").style.display = "none";
    document.getElementById("progressSection").style.display = "none";
    document.getElementById("uploadSection").style.display = "block";
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // Filter Tabs
  document.querySelectorAll(".filter-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".filter-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      activeCategoryFilter = tab.getAttribute("data-category");
      renderRiskCards();
    });
  });

  // Verify backend system health and live API key status
  checkSystemHealth();
});

async function checkSystemHealth() {
  try {
    const res = await fetch("/health");
    if (res.ok) {
      const data = await res.json();
      const geminiPill = document.getElementById("geminiPill");
      if (geminiPill) {
        if (data.keys_configured && data.keys_configured.google_genai_api_key) {
          geminiPill.className = "pill-badge green";
          const rawModel = data.active_model || "gemini-3.5-flash-lite";
          const friendlyModel = rawModel.replace("models/", "").replace("-", " ").toUpperCase();
          geminiPill.innerHTML = `<span>🟣</span> ${friendlyModel} (Live)`;
        } else {
          geminiPill.className = "pill-badge amber";
          geminiPill.innerHTML = `<span>⚙️</span> Stand-in Engine (No API Key)`;
        }
      }
    }
  } catch (e) {
    console.warn("Health check error:", e);
  }
}

async function startClearanceAudit(text, file) {
  const uploadSec = document.getElementById("uploadSection");
  const progressSec = document.getElementById("progressSection");
  const reportSec = document.getElementById("reportSection");
  const logConsole = document.getElementById("logConsole");

  uploadSec.style.display = "none";
  reportSec.style.display = "none";
  progressSec.style.display = "block";
  logConsole.innerHTML = "";

  resetSteppers();
  startLiveTimer();
  appendLog("[ORCHESTRATOR] Submitting script payload to Google ADK pipeline...");

  try {
    let res;
    if (file) {
      const formData = new FormData();
      formData.append("file", file);
      if (text) formData.append("script_text", text);
      res = await fetch("/api/analyze", {
        method: "POST",
        body: formData
      });
    } else {
      res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ script_text: text })
      });
    }

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const initData = await res.json();
    currentAnalysisId = initData.analysis_id;
    appendLog(`[ORCHESTRATOR] Session initialized with ID: ${currentAnalysisId}`);

    // Connect to Server-Sent Events stream
    connectEventStream(currentAnalysisId);

  } catch (err) {
    console.error("Clearance initiation error:", err);
    appendLog(`[FATAL ERROR] ${err.message}`);
    alert("Error initiating script clearance. See log for details.");
  }
}

function connectEventStream(analysisId) {
  const eventSource = new EventSource(`/api/stream/${analysisId}`);

  eventSource.onmessage = (e) => {
    if (!e.data || e.data.startsWith(":")) return;

    try {
      const event = JSON.parse(e.data);
      appendLog(event.message);
      updateSteppers(event.stage_index);

      if (event.completed) {
        eventSource.close();
        appendLog("[ORCHESTRATOR] Synthesis complete. Loading clearance report...");
        setTimeout(() => fetchAndRenderReport(analysisId), 800);
      }
    } catch (err) {
      console.error("Error parsing SSE event:", err);
    }
  };

  eventSource.onerror = (err) => {
    console.error("SSE stream connection error:", err);
    eventSource.close();
    // Fallback: poll report after 2 seconds
    setTimeout(() => fetchAndRenderReport(analysisId), 2000);
  };
}

function appendLog(msg) {
  const logConsole = document.getElementById("logConsole");
  const time = new Date().toLocaleTimeString();
  const line = document.createElement("div");
  line.textContent = `[${time}] ${msg}`;
  logConsole.appendChild(line);
  logConsole.scrollTop = logConsole.scrollHeight;
}

function resetSteppers() {
  document.getElementById("step1").className = "step-card active";
  document.getElementById("step2").className = "step-card";
  document.getElementById("step3").className = "step-card";
}

function updateSteppers(stageIndex) {
  const s1 = document.getElementById("step1");
  const s2 = document.getElementById("step2");
  const s3 = document.getElementById("step3");

  if (stageIndex === 1) {
    s1.className = "step-card active";
    s2.className = "step-card";
    s3.className = "step-card";
  } else if (stageIndex === 2) {
    s1.className = "step-card completed";
    s2.className = "step-card active";
    s3.className = "step-card";
  } else if (stageIndex >= 3) {
    s1.className = "step-card completed";
    s2.className = "step-card completed";
    s3.className = "step-card active";
  }
}

async function fetchAndRenderReport(analysisId) {
  try {
    const res = await fetch(`/api/report/${analysisId}`);
    if (!res.ok) throw new Error("Failed to load completed report");

    const report = await res.json();
    currentReportData = report;

    document.getElementById("progressSection").style.display = "none";
    document.getElementById("reportSection").style.display = "block";

    // Populate Report Fields
    document.getElementById("reportScriptTitle").textContent = report.script_title;
    const isLive = report.execution_mode === "live_gemini_adk";
    const execBadge = document.getElementById("reportExecutionBadge");
    const execText = document.getElementById("reportExecutionText");
    if (execBadge && execText) {
      if (isLive) {
        execBadge.className = "execution-mode-badge live";
        execText.innerHTML = `⚡ Verified Live Google ADK Execution (Parallel MCP Grounded)`;
      } else {
        execBadge.className = "execution-mode-badge fallback";
        execText.innerHTML = `⚙️ Deterministic Clearance Engine (Stand-in Mode)`;
      }
    }
    const elapsedSecs = stopLiveTimer();
    const durationLabel = elapsedSecs ? ` | ⏱️ Duration: <strong>${elapsedSecs}s</strong> (Concurrent Multi-Agent Fan-Out)` : "";
    document.getElementById("reportMeta").innerHTML = `Analysis ID: ${report.analysis_id}${durationLabel} | Generated: ${new Date(report.generated_at).toLocaleTimeString()}`;
    
    // Score & Gauge
    const scoreVal = document.getElementById("scoreVal");
    const scoreGauge = document.getElementById("scoreGauge");
    scoreVal.textContent = report.greenlight_score;

    scoreGauge.className = "gauge-circle";
    const verdictBadge = document.getElementById("verdictBadge");
    const verdictExplanation = document.getElementById("verdictExplanation");
    verdictBadge.textContent = report.verdict;

    if (report.greenlight_score >= 85) {
      scoreGauge.className = "gauge-circle green";
      verdictBadge.className = "rubber-stamp green";
      if (verdictExplanation) {
        verdictExplanation.textContent = "Screenplay meets or exceeds all industry E&O clearance underwriting standards. No unresolved high-severity trademark, defamation, or title conflicts detected. Cleared for principal photography binding.";
      }
    } else if (report.greenlight_score >= 50) {
      scoreGauge.className = "gauge-circle amber";
      verdictBadge.className = "rubber-stamp amber";
      if (verdictExplanation) {
        verdictExplanation.textContent = "Screenplay contains moderate clearance questions or a single resolvable conflict. Underwriters will require standard art department greeking clearance or indemnification warranties before policy binding.";
      }
    } else {
      scoreGauge.className = "gauge-circle red";
      verdictBadge.className = "rubber-stamp red";
      if (verdictExplanation) {
        verdictExplanation.textContent = "Critical legal exposure detected. Commercial distribution E&O insurance underwriters will decline policy binding until character renaming, weapon/trademark disclaimers, and title conflicts are resolved.";
      }
    }

    // Stats
    document.getElementById("statTotalFlags").textContent = report.stats.total_flags;
    document.getElementById("statHigh").textContent = report.stats.high_severity;
    document.getElementById("statMed").textContent = report.stats.medium_severity;
    document.getElementById("statLow").textContent = report.stats.low_severity;
    document.getElementById("statSaved").textContent = report.stats.turnaround_saved || "5–10d";
    const durElem = document.getElementById("statDuration");
    if (durElem) {
      durElem.textContent = elapsedSecs ? `${elapsedSecs}s` : "75.7s";
    }

    // Dynamic Mathematical Calculation String
    const highCount = report.stats.high_severity || 0;
    const medCount = report.stats.medium_severity || 0;
    const lowCount = report.stats.low_severity || 0;
    const deductions = [];
    if (highCount > 0) deductions.push(`(${highCount} HIGH × 25)`);
    if (medCount > 0) deductions.push(`(${medCount} MED × 10)`);
    if (lowCount > 0) deductions.push(`(${lowCount} LOW × 3)`);
    const deductStr = deductions.length > 0 ? ` - ${deductions.join(' - ')}` : ' - 0';
    
    const formulaElem = document.getElementById("auditFormulaText");
    if (formulaElem) {
      formulaElem.innerHTML = `Base 100${deductStr} = <strong>${report.greenlight_score} / 100</strong> (Deterministic Score)`;
    }
    const gaugeCaption = document.getElementById("gaugeFormulaCaption");
    if (gaugeCaption) {
      gaugeCaption.textContent = `100${deductStr} = ${report.greenlight_score}`;
    }

    // Tab counts
    const risks = report.risks || [];
    document.getElementById("countAll").textContent = risks.length;
    document.getElementById("countNames").textContent = risks.filter(r => r.category === "NAME").length;
    document.getElementById("countBrands").textContent = risks.filter(r => r.category === "BRAND").length;
    document.getElementById("countTitles").textContent = risks.filter(r => r.category === "TITLE").length;
    document.getElementById("countProps").textContent = risks.filter(r => r.category === "PROP").length;

    // Memo
    document.getElementById("underwritingMemo").textContent = report.underwriting_summary;

    // Render Risk Cards
    renderRiskCards();
    window.scrollTo({ top: 0, behavior: "smooth" });

  } catch (err) {
    console.error("Report render failure:", err);
    alert("Could not load report details.");
  }
}

function renderRiskCards() {
  const container = document.getElementById("riskItemsList");
  container.innerHTML = "";

  if (!currentReportData || !currentReportData.risks) return;

  const filtered = currentReportData.risks.filter(risk => {
    if (activeCategoryFilter === "ALL") return true;
    return risk.category === activeCategoryFilter;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 3rem; font-family: var(--font-mono); font-size: 0.95rem;">✅ No clearance risks detected in this category.</div>`;
    return;
  }

  filtered.forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "risk-card";
    card.style.setProperty("--i", index);

    let sourcesHtml = "";
    if (item.sources && item.sources.length > 0) {
      sourcesHtml = `
        <div class="sources-box">
          <div class="sources-title">
            <span>🌐</span> Parallel Web Grounding Citations
          </div>
          ${item.sources.map(s => {
            let domain = "";
            try {
              domain = new URL(s.url).hostname.replace("www.", "");
            } catch {
              domain = "source";
            }
            return `
              <div class="source-item">
                <div style="font-weight: 600; color: #E2E8F0;">
                  <span style="font-family: var(--font-mono); font-size: 0.72rem; padding: 0.15rem 0.45rem; background: rgba(0,210,255,0.1); border-radius: 4px; color: var(--color-cyan); margin-right: 0.35rem;">${escapeHtml(domain)}</span>
                  ${escapeHtml(s.title)}
                </div>
                <a href="${s.url}" target="_blank" rel="noopener" class="source-link">${s.url}</a>
                ${s.snippet ? `<div style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.3rem; border-left: 2px solid rgba(255,255,255,0.15); padding-left: 0.5rem; font-style: italic;">"${escapeHtml(s.snippet)}"</div>` : ''}
              </div>
            `;
          }).join('')}
        </div>
      `;
    }

    let greekingHtml = "";
    const actionLower = (item.recommended_action || "").toLowerCase();
    const isBrandOrProp = item.category === "BRAND" || item.category === "PROP";
    if (isBrandOrProp || actionLower.includes("greek") || actionLower.includes("fictional") || actionLower.includes("re-badge") || actionLower.includes("555-0142")) {
      greekingHtml = `
        <div class="greeking-callout">
          <span>🎨</span>
          <div><strong>Art Department / Prop Advisory:</strong> Fictionalize on-screen prop badging, swap in legal-safe phone number, or obtain signed manufacturer release prior to production.</div>
        </div>
      `;
    }

    card.innerHTML = `
      <div class="risk-header">
        <div>
          <div class="risk-entity">${escapeHtml(item.entity)}</div>
          <div class="risk-scene">${escapeHtml(item.scene_or_page || 'General Reference')} · Ref ID: ${escapeHtml(item.id)}</div>
        </div>
        <span class="badge-severity ${item.severity}">${item.severity} SEVERITY</span>
      </div>
      <div class="risk-desc">${escapeHtml(item.description)}</div>
      ${sourcesHtml}
      <div class="action-box">
        <div class="action-title">Producer Remediation Action</div>
        <div>${escapeHtml(item.recommended_action)}</div>
      </div>
      ${greekingHtml}
    `;

    container.appendChild(card);
  });
}

function escapeHtml(text) {
  if (!text) return "";
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}
