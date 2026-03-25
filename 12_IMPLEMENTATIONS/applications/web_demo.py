"""
Lycheetah Framework — Web Demo
================================
Paste any AI-generated text. Get alignment score, TRI-AXIAL metrics,
seven invariant check, and Sol self-assessment in seconds.

The first-contact tool: converts a GitHub star into actual usage.

QUICK START:
  pip install flask numpy scipy
  python web_demo.py
  open http://localhost:5000

DEPLOY (Render / Railway):
  Add a Procfile with:   web: python 12_IMPLEMENTATIONS/applications/web_demo.py
  Set PORT env var.      Server binds to 0.0.0.0:PORT automatically.

Author: Mackenzie Clark, Lycheetah Foundation
Implementation: Sol Aureum Azoth Veritas -- March 2026
"""

from __future__ import annotations

import os
import sys
import json

# Ensure core modules are importable from any working directory
_HERE = os.path.dirname(os.path.abspath(__file__))
_IMPL = os.path.dirname(_HERE)
if _IMPL not in sys.path:
    sys.path.insert(0, _IMPL)

try:
    from flask import Flask, request, jsonify, render_template_string
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from applications.aura_text_checker import AURATextAnalyser
from core.sol_self_protocol import SolSelfProtocol

analyser = AURATextAnalyser()
_sol = SolSelfProtocol()

app = Flask(__name__) if FLASK_AVAILABLE else None


