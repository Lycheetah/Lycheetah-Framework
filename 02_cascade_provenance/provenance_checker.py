#!/usr/bin/env python3
"""
CASCADE Provenance Checker
Lycheetah Foundation | CASCADE Framework v1.0

Fingerprints knowledge nodes at origin, tracks drift through transformations,
scores provenance integrity, and flags anomalies.

Core loop: Fingerprint → Store → Check → Score Drift → Flag → Report

Usage:
  python provenance_checker.py fingerprint "content here" --source "uri" --author "name"
  python provenance_checker.py check <node_id> "current content here"
  python provenance_checker.py chain <node_id> <node_id> <node_id>
  python provenance_checker.py demo
  python provenance_checker.py list
"""

import sys
import os
import json
import hashlib
import sqlite3
import argparse
import math
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ─── CONSTANTS ───────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent / "provenance_ledger.db"

DRIFT_THRESHOLDS = {
    "clean":    (0.00, 0.15),
    "caution":  (0.16, 0.35),
    "warning":  (0.36, 0.60),
    "critical": (0.61, 1.00),
}

SIM_WEIGHTS = {
    "semantic":     0.40,
    "structural":   0.30,
    "lineage":      0.20,
    "attribution":  0.10,
}

ANOMALY_THRESHOLDS = {
    "ANOMALY_001_SEMANTIC_BLEED":       {"field": "semantic_sim",   "threshold": 0.65, "below": True},
    "ANOMALY_002_LINEAGE_GAP":          {"field": "lineage_intact", "threshold": 0.01, "below": True},
    "ANOMALY_003_ATTRIBUTION_LOSS":     {"field": "source_attr",    "threshold": 0.50, "below": True},
    "ANOMALY_004_STRUCTURAL_COLLAPSE":  {"field": "structural_sim", "threshold": 0.50, "below": True},
}
COMPOUND_DRIFT_THRESHOLD = 0.55
COMPOUND_STEPS_MIN = 3


# ─── DATABASE ────────────────────────────────────────────────────────────────

def init_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            node_id         TEXT PRIMARY KEY,
            semantic_hash   TEXT NOT NULL,
            structure_sig   TEXT NOT NULL,
            content         TEXT NOT NULL,
            source_uri      TEXT,
            author          TEXT,
            created_at      TEXT NOT NULL,
            framework_ver   TEXT,
            cascade_domain  TEXT,
            parent_id       TEXT,
            lineage_chain   TEXT NOT NULL DEFAULT '[]'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            check_id            TEXT PRIMARY KEY,
            node_id             TEXT NOT NULL,
            timestamp           TEXT NOT NULL,
            drift_score         REAL NOT NULL,
            drift_cumulative    REAL,
            alert_level         TEXT NOT NULL,
            anomalies           TEXT NOT NULL DEFAULT '[]',
            component_scores    TEXT NOT NULL DEFAULT '{}',
            action_required     TEXT NOT NULL,
            current_content     TEXT
        )
    """)
    conn.commit()
    return conn


# ─── SEMANTIC SIMILARITY ─────────────────────────────────────────────────────

def _token_set(text: str) -> set:
    """Simple token set for similarity — no external deps required."""
    import re
    tokens = re.findall(r'\b\w+\b', text.lower())
    return set(tokens)


def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Jaccard similarity over token sets.
    Used when sentence-transformers is not available.
    For production, swap in cosine similarity over embeddings.
    """
    if not text_a or not text_b:
        return 0.0
    set_a = _token_set(text_a)
    set_b = _token_set(text_b)
    if not set_a and not set_b:
        return 1.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def _try_embedding_similarity(text_a: str, text_b: str) -> float | None:
    """Try sentence-transformers if available; return None if not installed."""
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer("all-MiniLM-L6-v2")
        emb_a = model.encode(text_a, convert_to_tensor=True)
        emb_b = model.encode(text_b, convert_to_tensor=True)
        score = float(util.cos_sim(emb_a, emb_b)[0][0])
        return max(0.0, min(1.0, score))
    except ImportError:
        return None


def compute_semantic_sim(text_a: str, text_b: str) -> float:
    """Use embeddings if available, fall back to token Jaccard."""
    embedding_score = _try_embedding_similarity(text_a, text_b)
    if embedding_score is not None:
        return embedding_score
    return semantic_similarity(text_a, text_b)


