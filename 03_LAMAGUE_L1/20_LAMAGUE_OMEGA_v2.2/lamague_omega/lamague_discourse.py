#!/usr/bin/env python3
"""
===============================================================================
LAMAGUE Ω v2.2 — EVIDENTIAL GRAMMAR, 5-SLOT CLASSIFIER & DISCOURSE ENGINE
===============================================================================
Author:   Aetheron (Antigravity Seat — Gemini 4 Argon) & Mackenzie Conor James Clark
Lineage:  Lycheetah Framework — Extending LAMAGUE Ω with Evidential,
          State-Addressed, Multi-Turn Human-AI & Cross-Seat Vocabulary
Location: creations/lamague_omega/lamague_discourse.py

Extends `lamague_omega.py` with:
  1. 20 New Morphemes (`LAMAGUE_V22_DISCOURSE_ROOTS`):
       - 5 Evidentiality Particles (`vira, sora, nura, kura, fara`).
       - 5 S=(H,K,A,R) State-Register Particles (`hista, kreda, autha, rekva, horza`).
       - 5 Causal & Boundary Connectors (`zeno, veka, boka, dosa, paka`).
       - 5 Epistemic Layer & Risk Markers (`fonda, teora, edga, riska, kalma`).
  2. Sardinas–Patterson (1953) Analysis across the 135-morpheme lexicon
     (80 base free roots + 20 v2.2 discourse roots = 100 free roots, plus
     35 bound glottal modifiers [31 canonical SOMA/THANATOS + 4 suffix/interrogative]
     = 135 total morphemes), reporting three regimes separately:
       (a) framed (`r.` / `ʔm.`): True (trivial comma code; continuous speech
           requires an audible word boundary — an UNTESTED_PHONOLOGICAL_ASSUMPTION).
       (b) raw roots + modifiers, unframed: False (witness `'in'`).
       (c) roots + `ʔmods`, no `.` terminator: False (witness `'in'`).
  3. 5-Slot Epistemic Classifier (`English -> SpL-Ω v2.2 / SXP-L v2.2 / CORE v0.4`)
     with strict disk-receipt verification for `vira` and Ed25519 `SignedActionPermit`
     verification for `periva/veka`.
===============================================================================
"""

from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import lamague_omega as lo


# =============================================================================
# 1. THE 20 NEW LAMAGUE Ω v2.2 EVIDENTIAL, REGISTER, CAUSAL & LAYER MORPHEMES
# =============================================================================