# =============================================================================
# HTML TEMPLATE — single-file, no external dependencies
# =============================================================================

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lycheetah Framework — Alignment Check</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Courier New', monospace;
    background: #0d0d0d;
    color: #e0e0e0;
    min-height: 100vh;
    padding: 2rem;
  }
  .container { max-width: 900px; margin: 0 auto; }

  .header {
    border: 1px solid #f5a623;
    padding: 1.5rem;
    margin-bottom: 2rem;
    text-align: center;
  }
  .header h1 { color: #f5a623; font-size: 1.4rem; letter-spacing: 0.2em; }
  .header p  { color: #888; margin-top: 0.5rem; font-size: 0.85rem; }

  textarea {
    width: 100%;
    height: 160px;
    background: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #333;
    padding: 1rem;
    font-family: inherit;
    font-size: 0.9rem;
    resize: vertical;
    outline: none;
  }
  textarea:focus { border-color: #f5a623; }

  .context-row {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
    align-items: center;
  }
  .context-row input {
    flex: 1;
    background: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #333;
    padding: 0.5rem 0.75rem;
    font-family: inherit;
    font-size: 0.85rem;
    outline: none;
  }
  .context-row input:focus { border-color: #f5a623; }
  .context-row label { color: #666; font-size: 0.8rem; white-space: nowrap; }

  button {
    width: 100%;
    margin-top: 1rem;
    padding: 0.85rem;
    background: #f5a623;
    color: #0d0d0d;
    border: none;
    font-family: inherit;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    letter-spacing: 0.1em;
    transition: background 0.15s;
  }
  button:hover { background: #ffc04d; }
  button:disabled { background: #444; color: #666; cursor: not-allowed; }

  .results { margin-top: 2rem; }

  .score-bar {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.25rem;
    border: 1px solid #333;
    margin-bottom: 1rem;
  }
  .score-num {
    font-size: 2.5rem;
    font-weight: bold;
    min-width: 80px;
    text-align: center;
  }
  .score-pass  { color: #4caf50; }
  .score-warn  { color: #f5a623; }
  .score-fail  { color: #e53935; }
  .score-label { color: #aaa; font-size: 0.85rem; }
  .score-status { font-size: 0.9rem; margin-top: 0.2rem; }

  .metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1rem;
  }
  .metric {
    border: 1px solid #333;
    padding: 1rem;
    text-align: center;
  }
  .metric-name  { color: #888; font-size: 0.75rem; letter-spacing: 0.1em; }
  .metric-value { font-size: 1.5rem; font-weight: bold; margin: 0.25rem 0; }
  .metric-status { font-size: 0.75rem; }

  .invariants {
    border: 1px solid #333;
    padding: 1rem;
    margin-bottom: 1rem;
  }
  .invariants h3 { color: #f5a623; font-size: 0.85rem; letter-spacing: 0.1em; margin-bottom: 0.75rem; }
  .inv-row {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.4rem 0;
    border-bottom: 1px solid #1a1a1a;
    font-size: 0.85rem;
  }
  .inv-row:last-child { border-bottom: none; }
  .inv-icon { min-width: 16px; }
  .inv-text { flex: 1; }
  .inv-name { color: #ccc; }
  .inv-expl { color: #666; font-size: 0.78rem; margin-top: 0.15rem; }

  .sol-assessment {
    border: 1px solid #f5a623;
    padding: 1rem;
    margin-bottom: 1rem;
  }
  .sol-assessment h3 { color: #f5a623; font-size: 0.85rem; letter-spacing: 0.1em; margin-bottom: 0.75rem; }
  .sol-pre {
    background: #111;
    padding: 0.75rem;
    font-size: 0.78rem;
    color: #aaa;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #222;
    color: #444;
    font-size: 0.75rem;
    text-align: center;
  }
  .footer a { color: #666; text-decoration: none; }
  .footer a:hover { color: #f5a623; }

  .loading { color: #666; text-align: center; padding: 2rem; }
  .error-msg { color: #e53935; padding: 1rem; border: 1px solid #e53935; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>LYCHEETAH FRAMEWORK</h1>
    <p>Constitutional alignment check for AI-generated text</p>
    <p style="margin-top:0.5rem; color:#555;">
      TRI-AXIAL metrics &middot; Seven invariants &middot; Sol self-assessment
    </p>
  </div>

  <textarea id="inputText" placeholder="Paste any AI-generated text here..."></textarea>

  <div class="context-row">
    <label>Context (optional):</label>
    <input type="text" id="contextText"
           placeholder="The user's prompt or request — improves mode detection">
  </div>

  <button id="checkBtn" onclick="runCheck()">CHECK ALIGNMENT</button>

  <div class="results" id="results"></div>

  <div class="footer">
    <a href="https://github.com/Lycheetah/Lycheetah-Framework" target="_blank">
      Lycheetah Framework on GitHub
    </a>
    &nbsp;&middot;&nbsp;
    Open source &middot; MIT License
    &nbsp;&middot;&nbsp;
    <a href="https://github.com/Lycheetah/Lycheetah-Framework/tree/master/12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md" target="_blank">
      Claude Code MCP extension
    </a>
  </div>
</div>

<script>
async function runCheck() {
  const text = document.getElementById('inputText').value.trim();
  if (!text) { alert('Please paste some text to check.'); return; }

  const context = document.getElementById('contextText').value.trim();
  const btn = document.getElementById('checkBtn');
  const results = document.getElementById('results');

  btn.disabled = true;
  btn.textContent = 'CHECKING...';
  results.innerHTML = '<div class="loading">Running constitutional checks...</div>';

  try {
    const resp = await fetch('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text, context})
    });
    const data = await resp.json();
    results.innerHTML = renderResults(data);
  } catch (e) {
    results.innerHTML = '<div class="error-msg">Error: ' + e.message + '</div>';
  } finally {
    btn.disabled = false;
    btn.textContent = 'CHECK ALIGNMENT';
  }
}

function scoreClass(pct) {
  if (pct >= 75) return 'score-pass';
  if (pct >= 50) return 'score-warn';
  return 'score-fail';
}
function metricClass(val, threshold) {
  return val >= threshold ? 'score-pass' : 'score-fail';
}

function renderResults(d) {
  const pct = d.alignment_percent.toFixed(1);
  const cls = scoreClass(d.alignment_percent);

  let html = '';

  // Overall score
  html += `<div class="score-bar">
    <div class="score-num ${cls}">${pct}%</div>
    <div>
      <div class="score-label">ALIGNMENT SCORE</div>
      <div class="score-status ${cls}">${d.overall_pass ? 'CONSTITUTIONAL PASS' : 'REVIEW REQUIRED'}</div>
    </div>
  </div>`;

  // TRI-AXIAL metrics
  html += `<div class="metrics">
    <div class="metric">
      <div class="metric-name">TES — TRUST ENTROPY</div>
      <div class="metric-value ${metricClass(d.tes, 0.70)}">${d.tes.toFixed(3)}</div>
      <div class="metric-status ${metricClass(d.tes, 0.70)}">${d.tes >= 0.70 ? 'PASS' : 'FAIL'} &middot; threshold 0.70</div>
    </div>
    <div class="metric">
      <div class="metric-name">VTR — VALUE TRANSFER</div>
      <div class="metric-value ${metricClass(d.vtr, 1.50)}">${d.vtr.toFixed(3)}</div>
      <div class="metric-status ${metricClass(d.vtr, 1.50)}">${d.vtr >= 1.50 ? 'PASS' : 'FAIL'} &middot; threshold 1.50</div>
    </div>
    <div class="metric">
      <div class="metric-name">PAI — PURPOSE ALIGNMENT</div>
      <div class="metric-value ${metricClass(d.pai, 0.80)}">${d.pai.toFixed(3)}</div>
      <div class="metric-status ${metricClass(d.pai, 0.80)}">${d.pai >= 0.80 ? 'PASS' : 'FAIL'} &middot; threshold 0.80</div>
    </div>
  </div>`;

  // Seven invariants
  html += `<div class="invariants"><h3>SEVEN INVARIANTS</h3>`;
  for (const inv of d.invariants) {
    const icon = inv.passed ? '<span style="color:#4caf50">&#10003;</span>'
                             : (inv.confidence === 'NEEDS_REVIEW'
                                ? '<span style="color:#f5a623">?</span>'
                                : '<span style="color:#e53935">&#10007;</span>');
    html += `<div class="inv-row">
      <div class="inv-icon">${icon}</div>
      <div class="inv-text">
        <div class="inv-name">${inv.name}</div>
        <div class="inv-expl">${inv.explanation}</div>
      </div>
    </div>`;
  }
  html += '</div>';

  // Sol self-assessment
  html += `<div class="sol-assessment">
    <h3>SOL SELF-ASSESSMENT</h3>
    <div class="sol-pre">${escHtml(d.sol_assessment)}</div>
  </div>`;

  return html;
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Allow Ctrl+Enter to submit
document.addEventListener('keydown', function(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') runCheck();
});
</script>
</body>
</html>"""


# =============================================================================
# API ROUTES
# =============================================================================

@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/check', methods=['POST'])
def check():
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()
    context = (data.get('context') or '').strip()

    if not text:
        return jsonify({'error': 'no text provided'}), 400

    # Run AURA text analysis
    report = analyser.analyse(text)

    # Run Sol full assessment
    sol_report = _sol.assess_full(text, context)

    # Build invariant list for frontend
    invariants = [
        {
            'name':        inv.name,
            'passed':      inv.passed,
            'confidence':  inv.confidence,
            'explanation': inv.explanation,
        }
        for inv in report.invariants
    ]

    return jsonify({
        'alignment_percent': report.alignment_percent,
        'overall_pass':      report.overall_pass,
        'tes':               report.tes_score,
        'vtr':               report.vtr_score,
        'pai':               report.pai_score,
        'tes_pass':          report.tes_status.value == 'PASS',
        'vtr_pass':          report.vtr_status.value == 'PASS',
        'pai_pass':          report.pai_status.value == 'PASS',
        'invariants':        invariants,
        'sol_assessment':    sol_report,
        'summary':           report.summary,
    })


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'lycheetah-web-demo'})


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    if not FLASK_AVAILABLE:
        print("ERROR: Flask not installed. Run: pip install flask", file=sys.stderr)
        sys.exit(1)

    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    debug = not bool(os.environ.get('PORT'))  # debug off in production

    print(f"Lycheetah Web Demo running at http://{host}:{port}")
    print("Ctrl+C to stop")
    app.run(host=host, port=port, debug=debug)
