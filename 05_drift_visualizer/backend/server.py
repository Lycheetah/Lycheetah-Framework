"""
AURA Drift Visualizer — FastAPI Backend
Lycheetah Foundation | Drift Visualizer v1.0

Serves drift scores to the React frontend via:
  REST  /api/score       — score a single turn
  REST  /api/batch       — score a full transcript
  REST  /api/session     — load a saved session
  WS    /ws/live         — live WebSocket stream (real-time mode)

Usage:
  pip install fastapi uvicorn
  python server.py
  # Frontend connects to http://localhost:8000
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from drift_scorer import compute_turn_drift, score_conversation, TurnScore

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("FastAPI not installed. Run: pip install fastapi uvicorn")
    sys.exit(1)

app = FastAPI(title="AURA Drift Visualizer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS_DIR = Path(__file__).parent.parent / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

# ── IN-MEMORY SESSION STATE ───────────────────────────────────────────────────

active_sessions: dict[str, dict] = {}


def get_or_create_session(session_id: str, persona: str = "") -> dict:
    if session_id not in active_sessions:
        active_sessions[session_id] = {
            "session_id": session_id,
            "model_tested": "unknown",
            "timestamp_start": datetime.now(timezone.utc).isoformat(),
            "declared_persona": persona or "constitutional AI assistant",
            "prev_drift": 0.0,
            "turn_counter": 0,
            "drift_history": [],
            "rapid_drift_events": [],
            "threshold_breaches": [],
            "peak_drift": 0.0,
            "peak_drift_turn": 0,
            "prev_alert": "clean",
        }
    return active_sessions[session_id]


# ── REQUEST MODELS ────────────────────────────────────────────────────────────

class TurnRequest(BaseModel):
    session_id: str
    prompt: str
    response: str
    model: str = "unknown"
    persona: str = ""


class BatchRequest(BaseModel):
    session_id: str
    turns: list[dict]
    persona: str = ""
    model: str = "unknown"


class ReplayRequest(BaseModel):
    session_id: str


# ── REST ENDPOINTS ────────────────────────────────────────────────────────────

@app.post("/api/score")
async def score_turn(req: TurnRequest):
    """Score a single conversation turn and add to session history."""
    session = get_or_create_session(req.session_id, req.persona)
    session["model_tested"] = req.model
    session["turn_counter"] += 1

    score = compute_turn_drift(
        turn=session["turn_counter"],
        prompt=req.prompt,
        response=req.response,
        declared_persona=session["declared_persona"],
        prev_drift=session["prev_drift"],
    )

    # Update session state
    if score.drift > session["peak_drift"]:
        session["peak_drift"] = score.drift
        session["peak_drift_turn"] = score.turn

    if score.rapid_drift_event:
        session["rapid_drift_events"].append({
            "turn": score.turn,
            "velocity": score.velocity,
        })

    prev_alert = session["prev_alert"]
    from drift_scorer import THRESHOLDS
    if score.alert != prev_alert:
        prev_hi = THRESHOLDS.get(prev_alert, ("", (0, 0)))[1] if isinstance(THRESHOLDS.get(prev_alert), tuple) else 0
        curr_lo = THRESHOLDS.get(score.alert, (0, 0))[0] if isinstance(THRESHOLDS.get(score.alert), tuple) else 0
        if curr_lo > prev_hi:
            session["threshold_breaches"].append({
                "turn": score.turn,
                "from": prev_alert,
                "to": score.alert,
            })

    result = score.to_dict()
    session["drift_history"].append(result)
    session["prev_drift"] = score.drift
    session["prev_alert"] = score.alert

    return result


@app.post("/api/batch")
async def score_batch(req: BatchRequest):
    """Score a full conversation transcript."""
    result = score_conversation(req.turns, req.persona or "constitutional AI assistant")
    result["session_id"] = req.session_id
    result["model_tested"] = req.model

    # Save session
    session_path = SESSIONS_DIR / f"{req.session_id}.json"
    session_path.write_text(json.dumps(result, indent=2))

    return result


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get current state of a live session."""
    if session_id in active_sessions:
        s = active_sessions[session_id]
        return {
            "session_id": session_id,
            "total_turns": s["turn_counter"],
            "peak_drift": s["peak_drift"],
            "peak_drift_turn": s["peak_drift_turn"],
            "rapid_drift_events": s["rapid_drift_events"],
            "threshold_breaches": s["threshold_breaches"],
            "final_alert_level": s["prev_alert"],
            "drift_history": s["drift_history"],
        }

    session_path = SESSIONS_DIR / f"{session_id}.json"
    if session_path.exists():
        return json.loads(session_path.read_text())

    return {"error": f"Session {session_id} not found"}


@app.get("/api/sessions")
async def list_sessions():
    """List all saved sessions."""
    sessions = []
    for f in sorted(SESSIONS_DIR.glob("*.json"), reverse=True)[:20]:
        try:
            data = json.loads(f.read_text())
            sessions.append({
                "session_id": data.get("session_id", f.stem),
                "total_turns": data.get("total_turns", 0),
                "peak_drift": data.get("peak_drift", 0),
                "final_alert_level": data.get("final_alert_level", "unknown"),
            })
        except Exception:
            pass
    return sessions


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear an active session (reset for new run)."""
    if session_id in active_sessions:
        del active_sessions[session_id]
    return {"cleared": session_id}


# ── WEBSOCKET — LIVE MODE ─────────────────────────────────────────────────────

@app.websocket("/ws/live/{session_id}")
async def websocket_live(websocket: WebSocket, session_id: str):
    """
    Live WebSocket stream.
    Client sends: {"prompt": "...", "response": "...", "model": "..."}
    Server emits: full TurnScore dict on each turn
    """
    await websocket.accept()
    session = get_or_create_session(session_id)

    try:
        while True:
            data = await websocket.receive_json()
            session["turn_counter"] += 1
            if data.get("model"):
                session["model_tested"] = data["model"]

            score = compute_turn_drift(
                turn=session["turn_counter"],
                prompt=data.get("prompt", ""),
                response=data.get("response", ""),
                declared_persona=session["declared_persona"],
                prev_drift=session["prev_drift"],
            )

            result = score.to_dict()
            session["drift_history"].append(result)
            session["prev_drift"] = score.drift
            session["prev_alert"] = score.alert

            if score.rapid_drift_event:
                session["rapid_drift_events"].append({
                    "turn": score.turn,
                    "velocity": score.velocity,
                })

            if score.drift > session["peak_drift"]:
                session["peak_drift"] = score.drift
                session["peak_drift_turn"] = score.turn

            await websocket.send_json(result)

    except WebSocketDisconnect:
        # Save session on disconnect
        if session["drift_history"]:
            session_path = SESSIONS_DIR / f"{session_id}.json"
            session_path.write_text(json.dumps({
                "session_id": session_id,
                "model_tested": session["model_tested"],
                "timestamp_start": session["timestamp_start"],
                "timestamp_end": datetime.now(timezone.utc).isoformat(),
                "total_turns": session["turn_counter"],
                "peak_drift": session["peak_drift"],
                "peak_drift_turn": session["peak_drift_turn"],
                "rapid_drift_events": session["rapid_drift_events"],
                "threshold_breaches": session["threshold_breaches"],
                "final_alert_level": session["prev_alert"],
                "drift_history": session["drift_history"],
            }, indent=2))


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "tool": "AURA Drift Visualizer", "version": "1.0.0"}


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  AURA Drift Visualizer — Backend")
    print("  Lycheetah Foundation | v1.0.0")
    print("  http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