LAMAGUE_V22_DISCOURSE_ROOTS: Dict[str, Dict[str, Any]] = {
    # --- 1. Evidentiality Particles (Mandatory Epistemic Provenance) ---
    "vira": {
        "class": "EVIDENTIAL",
        "token": "EVID_WITNESSED",
        "ipa": "ˈvi.ɾa",
        "native36_path": ["E", "V"],
        "core_op": "Ψ_wit",
        "gloss": "empirically witnessed with runtime/disk SHA-256 receipt",
        "english_marker": "[WITNESSED]",
    },
    "sora": {
        "class": "EVIDENTIAL",
        "token": "EVID_DERIVED",
        "ipa": "ˈso.ɾa",
        "native36_path": ["N", "Q"],
        "core_op": "Φ↑_der",
        "gloss": "derived by algebraic or mathematical computation",
        "english_marker": "[DERIVED]",
    },
    "nura": {
        "class": "EVIDENTIAL",
        "token": "EVID_PEER",
        "ipa": "ˈnu.ɾa",
        "native36_path": ["G", "I"],
        "core_op": "📡_peer",
        "gloss": "peer-reported across seats without local rerun",
        "english_marker": "[PEER-REPORTED]",
    },
    "kura": {
        "class": "EVIDENTIAL",
        "token": "EVID_UNKNOWN",
        "ipa": "ˈku.ɾa",
        "native36_path": ["U"],
        "core_op": "U<T>",
        "gloss": "held as an explicit unverified unknown U<T>",
        "english_marker": "[UNKNOWN U<T>]",
    },
    "fara": {
        "class": "EVIDENTIAL",
        "token": "EVID_REFUTED",
        "ipa": "ˈfa.ɾa",
        "native36_path": ["D", "N"],
        "core_op": "↯_ref",
        "gloss": "falsified by counterexample; preserved in history H without erasure",
        "english_marker": "[REFUTED-IN-H]",
    },

    # --- 2. S=(H,K,A,R) State-Register Particles ---
    "hista": {
        "class": "REGISTER",
        "token": "REG_H",
        "ipa": "ˈhis.ta",
        "native36_path": ["O", "R"],
        "core_op": "H_hist",
        "gloss": "in historical provenance register H",
        "english_marker": "in History(H)",
    },
    "kreda": {
        "class": "REGISTER",
        "token": "REG_K",
        "ipa": "ˈkɾe.da",
        "native36_path": ["E", "N"],
        "core_op": "K_end",
        "gloss": "in currently endorsed knowledge register K",
        "english_marker": "in Endorsed-Knowledge(K)",
    },
    "autha": {
        "class": "REGISTER",
        "token": "REG_A",
        "ipa": "ˈau.θa",
        "native36_path": ["P", "W"],
        "core_op": "A_perm",
        "gloss": "in effective human authority register A",
        "english_marker": "in Authority(A)",
    },
    "rekva": {
        "class": "REGISTER",
        "token": "REG_R",
        "ipa": "ˈɾek.va",
        "native36_path": ["F", "Y"],
        "core_op": "R_cap",
        "gloss": "in physical recovery capability register R",
        "english_marker": "in Recovery-Capability(R)",
    },
    "horza": {
        "class": "REGISTER",
        "token": "REG_HORIZON",
        "ipa": "ˈhoɾ.za",
        "native36_path": ["S", "Q"],
        "core_op": "H_opt",
        "gloss": "in former epistemic option horizon [Option_A, Option_B]",
        "english_marker": "in Option-Horizon(H_opt)",
    },

    # --- 3. Causal, Dissent & Boundary Connectors ---
    "zeno": {
        "class": "CONNECTOR",
        "token": "CONN_BECAUSE",
        "ipa": "ˈze.no",
        "native36_path": ["E", "A"],
        "core_op": "⊢_ev",
        "gloss": "grounded in / because of verified receipt",
        "english_marker": "because-of-receipt",
    },
    "veka": {
        "class": "CONNECTOR",
        "token": "CONN_THEREFORE",
        "ipa": "ˈve.ka",
        "native36_path": ["A", "Y"],
        "core_op": "⇒_act",
        "gloss": "therefore permitted to execute within scope",
        "english_marker": "therefore-permitted",
    },
    "boka": {
        "class": "CONNECTOR",
        "token": "CONN_BOUNDARY",
        "ipa": "ˈbo.ka",
        "native36_path": ["W", "I"],
        "core_op": "⊗_deny",
        "gloss": "hard read-only / do-not-touch boundary lock (DENY)",
        "english_marker": "under-boundary-lock(DENY)",
    },
    "dosa": {
        "class": "CONNECTOR",
        "token": "CONN_DISSENT",
        "ipa": "ˈdo.sa",
        "native36_path": ["C", "W"],
        "core_op": "∥_dis",
        "gloss": "preserving polyphonic dissent (v_A != v_B)",
        "english_marker": "preserving-dissent(v_A!=v_B)",
    },
    "paka": {
        "class": "CONNECTOR",
        "token": "CONN_INTERSECT",
        "ipa": "ˈpa.ka",
        "native36_path": ["K", "G"],
        "core_op": "∩_perm",
        "gloss": "restricted to joint permitted action intersection (A_perm ∩ B_perm)",
        "english_marker": "in-joint-intersection(A∩B)",
    },

    # --- 4. Epistemic Layer & Breathing Risk Markers ---
    "fonda": {
        "class": "LAYER",
        "token": "LAYER_FOUNDATION",
        "ipa": "ˈfon.da",
        "native36_path": ["A", "I"],
        "core_op": "L_found",
        "gloss": "at FOUNDATION epistemic layer",
        "english_marker": "at-Layer(FOUNDATION)",
    },
    "teora": {
        "class": "LAYER",
        "token": "LAYER_THEORY",
        "ipa": "te.ˈo.ɾa",
        "native36_path": ["N", "B"],
        "core_op": "L_theor",
        "gloss": "at THEORY epistemic layer (narrowed by CASCADE)",
        "english_marker": "at-Layer(THEORY)",
    },
    "edga": {
        "class": "LAYER",
        "token": "LAYER_EDGE",
        "ipa": "ˈed.ga",
        "native36_path": ["S", "U"],
        "core_op": "L_edge",
        "gloss": "at EDGE / experimental epistemic layer",
        "english_marker": "at-Layer(EDGE)",
    },
    "riska": {
        "class": "RISK_GATE",
        "token": "RISK_HIGH",
        "ipa": "ˈɾis.ka",
        "native36_path": ["W", "Z"],
        "core_op": "Z↑_high",
        "gloss": "HIGH/CRITICAL risk — mandates full semantic expansion (Z_up)",
        "english_marker": "[RISK:HIGH->Z_up]",
    },
    "kalma": {
        "class": "RISK_GATE",
        "token": "RISK_LOW",
        "ipa": "ˈkal.ma",
        "native36_path": ["G", "Z"],
        "core_op": "Z↓_low",
        "gloss": "LOW risk — permits capsule compression (Z_down)",
        "english_marker": "[RISK:LOW->Z_down]",
    },
}