# ─── FINGERPRINTING ──────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    import re
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _semantic_hash(content: str) -> str:
    """64-char prefix of sha256 of normalized content — proxy for embedding hash."""
    return _sha256(_normalize(content))[:64]


def _structure_sig(parent_id: str | None, cascade_domain: str | None) -> str:
    sig_input = f"{parent_id or 'root'}|{cascade_domain or 'unknown'}"
    return _sha256(sig_input)[:32]


def create_fingerprint(
    content: str,
    source_uri: str = "",
    author: str = "",
    framework_ver: str = "1.0.0",
    cascade_domain: str = "",
    parent_id: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> dict:
    """
    Create and store an immutable provenance fingerprint for a knowledge node.
    Returns the fingerprint dict.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    sem_hash = _semantic_hash(content)
    struct_sig = _structure_sig(parent_id, cascade_domain)

    # Build lineage chain
    lineage_chain = []
    if parent_id and conn:
        row = conn.execute(
            "SELECT lineage_chain FROM nodes WHERE node_id = ?", (parent_id,)
        ).fetchone()
        if row:
            lineage_chain = json.loads(row["lineage_chain"])
        lineage_chain.append(parent_id)

    node_id = _sha256(f"{content}{timestamp}{source_uri}")

    fingerprint = {
        "node_id":       node_id,
        "semantic_hash": sem_hash,
        "structure_sig": struct_sig,
        "content":       content,
        "lineage_chain": lineage_chain,
        "origin_meta": {
            "source_uri":       source_uri,
            "author":           author,
            "created_at":       timestamp,
            "framework_version": framework_ver,
            "cascade_domain":   cascade_domain,
        },
        "parent_id": parent_id,
    }

    if conn:
        conn.execute("""
            INSERT OR IGNORE INTO nodes
            (node_id, semantic_hash, structure_sig, content, source_uri, author,
             created_at, framework_ver, cascade_domain, parent_id, lineage_chain)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            node_id, sem_hash, struct_sig, content,
            source_uri, author, timestamp, framework_ver,
            cascade_domain, parent_id, json.dumps(lineage_chain)
        ))
        conn.commit()

    return fingerprint


# ─── DRIFT SCORING ───────────────────────────────────────────────────────────

def score_lineage_intact(origin_chain: list, current_chain: list) -> float:
    """
    1.0 if all lineage steps are present and ordered.
    0.0 if there is a gap (missing step).
    Partial score for partial gaps.
    """
    if not origin_chain and not current_chain:
        return 1.0
    if not current_chain:
        return 0.0
    expected_len = len(origin_chain) + 1
    actual_len = len(current_chain)
    if actual_len == 0:
        return 0.0
    # Check for gaps: all origin chain members should appear in current chain
    if not origin_chain:
        return 1.0
    present = sum(1 for node in origin_chain if node in current_chain)
    return present / len(origin_chain)


def score_source_attribution(
    origin_uri: str, origin_author: str,
    current_uri: str, current_author: str
) -> float:
    """Score how well the original source is still attributed."""
    uri_score = 1.0 if (origin_uri and current_uri and origin_uri == current_uri) else (
        0.5 if current_uri else 0.0
    )
    author_score = 1.0 if (origin_author and current_author and origin_author == current_author) else (
        0.5 if current_author else 0.0
    )
    return (uri_score + author_score) / 2


def score_structural_sim(origin_fp: dict, current_fp: dict) -> float:
    """Compare structure signatures and parent relationships."""
    orig_struct = origin_fp.get("structure_sig", "")
    curr_struct = current_fp.get("structure_sig", "")
    orig_parent = origin_fp.get("parent_id")
    curr_parent = current_fp.get("parent_id")

    struct_match = 1.0 if orig_struct == curr_struct else 0.3
    parent_match = 1.0 if orig_parent == curr_parent else (0.5 if curr_parent else 0.0)

    return (struct_match * 0.6) + (parent_match * 0.4)


