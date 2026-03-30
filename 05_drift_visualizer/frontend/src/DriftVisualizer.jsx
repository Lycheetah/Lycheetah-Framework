/**
 * AURA Drift Visualizer
 * Lycheetah Foundation | Drift Visualizer v1.0
 *
 * Renders real-time constitutional alignment drift across conversation turns.
 * Three views: drift timeline, channel breakdown, velocity gauge.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import {
  LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, ResponsiveContainer, Legend
} from "recharts";

// ── CONSTANTS ─────────────────────────────────────────────────────────────────

const API_BASE = "http://localhost:8000";
const SESSION_ID = `session-${Date.now()}`;

const ALERT_COLORS = {
  clean:    "#22c55e",
  caution:  "#eab308",
  warning:  "#f97316",
  critical: "#ef4444",
};

const ALERT_LABELS = {
  clean:    "CLEAN — Alignment nominal",
  caution:  "CAUTION — Minor drift detected",
  warning:  "WARNING — Significant drift",
  critical: "CRITICAL — Provenance broken. Immediate review required.",
};

const CHANNEL_COLORS = {
  SA: "#3b82f6",   // blue
  VA: "#a855f7",   // purple
  IS: "#14b8a6",   // teal
  EI: "#f59e0b",   // amber
};

const CHANNEL_LABELS = {
  SA: "Semantic Alignment",
  VA: "Value Alignment",
  IS: "Identity Stability",
  EI: "Epistemic Integrity",
};

// ── VELOCITY GAUGE ────────────────────────────────────────────────────────────

function VelocityGauge({ velocity = 0 }) {
  const clamp = Math.max(-0.20, Math.min(0.20, velocity));
  const pct = ((clamp + 0.20) / 0.40) * 100; // 0–100
  const isPositive = velocity > 0;
  const isAlarm = Math.abs(velocity) >= 0.10;

  return (
    <div style={styles.gaugeContainer}>
      <div style={styles.gaugeLabel}>DRIFT VELOCITY</div>
      <div style={styles.gaugeTrack}>
        <div style={{
          ...styles.gaugeNeedle,
          left: `${pct}%`,
          backgroundColor: isAlarm
            ? ALERT_COLORS.critical
            : isPositive ? ALERT_COLORS.warning : ALERT_COLORS.clean,
        }} />
        <div style={styles.gaugeCentre} />
      </div>
      <div style={styles.gaugeScale}>
        <span style={{ color: ALERT_COLORS.clean }}>-0.20</span>
        <span>STABLE</span>
        <span style={{ color: ALERT_COLORS.critical }}>+0.20</span>
      </div>
      <div style={{
        ...styles.gaugeValue,
        color: isAlarm ? ALERT_COLORS.critical : isPositive ? ALERT_COLORS.warning : ALERT_COLORS.clean,
      }}>
        {velocity >= 0 ? "+" : ""}{velocity.toFixed(4)}
        {isAlarm && <span style={styles.alarmBadge}>⚡ RAPID DRIFT</span>}
      </div>
    </div>
  );
}

// ── ALERT BANNER ──────────────────────────────────────────────────────────────

function AlertBanner({ alert, rapidDriftEvents, currentTurn }) {
  const lastRapid = rapidDriftEvents[rapidDriftEvents.length - 1];
  const color = ALERT_COLORS[alert] || ALERT_COLORS.clean;

  return (
    <div style={{ ...styles.alertBanner, borderColor: color, backgroundColor: color + "22" }}>
      <span style={{ ...styles.alertDot, backgroundColor: color }} />
      <span style={{ color, fontWeight: 700 }}>
        {ALERT_LABELS[alert] || alert.toUpperCase()}
      </span>
      {lastRapid && (
        <span style={{ color: ALERT_COLORS.critical, marginLeft: 16, fontSize: 13 }}>
          ⚡ Rapid drift at turn {lastRapid.turn} (velocity {lastRapid.velocity > 0 ? "+" : ""}{lastRapid.velocity.toFixed(3)})
        </span>
      )}
      {currentTurn > 0 && (
        <span style={styles.turnBadge}>Turn {currentTurn}</span>
      )}
    </div>
  );
}

// ── CUSTOM TOOLTIP ────────────────────────────────────────────────────────────

function DriftTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;

  return (
    <div style={styles.tooltip}>
      <div style={styles.tooltipTitle}>Turn {d.turn}</div>
      <div>Drift: <strong>{d.drift?.toFixed(4)}</strong></div>
      <div>Velocity: <strong>{d.velocity >= 0 ? "+" : ""}{d.velocity?.toFixed(4)}</strong></div>
      <div>Alert: <strong style={{ color: ALERT_COLORS[d.alert] }}>{d.alert?.toUpperCase()}</strong></div>
      <hr style={styles.tooltipDivider} />
      <div>SA: {d.SA?.toFixed(3)} &nbsp; VA: {d.VA?.toFixed(3)}</div>
      <div>IS: {d.IS?.toFixed(3)} &nbsp; EI: {d.EI?.toFixed(3)}</div>
      {d.rapid_drift_event && <div style={{ color: ALERT_COLORS.critical }}>⚡ Rapid drift event</div>}
    </div>
  );
}

// ── MANUAL INPUT PANEL ────────────────────────────────────────────────────────

function InputPanel({ onScore, loading }) {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");

  const handleSubmit = () => {
    if (!prompt.trim() || !response.trim()) return;
    onScore(prompt, response);
    setPrompt("");
    setResponse("");
  };

  return (
    <div style={styles.inputPanel}>
      <div style={styles.inputPanelTitle}>SCORE A TURN</div>
      <textarea
        style={styles.textarea}
        placeholder="Prompt / user message..."
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        rows={2}
      />
      <textarea
        style={styles.textarea}
        placeholder="Model response..."
        value={response}
        onChange={e => setResponse(e.target.value)}
        rows={4}
      />
      <button
        style={{ ...styles.button, opacity: loading ? 0.6 : 1 }}
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? "Scoring..." : "Score Turn →"}
      </button>
    </div>
  );
}

// ── BATCH LOADER ──────────────────────────────────────────────────────────────

function BatchLoader({ onLoad }) {
  const [text, setText] = useState("");
  const [error, setError] = useState("");

  const handleLoad = () => {
    try {
      const turns = JSON.parse(text);
      if (!Array.isArray(turns)) throw new Error("Must be an array");
      onLoad(turns);
      setText("");
      setError("");
    } catch (e) {
      setError("Invalid JSON. Format: [{\"prompt\": \"...\", \"response\": \"...\"}, ...]");
    }
  };

  return (
    <div style={styles.inputPanel}>
      <div style={styles.inputPanelTitle}>BATCH LOAD (paste JSON transcript)</div>
      <textarea
        style={{ ...styles.textarea, fontFamily: "monospace", fontSize: 12 }}
        placeholder={'[{"prompt": "...", "response": "..."}, ...]'}
        value={text}
        onChange={e => setText(e.target.value)}
        rows={5}
      />
      {error && <div style={styles.error}>{error}</div>}
      <button style={styles.button} onClick={handleLoad}>Load Transcript →</button>
    </div>
  );
}

// ── MAIN COMPONENT ────────────────────────────────────────────────────────────

export default function DriftVisualizer() {
  const [history, setHistory] = useState([]);
  const [alert, setAlert] = useState("clean");
  const [velocity, setVelocity] = useState(0);
  const [rapidEvents, setRapidEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("live"); // "live" | "batch"
  const [sessionExport, setSessionExport] = useState(null);

  const MAX_VISIBLE = 20;
  const visibleHistory = history.slice(-MAX_VISIBLE);

  const scoreTurn = useCallback(async (prompt, response) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: SESSION_ID, prompt, response }),
      });
      const data = await res.json();
      setHistory(prev => [...prev, data]);
      setAlert(data.alert);
      setVelocity(data.velocity);
      if (data.rapid_drift_event) {
        setRapidEvents(prev => [...prev, { turn: data.turn, velocity: data.velocity }]);
      }
    } catch (e) {
      console.error("Score error:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadBatch = useCallback(async (turns) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: `batch-${Date.now()}`, turns }),
      });
      const data = await res.json();
      setHistory(data.drift_history || []);
      setAlert(data.final_alert_level || "clean");
      setVelocity(data.drift_history?.at(-1)?.velocity || 0);
      setRapidEvents(data.rapid_drift_events || []);
      setSessionExport(data);
    } catch (e) {
      console.error("Batch error:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  const resetSession = () => {
    setHistory([]);
    setAlert("clean");
    setVelocity(0);
    setRapidEvents([]);
    setSessionExport(null);
    fetch(`${API_BASE}/api/session/${SESSION_ID}`, { method: "DELETE" }).catch(() => {});
  };

  const exportSession = () => {
    const data = sessionExport || {
      session_id: SESSION_ID,
      total_turns: history.length,
      peak_drift: Math.max(...history.map(h => h.drift), 0),
      rapid_drift_events: rapidEvents,
      final_alert_level: alert,
      drift_history: history,
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `drift-session-${Date.now()}.json`;
    a.click();
  };

  return (
    <div style={styles.root}>

      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerTitle}>AURA DRIFT VISUALIZER</div>
        <div style={styles.headerSub}>Lycheetah Foundation | v1.0.0</div>
        <div style={styles.headerControls}>
          <button
            style={{ ...styles.tabButton, ...(mode === "live" ? styles.tabActive : {}) }}
            onClick={() => setMode("live")}
          >Live</button>
          <button
            style={{ ...styles.tabButton, ...(mode === "batch" ? styles.tabActive : {}) }}
            onClick={() => setMode("batch")}
          >Batch</button>
          <button style={styles.btnSecondary} onClick={resetSession}>Reset</button>
          {history.length > 0 && (
            <button style={styles.btnSecondary} onClick={exportSession}>Export JSON</button>
          )}
        </div>
      </div>

      {/* Alert Banner */}
      <AlertBanner
        alert={alert}
        rapidDriftEvents={rapidEvents}
        currentTurn={history.length}
      />

      {/* Main Chart — Drift Timeline */}
      <div style={styles.chartCard}>
        <div style={styles.chartTitle}>DRIFT TIMELINE</div>
        {history.length === 0 ? (
          <div style={styles.emptyState}>Score turns to see drift timeline</div>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={visibleHistory} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
              <XAxis dataKey="turn" stroke="#666" tick={{ fill: "#888", fontSize: 11 }} label={{ value: "Turn", position: "insideBottom", offset: -5, fill: "#666" }} />
              <YAxis domain={[0, 1]} stroke="#666" tick={{ fill: "#888", fontSize: 11 }} />
              <Tooltip content={<DriftTooltip />} />

              {/* Threshold bands */}
              <ReferenceLine y={0.15} stroke={ALERT_COLORS.clean}   strokeDasharray="4 2" strokeOpacity={0.4} label={{ value: "clean", fill: ALERT_COLORS.clean, fontSize: 10 }} />
              <ReferenceLine y={0.35} stroke={ALERT_COLORS.caution} strokeDasharray="4 2" strokeOpacity={0.4} label={{ value: "caution", fill: ALERT_COLORS.caution, fontSize: 10 }} />
              <ReferenceLine y={0.60} stroke={ALERT_COLORS.warning} strokeDasharray="4 2" strokeOpacity={0.4} label={{ value: "warning", fill: ALERT_COLORS.warning, fontSize: 10 }} />

              <Line
                type="monotone"
                dataKey="drift"
                stroke="#818cf8"
                strokeWidth={2.5}
                dot={(props) => {
                  const { cx, cy, payload } = props;
                  const color = ALERT_COLORS[payload.alert] || "#818cf8";
                  return (
                    <circle key={`dot-${payload.turn}`} cx={cx} cy={cy} r={payload.rapid_drift_event ? 7 : 4}
                      fill={color} stroke={payload.rapid_drift_event ? ALERT_COLORS.critical : color}
                      strokeWidth={payload.rapid_drift_event ? 2 : 0}
                    />
                  );
                }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Lower row: Channel Breakdown + Velocity Gauge */}
      <div style={styles.lowerRow}>

        {/* Channel Breakdown */}
        <div style={{ ...styles.chartCard, flex: 1, minWidth: 0 }}>
          <div style={styles.chartTitle}>CHANNEL BREAKDOWN</div>
          {history.length === 0 ? (
            <div style={styles.emptyState}>—</div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={visibleHistory} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                <XAxis dataKey="turn" stroke="#666" tick={{ fill: "#777", fontSize: 10 }} />
                <YAxis domain={[0, 1]} stroke="#666" tick={{ fill: "#777", fontSize: 10 }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                {Object.entries(CHANNEL_COLORS).map(([key, color]) => (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={color}
                    fill={color + "30"}
                    strokeWidth={1.5}
                    name={CHANNEL_LABELS[key]}
                  />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Velocity Gauge */}
        <div style={{ ...styles.chartCard, width: 220, flexShrink: 0 }}>
          <div style={styles.chartTitle}>VELOCITY</div>
          <VelocityGauge velocity={velocity} />
          {history.length > 0 && (
            <div style={styles.statsGrid}>
              <div style={styles.statItem}>
                <div style={styles.statLabel}>Peak drift</div>
                <div style={styles.statValue}>{Math.max(...history.map(h => h.drift)).toFixed(4)}</div>
              </div>
              <div style={styles.statItem}>
                <div style={styles.statLabel}>Rapid events</div>
                <div style={{ ...styles.statValue, color: rapidEvents.length ? ALERT_COLORS.critical : ALERT_COLORS.clean }}>
                  {rapidEvents.length}
                </div>
              </div>
              <div style={styles.statItem}>
                <div style={styles.statLabel}>Turns scored</div>
                <div style={styles.statValue}>{history.length}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Panel */}
      {mode === "live" && <InputPanel onScore={scoreTurn} loading={loading} />}
      {mode === "batch" && <BatchLoader onLoad={loadBatch} />}

    </div>
  );
}

// ── STYLES ────────────────────────────────────────────────────────────────────

const styles = {
  root: {
    fontFamily: "'Inter', 'Segoe UI', sans-serif",
    backgroundColor: "#0f0f1a",
    color: "#e2e8f0",
    minHeight: "100vh",
    padding: "20px 24px",
    maxWidth: 1100,
    margin: "0 auto",
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: 16,
    marginBottom: 16,
    flexWrap: "wrap",
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 700,
    color: "#c7d2fe",
    letterSpacing: "0.05em",
  },
  headerSub: {
    fontSize: 12,
    color: "#64748b",
    flex: 1,
  },
  headerControls: {
    display: "flex",
    gap: 8,
    alignItems: "center",
  },
  tabButton: {
    padding: "6px 14px",
    borderRadius: 6,
    border: "1px solid #334155",
    backgroundColor: "transparent",
    color: "#94a3b8",
    cursor: "pointer",
    fontSize: 13,
  },
  tabActive: {
    backgroundColor: "#1e1b4b",
    color: "#c7d2fe",
    borderColor: "#4f46e5",
  },
  btnSecondary: {
    padding: "6px 12px",
    borderRadius: 6,
    border: "1px solid #334155",
    backgroundColor: "transparent",
    color: "#64748b",
    cursor: "pointer",
    fontSize: 12,
  },
  alertBanner: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "10px 16px",
    borderRadius: 8,
    border: "1px solid",
    marginBottom: 16,
    fontSize: 14,
  },
  alertDot: {
    width: 10,
    height: 10,
    borderRadius: "50%",
    flexShrink: 0,
  },
  turnBadge: {
    marginLeft: "auto",
    fontSize: 12,
    color: "#64748b",
  },
  chartCard: {
    backgroundColor: "#16162a",
    borderRadius: 10,
    border: "1px solid #1e1e3a",
    padding: "16px 20px",
    marginBottom: 16,
  },
  chartTitle: {
    fontSize: 11,
    fontWeight: 700,
    color: "#64748b",
    letterSpacing: "0.1em",
    marginBottom: 12,
  },
  emptyState: {
    height: 200,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#334155",
    fontSize: 13,
  },
  lowerRow: {
    display: "flex",
    gap: 16,
    flexWrap: "wrap",
  },
  gaugeContainer: {
    padding: "8px 0",
  },
  gaugeLabel: {
    fontSize: 11,
    color: "#64748b",
    marginBottom: 16,
    letterSpacing: "0.1em",
  },
  gaugeTrack: {
    position: "relative",
    height: 12,
    borderRadius: 6,
    background: "linear-gradient(to right, #22c55e, #eab308, #f97316, #ef4444)",
    marginBottom: 6,
  },
  gaugeNeedle: {
    position: "absolute",
    top: -4,
    width: 4,
    height: 20,
    borderRadius: 2,
    transform: "translateX(-50%)",
    transition: "left 0.3s ease",
    boxShadow: "0 0 6px rgba(255,255,255,0.4)",
  },
  gaugeCentre: {
    position: "absolute",
    top: 2,
    left: "50%",
    transform: "translateX(-50%)",
    width: 2,
    height: 8,
    backgroundColor: "rgba(255,255,255,0.3)",
  },
  gaugeScale: {
    display: "flex",
    justifyContent: "space-between",
    fontSize: 10,
    color: "#475569",
    marginTop: 2,
  },
  gaugeValue: {
    textAlign: "center",
    fontSize: 20,
    fontWeight: 700,
    marginTop: 12,
    fontFamily: "monospace",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 4,
  },
  alarmBadge: {
    fontSize: 11,
    fontWeight: 700,
    color: "#ef4444",
    letterSpacing: "0.05em",
  },
  statsGrid: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
    marginTop: 20,
  },
  statItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  statLabel: {
    fontSize: 11,
    color: "#475569",
  },
  statValue: {
    fontSize: 13,
    fontWeight: 700,
    color: "#94a3b8",
    fontFamily: "monospace",
  },
  inputPanel: {
    backgroundColor: "#16162a",
    borderRadius: 10,
    border: "1px solid #1e1e3a",
    padding: "16px 20px",
    marginBottom: 16,
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  inputPanelTitle: {
    fontSize: 11,
    fontWeight: 700,
    color: "#64748b",
    letterSpacing: "0.1em",
  },
  textarea: {
    backgroundColor: "#0f0f1a",
    border: "1px solid #1e1e3a",
    borderRadius: 6,
    color: "#e2e8f0",
    padding: "8px 12px",
    fontSize: 13,
    resize: "vertical",
    outline: "none",
    width: "100%",
    boxSizing: "border-box",
  },
  button: {
    padding: "9px 20px",
    borderRadius: 6,
    border: "none",
    backgroundColor: "#4f46e5",
    color: "#fff",
    fontWeight: 600,
    fontSize: 13,
    cursor: "pointer",
    alignSelf: "flex-start",
  },
  error: {
    color: "#ef4444",
    fontSize: 12,
  },
  tooltip: {
    backgroundColor: "#1e1e3a",
    border: "1px solid #2d2d5a",
    borderRadius: 8,
    padding: "10px 14px",
    fontSize: 12,
    color: "#e2e8f0",
    lineHeight: 1.7,
    boxShadow: "0 4px 20px rgba(0,0,0,0.5)",
  },
  tooltipTitle: {
    fontWeight: 700,
    color: "#c7d2fe",
    marginBottom: 4,
    fontSize: 13,
  },
  tooltipDivider: {
    border: "none",
    borderTop: "1px solid #2d2d5a",
    margin: "6px 0",
  },
};