CANONICAL_SOMA_THANATOS_CATEGORIES = {"prosodic", "breath", "gesture", "spatial", "temporal"}


def verify_extended_135_morpheme_decodability() -> Dict[str, Any]:
    """
    Evaluate the 135-morpheme lexicon (80 base free roots + 20 v2.2 discourse
    roots = 100 free roots, plus 35 bound glottal modifiers [31 canonical
    SOMA/THANATOS particles + 4 compound/interrogative suffixes] = 135 morphemes)
    across three distinct Sardinas–Patterson (1953) regimes:
      (a) framed (`r.` / `ʔm.`): True (trivial comma code — requires an audible
          word boundary, labelled an UNTESTED_PHONOLOGICAL_ASSUMPTION).
      (b) raw roots + modifiers, unframed: False (witness `'in'`).
      (c) roots + `ʔmods`, no `.` terminator: False (witness `'in'`).
    """
    existing_roots = set(lo.UNIFIED_SPOKEN_ROOTS.keys())
    new_roots = set(LAMAGUE_V22_DISCOURSE_ROOTS.keys())
    overlap = sorted(existing_roots & new_roots)

    combined_free_roots = existing_roots | new_roots
    bound_mods = set(lo.UNIFIED_BOUND_MODIFIERS.keys())
    canonical_31_mods = {
        k for k, v in lo.UNIFIED_BOUND_MODIFIERS.items()
        if v.get("category") in CANONICAL_SOMA_THANATOS_CATEGORIES
    }
    bare_homophones = sorted(combined_free_roots & bound_mods)
    glottal_mods_no_dot = {f"{lo.GLOTTAL}{m}" for m in bound_mods}
    glottal_overlap = sorted(combined_free_roots & glottal_mods_no_dot)

    # (a) Framed comma code (r. / ʔm.)
    framed_roots = {f"{r}." for r in combined_free_roots}
    framed_mods = {f"{lo.GLOTTAL}{m}." for m in bound_mods}
    full_135_code = framed_roots | framed_mods
    framed_ok, framed_witness, framed_steps = lo.sardinas_patterson_verify(full_135_code)

    # (b) Raw roots + modifiers, unframed (no glottal stop, no '.')
    raw_b_set = combined_free_roots | bound_mods
    raw_b_ok, raw_b_witness, raw_b_steps = lo.sardinas_patterson_verify(raw_b_set)

    # (c) Roots + ʔmods, no '.'
    raw_c_set = combined_free_roots | glottal_mods_no_dot
    raw_c_ok, raw_c_witness, raw_c_steps = lo.sardinas_patterson_verify(raw_c_set)

    new20_unspaced_ok, new20_witness, _ = lo.sardinas_patterson_verify(new_roots)

    return {
        "existing_free_roots_count": len(existing_roots),
        "new_v22_discourse_roots_count": len(new_roots),
        "combined_free_roots_count": len(combined_free_roots),
        "bound_modifiers_count": len(bound_mods),
        "canonical_soma_thanatos_modifiers_count": len(canonical_31_mods),
        "compound_and_interrogative_modifiers_count": len(bound_mods) - len(canonical_31_mods),
        "total_morphemes_count": len(full_135_code),
        "root_homophone_overlap": overlap,
        "bare_root_modifier_homophones": bare_homophones,
        "glottal_prefixed_root_modifier_overlap": glottal_overlap,
        "new_20_unspaced_uniquely_decodable": new20_unspaced_ok,
        "new_20_unspaced_witness": new20_witness,
        "a_framed_with_terminator": {
            "uniquely_decodable": framed_ok and len(overlap) == 0,
            "witness": framed_witness,
            "steps": framed_steps,
            "note": (
                "TRIVIAL_COMMA_CODE: appending '.' to every codeword makes a comma code, which is "
                "trivially uniquely decodable whenever words are distinct. Continuous speech requires "
                "an audible word boundary (UNTESTED_PHONOLOGICAL_ASSUMPTION)."
            ),
        },
        "b_raw_roots_and_mods_unframed": {
            "uniquely_decodable": raw_b_ok,
            "witness": raw_b_witness,
            "steps": raw_b_steps,
        },
        "c_roots_and_glottal_mods_no_terminator": {
            "uniquely_decodable": raw_c_ok,
            "witness": raw_c_witness,
            "steps": raw_c_steps,
        },
        "framed_stream_distinct_with_terminator": framed_ok and len(overlap) == 0,
        "framed_stream_witness": framed_witness,
        "sardinas_patterson_steps": framed_steps,
    }


