// GREENLIGHT: Studio Pre-Production Script Clearance Client Engine
let currentAnalysisId = null;
let currentReportData = null;
let activeCategoryFilter = "ALL";
let selectedFile = null;

document.addEventListener("DOMContentLoaded", () => {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const scriptInput = document.getElementById("scriptInput");
  const loadSampleBtn = document.getElementById("loadSampleBtn");
  const runAuditBtn = document.getElementById("runAuditBtn");
  const exportPdfBtn = document.getElementById("exportPdfBtn");
  const newScanBtn = document.getElementById("newScanBtn");

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
    dropZone.querySelector(".upload-icon").textContent = "✅";
    dropZone.querySelector("div:nth-child(2)").textContent = `Loaded file: ${file.name}`;
    dropZone.querySelector("div:nth-child(3)").textContent = `${(file.size / 1024).toFixed(1)} KB — ready to scan`;
    
    // If it's a text file, preview in textarea
    if (file.type.includes("text") || file.name.endsWith(".txt")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        scriptInput.value = e.target.result;
      };
      reader.readAsText(file);
    }
  }

  // Load Landmine Test Script
  loadSampleBtn.addEventListener("click", async () => {
    try {
      loadSampleBtn.disabled = true;
      loadSampleBtn.textContent = "Loading...";
      const res = await fetch("/api/sample");
      const data = await res.json();
      scriptInput.value = data.script_text;
      selectedFile = null;
      dropZone.querySelector(".upload-icon").textContent = "⚡";
      dropZone.querySelector("div:nth-child(2)").textContent = "Landmine Test Screenplay Loaded";
      dropZone.querySelector("div:nth-child(3)").textContent = "Features deliberate character, trademark, and title collisions";
    } catch (err) {
      console.error("Failed to load sample script:", err);
      alert("Failed to load sample script.");
    } finally {
      loadSampleBtn.disabled = false;
      loadSampleBtn.innerHTML = "<span>⚡</span> Load Landmine Demo Script";
    }
  });

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
    window.print();
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
    tab.addEventListener("click", (e) => {
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
          geminiPill.innerHTML = `<span>🟣</span> Gemini 2.0 (Live)`;
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
    const modeHtml = isLive
      ? `<span class="pill-badge green" style="display:inline-flex; font-size:0.75rem; padding: 0.2rem 0.6rem;">🚀 Live Gemini 2.0 + Parallel Search MCP</span>`
      : `<span class="pill-badge amber" style="display:inline-flex; font-size:0.75rem; padding: 0.2rem 0.6rem;">⚙️ Deterministic Stand-in Engine</span>`;
    document.getElementById("reportMeta").innerHTML = `Analysis ID: ${report.analysis_id} | Date: ${new Date(report.generated_at).toLocaleString()} | ${modeHtml}`;
    
    // Score & Gauge
    const scoreVal = document.getElementById("scoreVal");
    const scoreGauge = document.getElementById("scoreGauge");
    scoreVal.textContent = report.greenlight_score;

    scoreGauge.className = "gauge-circle";
    const verdictBadge = document.getElementById("verdictBadge");
    verdictBadge.textContent = report.verdict;

    if (report.greenlight_score >= 85) {
      scoreGauge.classList.add("green");
      verdictBadge.className = "verdict-badge green";
    } else if (report.greenlight_score >= 50) {
      scoreGauge.classList.add("amber");
      verdictBadge.className = "verdict-badge amber";
    } else {
      scoreGauge.classList.add("red");
      verdictBadge.className = "verdict-badge red";
    }

    // Stats
    document.getElementById("statTotalFlags").textContent = report.stats.total_flags;
    document.getElementById("statHigh").textContent = report.stats.high_severity;
    document.getElementById("statMed").textContent = report.stats.medium_severity;
    document.getElementById("statLow").textContent = report.stats.low_severity;
    document.getElementById("statSaved").textContent = report.stats.turnaround_saved || "5–10d";

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
    container.innerHTML = `<div style="text-align: center; color: var(--text-dim); padding: 2rem;">No clearance risks in this category.</div>`;
    return;
  }

  filtered.forEach(item => {
    const card = document.createElement("div");
    card.className = "risk-card";

    let sourcesHtml = "";
    if (item.sources && item.sources.length > 0) {
      sourcesHtml = `
        <div class="sources-box">
          <div class="sources-title">
            <span>🌐</span> Parallel Web Grounding Citations
          </div>
          ${item.sources.map(s => `
            <div class="source-item">
              <div style="font-weight: 600;">${escapeHtml(s.title)}</div>
              <a href="${s.url}" target="_blank" rel="noopener" class="source-link">${s.url}</a>
              ${s.snippet ? `<div style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.25rem;">"${escapeHtml(s.snippet)}"</div>` : ''}
            </div>
          `).join('')}
        </div>
      `;
    }

    card.innerHTML = `
      <div class="risk-header">
        <div>
          <div class="risk-entity">${escapeHtml(item.entity)}</div>
          <div class="risk-scene">${escapeHtml(item.scene_or_page || 'General Reference')} | Ref: ${item.id}</div>
        </div>
        <span class="badge-severity ${item.severity}">${item.severity} SEVERITY</span>
      </div>
      <div class="risk-desc">${escapeHtml(item.description)}</div>
      ${sourcesHtml}
      <div class="action-box">
        <div class="action-title">Producer Remediation Action</div>
        <div>${escapeHtml(item.recommended_action)}</div>
      </div>
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