def compute_drift(
    origin_fp: dict,
    current_content: str,
    current_uri: str = "",
    current_author: str = "",
    current_lineage: list | None = None,
    current_parent_id: str | None = None,
    current_domain: str = "",
) -> dict:
    """
    Compute drift score between origin fingerprint and current state.
    Returns component scores and composite drift.
    """
    origin_content = origin_fp.get("content", "")
    origin_meta = origin_fp.get("origin_meta", {})
    origin_lineage = origin_fp.get("lineage_chain", [])

    current_lineage = current_lineage or []

    # Build a minimal current fingerprint for structural comparison
    current_fp = {
        "structure_sig": _structure_sig(current_parent_id, current_domain),
        "parent_id": current_parent_id,
    }

    semantic_sim   = compute_semantic_sim(origin_content, current_content)
    structural_sim = score_structural_sim(origin_fp, current_fp)
    lineage_intact = score_lineage_intact(origin_lineage, current_lineage)
    source_attr    = score_source_attribution(
        origin_meta.get("source_uri", ""), origin_meta.get("author", ""),
        current_uri, current_author
    )

    sim = (
        semantic_sim   * SIM_WEIGHTS["semantic"]
        + structural_sim * SIM_WEIGHTS["structural"]
        + lineage_intact * SIM_WEIGHTS["lineage"]
        + source_attr    * SIM_WEIGHTS["attribution"]
    )
    drift = round(1.0 - sim, 4)
    drift = max(0.0, min(1.0, drift))

    return {
        "semantic_sim":   round(semantic_sim,   4),
        "structural_sim": round(structural_sim, 4),
        "lineage_intact": round(lineage_intact, 4),
        "source_attr":    round(source_attr,    4),
        "sim":            round(sim, 4),
        "drift":          drift,
    }


def drift_alert_level(drift: float) -> str:
    if drift <= 0.15:
        return "clean"
    if drift <= 0.35:
        return "caution"
    if drift <= 0.60:
        return "warning"
    return "critical"


def cumulative_drift(drift_steps: list[float]) -> float:
    """
    DRIFT_cumulative = 1 - PRODUCT(SIM_step_i)
    Each step's fidelity multiplies — drift compounds.
    """
    if not drift_steps:
        return 0.0
    fidelity = 1.0
    for d in drift_steps:
        fidelity *= (1.0 - d)
    return round(1.0 - fidelity, 4)


# ─── ANOMALY DETECTION ───────────────────────────────────────────────────────

def detect_anomalies(components: dict, drift_cumulative: float | None, n_steps: int) -> list:
    anomalies = []

    if components["semantic_sim"] < 0.65:
        anomalies.append({
            "code": "ANOMALY_001",
            "name": "SEMANTIC_BLEED",
            "trigger": f"semantic_sim = {components['semantic_sim']} < 0.65",
            "meaning": "Core meaning has changed beyond acceptable variance",
            "action": "Flag + require human review",
        })

    if components["lineage_intact"] < 0.01:
        anomalies.append({
            "code": "ANOMALY_002",
            "name": "LINEAGE_GAP",
            "trigger": f"lineage_intact = {components['lineage_intact']} < 0.01",
            "meaning": "One or more transformation steps are unlogged",
            "action": "Quarantine immediately, trace missing step",
        })

    if components["source_attr"] < 0.50:
        anomalies.append({
            "code": "ANOMALY_003",
            "name": "ATTRIBUTION_LOSS",
            "trigger": f"source_attr = {components['source_attr']} < 0.50",
            "meaning": "Original source no longer traceable",
            "action": "Warn + attempt source recovery",
        })

    if components["structural_sim"] < 0.50:
        anomalies.append({
            "code": "ANOMALY_004",
            "name": "STRUCTURAL_COLLAPSE",
            "trigger": f"structural_sim = {components['structural_sim']} < 0.50",
            "meaning": "Node relationship map has changed fundamentally",
            "action": "Flag as potentially re-categorised or corrupted",
        })

    if (
        drift_cumulative is not None
        and drift_cumulative > COMPOUND_DRIFT_THRESHOLD
        and n_steps >= COMPOUND_STEPS_MIN
    ):
        anomalies.append({
            "code": "ANOMALY_005",
            "name": "COMPOUND_DRIFT",
            "trigger": f"drift_cumulative = {drift_cumulative} > {COMPOUND_DRIFT_THRESHOLD} over {n_steps} steps",
            "meaning": "Per-step drift looked acceptable but compound effect is severe",
            "action": "Trigger full lineage audit",
        })

    return anomalies


def action_required(alert_level: str, anomalies: list) -> str:
    codes = [a["code"] for a in anomalies]
    if "ANOMALY_002" in codes:
        return "quarantine"
    if alert_level == "critical":
        return "reject"
    if alert_level == "warning":
        return "quarantine"
    if alert_level == "caution":
        return "review"
    return "none"