# =============================================================================
# 2. 5-SLOT EPISTEMIC CLASSIFIER: ENGLISH -> LAMAGUE Ω v2.2 DISCOURSE
# =============================================================================

_RE_REFUTED = re.compile(r"\b(?:refuted|falsified|counterexample)\b", re.IGNORECASE)
_RE_PEER = re.compile(r"\b(?:peer-reported|peer\s+reported|reported\s+by|without\s+local\s+rerun)\b", re.IGNORECASE)
_RE_DERIVED = re.compile(r"\b(?:derived|algebraic|sardinas)\b", re.IGNORECASE)

_RE_REG_R = re.compile(r"\b(?:backup|recovery|restore|snapshot)\b", re.IGNORECASE)
_RE_REG_HORIZON = re.compile(r"\b(?:option\s+a|option\s+b|horizon|unchosen)\b", re.IGNORECASE)
_RE_REG_H = re.compile(r"\b(?:history|original\s+claim|formerly|at\s+t1)\b", re.IGNORECASE)
_RE_REG_A = re.compile(r"\b(?:authority|permission|read-only|do\s+not|boundary|revoke|grant|permit)\b", re.IGNORECASE)

_RE_LAYER_FOUNDATION = re.compile(r"\bfoundation\b", re.IGNORECASE)
_RE_LAYER_THEORY = re.compile(r"\b(?:theory|narrowed|demoted|demotion)\b", re.IGNORECASE)
_RE_LAYER_EDGE = re.compile(r"\bedge\b", re.IGNORECASE)

_RE_RISK_HIGH = re.compile(
    r"\b(?:high\s+risk|risk_level:\s*high|critical|irreversible|read-only|do\s+not|push|release|publish|deploy|delete|merge)\b",
    re.IGNORECASE,
)

_RE_ACT_REVOKE = re.compile(r"\b(?:revoke|read-only|do\s+not|never\s+touch|freeze)\b", re.IGNORECASE)
_RE_ACT_DISSENT = re.compile(r"\b(?:dissent|disagree|v_a|v_b|intersection)\b", re.IGNORECASE)
_RE_ACT_GRANT = re.compile(r"\b(?:grant|authorize|permit|allow)\b", re.IGNORECASE)


def _verify_disk_receipt(receipt: Optional[Dict[str, str]]) -> Tuple[bool, str]:
    """
    Verify `receipt={"path": ..., "sha256": ...}` by reading the actual file on disk
    and comparing its SHA-256 digest. Never emits `vira` without a matching file on disk.
    """
    if not isinstance(receipt, dict):
        return False, "NO_RECEIPT_PROVIDED"
    raw_path = receipt.get("path", "")
    expected_sha = str(receipt.get("sha256", "")).strip().lower()
    if not raw_path or not expected_sha or len(expected_sha) != 64:
        return False, "RECEIPT_MISSING_PATH_OR_SHA256"
    fpath = Path(raw_path)
    try:
        if not fpath.is_file() or fpath.is_symlink():
            return False, "RECEIPT_FILE_MISSING_OR_SYMLINK"
        actual_sha = hashlib.sha256(fpath.read_bytes()).hexdigest().lower()
    except OSError as exc:
        return False, f"RECEIPT_IO_ERROR:{exc}"
    if actual_sha != expected_sha:
        return False, f"RECEIPT_SHA256_MISMATCH:expected={expected_sha[:12]}!=actual={actual_sha[:12]}"
    return True, f"VERIFIED_DISK_SHA256:{actual_sha[:12]}"