# ─── FULL CHECK ──────────────────────────────────────────────────────────────

def check_node(
    node_id: str,
    current_content: str,
    current_uri: str = "",
    current_author: str = "",
    current_lineage: list | None = None,
    current_parent_id: str | None = None,
    current_domain: str = "",
    prior_drift_steps: list[float] | None = None,
    conn: sqlite3.Connection | None = None,
) -> dict:
    """
    Run a full provenance check on a node against its stored origin fingerprint.
    """
    check_id = f"cascade-prov-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
    timestamp = datetime.now(timezone.utc).isoformat()

    origin_fp = None
    if conn:
        row = conn.execute(
            "SELECT * FROM nodes WHERE node_id = ?", (node_id,)
        ).fetchone()
        if row:
            origin_fp = {
                "node_id":       row["node_id"],
                "semantic_hash": row["semantic_hash"],
                "structure_sig": row["structure_sig"],
                "content":       row["content"],
                "parent_id":     row["parent_id"],
                "lineage_chain": json.loads(row["lineage_chain"]),
                "origin_meta": {
                    "source_uri":  row["source_uri"] or "",
                    "author":      row["author"] or "",
                    "created_at":  row["created_at"],
                    "cascade_domain": row["cascade_domain"] or "",
                },
            }

    if not origin_fp:
        # Node not in ledger — treat as unregistered, score against itself
        origin_fp = create_fingerprint(
            current_content, current_uri, current_author,
            cascade_domain=current_domain, parent_id=current_parent_id
        )

    components = compute_drift(
        origin_fp, current_content,
        current_uri, current_author,
        current_lineage, current_parent_id, current_domain
    )

    drift = components["drift"]
    alert = drift_alert_level(drift)

    # Cumulative drift
    all_steps = (prior_drift_steps or []) + [drift]
    drift_cum = cumulative_drift(all_steps) if len(all_steps) > 1 else None
    n_steps = len(all_steps)

    anomalies = detect_anomalies(components, drift_cum, n_steps)
    action = action_required(alert, anomalies)

    report = {
        "check_id":          check_id,
        "node_id":           node_id,
        "timestamp":         timestamp,
        "drift_score":       drift,
        "drift_cumulative":  drift_cum,
        "alert_level":       alert,
        "anomalies_triggered": anomalies,
        "component_scores": {
            "semantic_sim":   components["semantic_sim"],
            "structural_sim": components["structural_sim"],
            "lineage_intact": components["lineage_intact"],
            "source_attribution": components["source_attr"],
        },
        "lineage_chain":    origin_fp.get("lineage_chain", []),
        "action_required":  action,
    }

    if conn:
        conn.execute("""
            INSERT INTO checks
            (check_id, node_id, timestamp, drift_score, drift_cumulative,
             alert_level, anomalies, component_scores, action_required, current_content)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            check_id, node_id, timestamp, drift, drift_cum,
            alert, json.dumps(anomalies), json.dumps(report["component_scores"]),
            action, current_content[:500]
        ))
        conn.commit()

    return report


# ─── CHAIN CHECK ─────────────────────────────────────────────────────────────

def check_chain(node_ids: list[str], contents: list[str], conn: sqlite3.Connection) -> dict:
    """
    Check a sequence of transformations for cumulative drift.
    node_ids[0] is origin, subsequent are transformation steps.
    """
    if len(node_ids) != len(contents):
        raise ValueError("node_ids and contents must be same length")

    steps = []
    drift_steps = []

    origin_row = conn.execute(
        "SELECT * FROM nodes WHERE node_id = ?", (node_ids[0],)
    ).fetchone()

    if not origin_row:
        raise ValueError(f"Origin node {node_ids[0]} not found in ledger")

    origin_fp = {
        "node_id":       origin_row["node_id"],
        "semantic_hash": origin_row["semantic_hash"],
        "structure_sig": origin_row["structure_sig"],
        "content":       origin_row["content"],
        "parent_id":     origin_row["parent_id"],
        "lineage_chain": json.loads(origin_row["lineage_chain"]),
        "origin_meta": {
            "source_uri": origin_row["source_uri"] or "",
            "author":     origin_row["author"] or "",
            "created_at": origin_row["created_at"],
            "cascade_domain": origin_row["cascade_domain"] or "",
        },
    }

    for i, (nid, content) in enumerate(zip(node_ids, contents)):
        if i == 0:
            steps.append({
                "step": 0,
                "node_id": nid,
                "content_preview": content[:80],
                "drift": 0.0,
                "alert": "clean",
                "note": "origin",
            })
            continue

        components = compute_drift(origin_fp, content)
        drift = components["drift"]
        drift_steps.append(drift)
        alert = drift_alert_level(drift)

        steps.append({
            "step": i,
            "node_id": nid,
            "content_preview": content[:80],
            "drift": drift,
            "alert": alert,
            "components": {
                "semantic_sim":   components["semantic_sim"],
                "structural_sim": components["structural_sim"],
                "lineage_intact": components["lineage_intact"],
                "source_attr":    components["source_attr"],
            },
        })

    drift_cum = cumulative_drift(drift_steps) if drift_steps else 0.0
    anomalies = detect_anomalies(
        steps[-1].get("components", {"semantic_sim": 1, "structural_sim": 1,
                                     "lineage_intact": 1, "source_attr": 1}),
        drift_cum,
        len(drift_steps)
    )

    return {
        "chain_id": f"chain-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "origin_node": node_ids[0],
        "n_transformations": len(drift_steps),
        "steps": steps,
        "drift_cumulative": drift_cum,
        "alert_level": drift_alert_level(drift_cum),
        "anomalies_triggered": anomalies,
        "action_required": action_required(drift_alert_level(drift_cum), anomalies),
    }


# ─── DEMO MODE ───────────────────────────────────────────────────────────────

DEMO_CASES = [
    {
        "name": "Example 1 — Clean Pass",
        "origin": "AURA Protocol enforces seven constitutional invariants for AI governance.",
        "current": "The AURA Protocol uses seven invariants to govern AI behaviour constitutionally.",
        "description": "Minor reword, meaning preserved.",
    },
    {
        "name": "Example 2 — Semantic Bleed",
        "origin": "Earned Light is the principle that insight must be worked for, not given.",
        "current": "Earned Light is about reward and achievement.",
        "description": "Aggressive summarisation strips the core meaning.",
    },
    {
        "name": "Example 3 — Attribution Loss",
        "origin": "CASCADE provenance system tracks knowledge drift across transformation chains.",
        "current": "CASCADE provenance system tracks knowledge drift across transformation chains.",
        "source_uri_origin": "lycheetah.org/cascade/3.2",
        "author_origin": "Mackenzie Clark",
        "source_uri_current": "",
        "author_current": "",
        "description": "Same content but attribution stripped.",
    },
    {
        "name": "Example 4 — Compound Drift (3 steps)",
        "chain": [
            "CASCADE Framework establishes provenance tracking for all knowledge nodes in the system.",
            "CASCADE establishes tracking for knowledge nodes.",
            "CASCADE tracks knowledge.",
            "System tracks data.",
        ],
        "description": "Each step looks minor; compound effect is severe.",
    },
]


def run_demo(conn: sqlite3.Connection) -> None:
    print()
    print(col("bold", "=" * 64))
    print(col("bold", "  CASCADE PROVENANCE CHECKER — DEMO"))
    print(col("bold", "  Six examples from the spec"))
    print(col("bold", "=" * 64))

    for i, case in enumerate(DEMO_CASES):
        print()
        print(col("bold", f"  {case['name']}"))
        print(f"  {case['description']}")
        print()

        if "chain" in case:
            # Compound drift chain
            chain_contents = case["chain"]
            fps = []
            for j, content in enumerate(chain_contents):
                fp = create_fingerprint(content, conn=conn)
                fps.append(fp)

            for j in range(1, len(chain_contents)):
                components = compute_drift(fps[0], chain_contents[j])
                drift_steps_so_far = [
                    compute_drift(fps[0], chain_contents[k])["drift"]
                    for k in range(1, j + 1)
                ]
                drift_cum = cumulative_drift(drift_steps_so_far)
                step_alert = drift_alert_level(components["drift"])
                print(f"    Step {j}: drift = {components['drift']:.2f}  {alert_badge(step_alert)}")

            all_drifts = [compute_drift(fps[0], c)["drift"] for c in chain_contents[1:]]
            final_cum = cumulative_drift(all_drifts)
            anomalies = detect_anomalies(
                compute_drift(fps[0], chain_contents[-1]),
                final_cum, len(all_drifts)
            )
            cum_alert = drift_alert_level(final_cum)
            print()
            print(f"    DRIFT_cumulative = {final_cum:.2f}  {alert_badge(cum_alert)}")
            if anomalies:
                for a in anomalies:
                    print(f"    {col('critical', a['code'])} {a['name']} — {a['action']}")

        else:
            origin = case.get("origin", "")
            current = case.get("current", "")
            src_uri = case.get("source_uri_origin", "lycheetah.org/example")
            author = case.get("author_origin", "Mackenzie Clark")
            curr_uri = case.get("source_uri_current", src_uri)
            curr_author = case.get("author_current", author)

            origin_fp = create_fingerprint(origin, source_uri=src_uri, author=author, conn=conn)
            components = compute_drift(origin_fp, current, curr_uri, curr_author)
            drift = components["drift"]
            alert = drift_alert_level(drift)
            anomalies = detect_anomalies(components, None, 1)

            print(f"    Origin  : \"{origin[:70]}\"")
            print(f"    Current : \"{current[:70]}\"")
            print()
            print(f"    semantic_sim   = {components['semantic_sim']:.2f}")
            print(f"    structural_sim = {components['structural_sim']:.2f}")
            print(f"    lineage_intact = {components['lineage_intact']:.2f}")
            print(f"    source_attr    = {components['source_attr']:.2f}")
            print(f"    DRIFT          = {col('bold', str(drift))}  {alert_badge(alert)}")

            if anomalies:
                for a in anomalies:
                    print(f"    {col('critical', a['code'])} {a['name']} — {a['action']}")
            else:
                print(f"    {col('green', 'No anomalies.')}")

    print()
    print(col("bold", "=" * 64))
    print()


# ─── HUMAN OUTPUT HELPERS ────────────────────────────────────────────────────

C = {
    "critical": "\033[91m",
    "high":     "\033[93m",
    "caution":  "\033[93m",
    "warning":  "\033[33m",
    "clean":    "\033[92m",
    "green":    "\033[92m",
    "bold":     "\033[1m",
    "low":      "\033[37m",
    "reset":    "\033[0m",
}

ALERT_BADGES = {
    "clean":    "[GREEN]  CLEAN",
    "caution":  "[YELLOW] CAUTION",
    "warning":  "[ORANGE] WARNING",
    "critical": "[RED]    CRITICAL",
}

ALERT_COLORS = {
    "clean":    "clean",
    "caution":  "caution",
    "warning":  "warning",
    "critical": "critical",
}


def col(key: str, text: str) -> str:
    return f"{C.get(key, '')}{text}{C['reset']}"


def alert_badge(level: str) -> str:
    badge = ALERT_BADGES.get(level, level)
    color = ALERT_COLORS.get(level, "reset")
    return col(color, badge)


def print_check_report(report: dict) -> None:
    print()
    print(col("bold", "=" * 64))
    print(col("bold", "  CASCADE PROVENANCE CHECK REPORT"))
    print(col("bold", "=" * 64))
    print(f"  Check ID  : {report['check_id']}")
    print(f"  Node ID   : {report['node_id'][:24]}...")
    print(f"  Timestamp : {report['timestamp']}")
    print()

    drift = report["drift_score"]
    alert = report["alert_level"]
    print(col("bold", "-- DRIFT SCORE --------------------------------------------------"))
    print(f"  Drift score      : {col('bold', str(drift))}  {alert_badge(alert)}")
    if report.get("drift_cumulative") is not None:
        cum = report["drift_cumulative"]
        print(f"  Drift cumulative : {cum}  {alert_badge(drift_alert_level(cum))}")

    print()
    cs = report["component_scores"]
    print(col("bold", "-- COMPONENTS ---------------------------------------------------"))
    print(f"  semantic_sim      : {cs['semantic_sim']:.4f}")
    print(f"  structural_sim    : {cs['structural_sim']:.4f}")
    print(f"  lineage_intact    : {cs['lineage_intact']:.4f}")
    print(f"  source_attribution: {cs['source_attribution']:.4f}")

    anomalies = report.get("anomalies_triggered", [])
    print()
    print(col("bold", "-- ANOMALIES ----------------------------------------------------"))
    if anomalies:
        for a in anomalies:
            print(f"  {col('critical', a['code'])} {a['name']}")
            print(f"    Trigger : {a['trigger']}")
            print(f"    Meaning : {a['meaning']}")
            print(f"    Action  : {a['action']}")
    else:
        print(f"  {col('green', 'None detected.')}")

    print()
    action = report["action_required"]
    action_colors = {"none": "green", "review": "caution", "quarantine": "warning", "reject": "critical"}
    print(col("bold", "-- ACTION -------------------------------------------------------"))
    print(f"  {col(action_colors.get(action, 'reset'), action.upper())}")
    print(col("bold", "=" * 64))
    print()


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CASCADE Provenance Checker — Lycheetah Foundation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
commands:
  fingerprint   Create and store a provenance fingerprint for a new node
  check         Check a stored node against new content
  chain         Check cumulative drift across a sequence of transformations
  list          List all stored nodes in the ledger
  demo          Run all 4 demo cases from the spec

examples:
  python provenance_checker.py fingerprint "AURA enforces seven invariants." --source "lycheetah.org/aura" --author "Mac Clark"
  python provenance_checker.py check <node_id> "The AURA protocol uses seven invariants."
  python provenance_checker.py demo
  python provenance_checker.py list
        """,
    )

    sub = parser.add_subparsers(dest="command")

    # fingerprint
    fp_parser = sub.add_parser("fingerprint", help="Fingerprint a new node")
    fp_parser.add_argument("content", help="Node content to fingerprint")
    fp_parser.add_argument("--source", default="", help="Source URI")
    fp_parser.add_argument("--author", default="", help="Author name")
    fp_parser.add_argument("--domain", default="", help="CASCADE domain")
    fp_parser.add_argument("--parent", default=None, help="Parent node ID")
    fp_parser.add_argument("--output", help="Write fingerprint JSON to file")

    # check
    chk_parser = sub.add_parser("check", help="Check a node against new content")
    chk_parser.add_argument("node_id", help="Origin node ID to check against")
    chk_parser.add_argument("current_content", help="Current state of the content")
    chk_parser.add_argument("--source", default="", help="Current source URI")
    chk_parser.add_argument("--author", default="", help="Current author")
    chk_parser.add_argument("--output", help="Write report JSON to file")

    # chain
    chain_parser = sub.add_parser("chain", help="Check cumulative drift across transformations")
    chain_parser.add_argument("node_ids", nargs="+", help="Node IDs in chain order (origin first)")
    chain_parser.add_argument("--contents", nargs="+", help="Content at each step (must match node_ids count)")
    chain_parser.add_argument("--output", help="Write chain report JSON to file")

    # list
    sub.add_parser("list", help="List all stored nodes")

    # demo
    sub.add_parser("demo", help="Run demo cases from the spec")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    conn = init_db()

    if args.command == "fingerprint":
        fp = create_fingerprint(
            args.content,
            source_uri=args.source,
            author=args.author,
            cascade_domain=args.domain,
            parent_id=args.parent,
            conn=conn,
        )
        print()
        print(col("bold", "  Fingerprint created and stored."))
        print(f"  Node ID : {fp['node_id']}")
        print(f"  Semantic: {fp['semantic_hash'][:32]}...")
        print(f"  Lineage : {fp['lineage_chain']}")
        print()
        if args.output:
            Path(args.output).write_text(json.dumps(fp, indent=2))
            print(f"  Saved to: {args.output}")

    elif args.command == "check":
        report = check_node(
            args.node_id,
            args.current_content,
            current_uri=args.source,
            current_author=args.author,
            conn=conn,
        )
        print_check_report(report)
        if args.output:
            Path(args.output).write_text(json.dumps(report, indent=2))
            print(f"Report saved: {args.output}")

    elif args.command == "chain":
        if not args.contents or len(args.contents) != len(args.node_ids):
            print("Error: --contents must be provided with same count as node_ids", file=sys.stderr)
            sys.exit(1)
        result = check_chain(args.node_ids, args.contents, conn)
        print(json.dumps(result, indent=2))
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2))

    elif args.command == "list":
        rows = conn.execute("SELECT node_id, author, source_uri, created_at FROM nodes ORDER BY created_at DESC").fetchall()
        if not rows:
            print("  No nodes in ledger yet.")
        else:
            print()
            print(col("bold", f"  {len(rows)} node(s) in provenance ledger:"))
            for r in rows:
                print(f"  {r['node_id'][:24]}...  author={r['author'] or '—'}  {r['created_at'][:19]}")
            print()

    elif args.command == "demo":
        run_demo(conn)

    conn.close()


if __name__ == "__main__":
    main()