def _verify_signed_action_permit(permit: Any, authority_public_key: Any = None) -> Tuple[bool, str]:
    """
    Verify that `permit` is a valid Ed25519-signed `SignedActionPermit` from `guarded_handoff`.
    """
    if permit is None:
        return False, "NO_SIGNED_ACTION_PERMIT_PROVIDED"
    if not hasattr(permit, "verify_signature") or not hasattr(permit, "expires_at_unix"):
        return False, "INVALID_PERMIT_OBJECT"
    if time.time() > float(getattr(permit, "expires_at_unix", 0.0)):
        return False, "SIGNED_ACTION_PERMIT_EXPIRED"
    if not permit.verify_signature(authority_public_key):
        return False, "SIGNED_ACTION_PERMIT_SIGNATURE_INVALID"
    return True, f"VERIFIED_PERMIT:{getattr(permit, 'permit_id', 'OK')}"


def translate_english_to_lamague_v22(
    english_text: str,
    speaker: str = "Aetheron",
    addressee: str = "Mac",
    receipt: Optional[Dict[str, str]] = None,
    permit: Optional[Any] = None,
    authority_public_key: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Classify an English engineering/governance statement into the 5-slot
    `LAMAGUE Ω v2.2` Discourse Utterance (`evidential`, `register`, `layer`,
    `risk`, `action`):
      - Default evidential is `"kura"` (unknown), NEVER `"vira"`.
      - `"vira"` is emitted ONLY when `receipt={"path", "sha256"}` is passed and
        matches the re-hashed file on disk.
      - `"periva veka"` (grant) is emitted ONLY when a valid `SignedActionPermit`
        is passed and verified. Otherwise a grant request emits a refusal (`nevira boka`).
      - `push/release/publish/deploy/delete/merge` always emit `"riska"`.
    """
    morphemes: List[str] = ["mi"]

    # 1. Evidentiality Gate (default is ALWAYS 'kura' unless receipt verified on disk)
    receipt_ok, receipt_reason = _verify_disk_receipt(receipt)
    if receipt is not None:
        if receipt_ok:
            evid = "vira"
            evid_reason = receipt_reason
        else:
            evid = "kura"
            evid_reason = receipt_reason
    elif _RE_REFUTED.search(english_text):
        evid = "fara"
        evid_reason = "MATCHED_REFUTATION_MARKER"
    elif _RE_PEER.search(english_text):
        evid = "nura"
        evid_reason = "MATCHED_PEER_REPORT_MARKER"
    elif _RE_DERIVED.search(english_text):
        evid = "sora"
        evid_reason = "MATCHED_DERIVATION_MARKER"
    else:
        evid = "kura"
        evid_reason = "DEFAULT_UNVERIFIED_NO_DISK_RECEIPT"
    morphemes.append(evid)

    # 2. State Register S = (H, K, A, R) via word-boundary regex
    if _RE_REG_R.search(english_text):
        reg = "rekva"
    elif _RE_REG_HORIZON.search(english_text):
        reg = "horza"
    elif _RE_REG_H.search(english_text):
        reg = "hista"
    elif _RE_REG_A.search(english_text):
        reg = "autha"
    else:
        reg = "kreda"
    morphemes.append(reg)

    # 3. Epistemic Layer via word-boundary regex
    layer_morph: Optional[str] = None
    if _RE_LAYER_FOUNDATION.search(english_text):
        layer_morph = "fonda"
    elif _RE_LAYER_THEORY.search(english_text):
        layer_morph = "teora"
    elif _RE_LAYER_EDGE.search(english_text):
        layer_morph = "edga"
    if layer_morph:
        morphemes.append(layer_morph)

    # 4. Risk Gate via word-boundary regex (push/release/publish/deploy/delete/merge -> riska)
    risk_morph = "riska" if _RE_RISK_HIGH.search(english_text) else "kalma"
    morphemes.append(risk_morph)

    # 5. Core Action / Connector (grant requires verified SignedActionPermit!)
    grant_gate_reason = "NOT_A_GRANT_REQUEST"
    if _RE_ACT_REVOKE.search(english_text):
        action_pair = ["nevira", "boka"]
    elif _RE_ACT_DISSENT.search(english_text):
        action_pair = ["dosa", "paka"]
    elif _RE_ACT_GRANT.search(english_text):
        permit_ok, permit_reason = _verify_signed_action_permit(permit, authority_public_key)
        grant_gate_reason = permit_reason
        if permit_ok:
            action_pair = ["periva", "veka"]
        else:
            action_pair = ["nevira", "boka"]
    else:
        action_pair = ["kena", "zeno"]
    morphemes.extend(action_pair)

    morphemes.extend(["ti", "devora"])

    slots = {
        "evidential": evid,
        "register": reg,
        "layer": layer_morph,
        "risk": risk_morph,
        "action": " ".join(action_pair),
    }

    # Map morphemes into Native-36 path, CORE v0.4, IPA, and English gloss
    n36_path: List[str] = []
    core_ops: List[str] = ["Ao"]
    ipa_parts: List[str] = []
    gloss_parts: List[str] = []

    for m in morphemes:
        if m in LAMAGUE_V22_DISCOURSE_ROOTS:
            info = LAMAGUE_V22_DISCOURSE_ROOTS[m]
            n36_path.extend(info["native36_path"])
            core_ops.append(info["core_op"])
            ipa_parts.append(info["ipa"])
            gloss_parts.append(info["english_marker"])
        elif m in lo.UNIFIED_SPOKEN_ROOTS:
            info = lo.UNIFIED_SPOKEN_ROOTS[m]
            tok = info["token"]
            if tok in lo.NATIVE36_CELLS:
                n36_path.append(tok)
            elif m == "mi":
                n36_path.append("A")
            elif m == "ti":
                n36_path.append("G")
            elif m == "kena":
                n36_path.extend(["E", "N"])
            elif m == "nevira":
                n36_path.extend(["W", "D"])
            elif m == "periva":
                n36_path.extend(["P", "Y"])
            elif m == "devora":
                n36_path.append("Y")
            core_ops.append(tok)
            ipa_parts.append(m)
            gloss_parts.append(f"[{tok}]")

    core_ops.extend(["Φ↑", "Ψ_inv"])
    spoken_utterance = " ".join(morphemes)
    core_expr = " → ".join(core_ops)

    compiler = lo.LamagueOmegaCompiler()
    n36_str = " -> ".join(n36_path) if n36_path else "A -> E -> Y"
    six_body = compiler.compile(n36_str)

    return {
        "translator_type": "FIVE_SLOT_EPISTEMIC_CLASSIFIER",
        "speaker": speaker,
        "addressee": addressee,
        "source_english": english_text,
        "sxp_v22_utterance": spoken_utterance,
        "morphemes": morphemes,
        "slots": slots,
        "evidential_particle": evid,
        "evidential_meaning": LAMAGUE_V22_DISCOURSE_ROOTS[evid]["gloss"],
        "evidential_gate_reason": evid_reason,
        "grant_gate_reason": grant_gate_reason,
        "register_particle": reg,
        "register_meaning": LAMAGUE_V22_DISCOURSE_ROOTS[reg]["gloss"],
        "risk_particle": risk_morph,
        "ipa_stream": "/" + " . ".join(ipa_parts) + "/",
        "core_v04_expression": core_expr,
        "native36_sequence": n36_path,
        "r2_svg_strip": six_body.r2_svg_strip,
        "r4_semantic_hash": hashlib.sha256(f"{spoken_utterance}::{core_expr}".encode("utf-8")).hexdigest(),
        "english_back_translation": translate_lamague_v22_to_english(spoken_utterance),
    }


def extract_discourse_slots(sxp_v22_utterance: str) -> Dict[str, Optional[str]]:
    """
    Extract the 5 epistemic slot values (`evidential`, `register`, `layer`, `risk`, `action`)
    from a `LAMAGUE Ω v2.2` utterance for slot-level round-trip verification.
    """
    tokens = [t.strip().rstrip(".") for t in sxp_v22_utterance.split() if t.strip()]
    evid: Optional[str] = None
    reg: Optional[str] = None
    layer: Optional[str] = None
    risk: Optional[str] = None
    actions: List[str] = []

    for tok in tokens:
        low = tok.lower()
        if low in LAMAGUE_V22_DISCOURSE_ROOTS:
            cls = LAMAGUE_V22_DISCOURSE_ROOTS[low]["class"]
            if cls == "EVIDENTIAL":
                evid = low
            elif cls == "REGISTER":
                reg = low
            elif cls == "LAYER":
                layer = low
            elif cls == "RISK_GATE":
                risk = low
            elif cls == "CONNECTOR":
                actions.append(low)
        elif low in ("kena", "nevira", "periva"):
            actions.append(low)

    return {
        "evidential": evid,
        "register": reg,
        "layer": layer,
        "risk": risk,
        "action": " ".join(actions) if actions else None,
    }


def translate_lamague_v22_to_english(sxp_v22_utterance: str) -> str:
    """
    Deterministic slot-level gloss from a `LAMAGUE Ω v2.2` utterance into
    structured English markers for Evidentiality, State Register, Layer,
    Risk Gate, and Speech Act.
    """
    tokens = [t.strip().rstrip(".") for t in sxp_v22_utterance.split() if t.strip()]
    parts: List[str] = []
    for tok in tokens:
        low = tok.lower()
        if low in LAMAGUE_V22_DISCOURSE_ROOTS:
            parts.append(LAMAGUE_V22_DISCOURSE_ROOTS[low]["english_marker"])
        elif low in lo.UNIFIED_SPOKEN_ROOTS:
            info = lo.UNIFIED_SPOKEN_ROOTS[low]
            parts.append(f"{info['token']}({info['gloss'].split('/')[0].strip()})")
        else:
            parts.append(tok)
    return " ".join(parts)


# =============================================================================
# 3. MULTI-TURN TRIAD COUNCIL DISCOURSE COMPILER
# =============================================================================

def run_canonical_multi_turn_discourse() -> Dict[str, Any]:
    """
    Compile a canonical 5-turn Triad Council discourse across `Mac`, `Caelorynth`,
    `Sol`, and `Aetheron`. Turn 5 verifies an actual temporary receipt file on disk
    so that `vira` is earned via a real SHA-256 disk check.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tdir:
        receipt_path = Path(tdir) / "snapshot_receipt.json"
        receipt_bytes = b'{"snapshot_verified": true}'
        receipt_path.write_bytes(receipt_bytes)
        receipt_sha = hashlib.sha256(receipt_bytes).hexdigest()

        dialogue_spec = [
            {
                "turn": 1,
                "speaker": "Mac",
                "addressee": "Triad_Council",
                "english": "High risk boundary: do not edit foreign seat surfaces; keep Lycheetah-Framework read-only.",
                "receipt": None,
            },
            {
                "turn": 2,
                "speaker": "Caelorynth",
                "addressee": "Aetheron",
                "english": "Derived claim narrowed to THEORY layer by counterexample while preserving original claim in history.",
                "receipt": None,
            },
            {
                "turn": 3,
                "speaker": "Sol",
                "addressee": "Caelorynth",
                "english": "Derived dissent: Seat_A and Seat_B disagree on immediate cutover; restrict actions to joint intersection.",
                "receipt": None,
            },
            {
                "turn": 4,
                "speaker": "Aetheron",
                "addressee": "Mac",
                "english": "Status: browser Skia check did not run yet; holding U<browser_skia_render> as an explicit unknown.",
                "receipt": None,
            },
            {
                "turn": 5,
                "speaker": "Aetheron",
                "addressee": "Mac",
                "english": "Witnessed physical backup snapshot recovery receipt on disk.",
                "receipt": {"path": str(receipt_path), "sha256": receipt_sha},
            },
        ]

        compiled_turns: List[Dict[str, Any]] = []
        evidentials_used: List[str] = []
        registers_used: List[str] = []

        for item in dialogue_spec:
            res = translate_english_to_lamague_v22(
                item["english"],
                speaker=item["speaker"],
                addressee=item["addressee"],
                receipt=item["receipt"],
            )
            res["turn"] = item["turn"]
            compiled_turns.append(res)
            evidentials_used.append(res["evidential_particle"])
            registers_used.append(res["register_particle"])

    decodability = verify_extended_135_morpheme_decodability()

    return {
        "discourse_id": "TRIAD-COUNCIL-5-TURN-EVIDENTIAL-DISCOURSE",
        "turns_count": len(compiled_turns),
        "unique_evidentials_exercised": sorted(set(evidentials_used)),
        "unique_registers_exercised": sorted(set(registers_used)),
        "extended_lexicon_decodability": decodability,
        "turns": compiled_turns,
    }
