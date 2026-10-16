#!/usr/bin/env python3
"""Prepare anonymised evaluator pack and a separate private method-mapping key."""
from __future__ import annotations
import argparse, hashlib, json, secrets
from pathlib import Path

LEAK_TERMS = {
    "ordinary_baseline": ["ordinary analysis", "conventional baseline", "arm a"],
    "structured_ledger": ["structured evidence ledger", "arm b", "evidence-ledger condition"],
    "anon_politician": ["anon politician", "cascade workflow", "arm c", "policy lab workflow"],
}


def prepare(data: dict, seed: int | None = None) -> tuple[dict, dict]:
    methods = data.get("methods", [])
    if len(methods) != 3:
        raise ValueError("Exactly three method records are required for this protocol.")
    ids = [m.get("method_id") for m in methods]
    expected = {"ordinary_baseline", "structured_ledger", "anon_politician"}
    if set(ids) != expected or len(ids) != len(set(ids)):
        raise ValueError(f"methods must be exactly: {sorted(expected)}")
    for m in methods:
        text = m.get("analysis_text", "")
        if not isinstance(text, str) or not text.strip() or text.startswith("PASTE "):
            raise ValueError(f"Missing analysis_text for {m.get('method_id')}")
    # Deterministic PRNG only for tests or reproducibility exercises; use cryptographic shuffle by default.
    aliases = ["A", "B", "C"]
    if seed is None:
        secrets.SystemRandom().shuffle(aliases)
    else:
        import random
        random.Random(seed).shuffle(aliases)
    mapping = dict(zip(ids, aliases))
    alias_to_method = {alias: method_id for method_id, alias in mapping.items()}
    methods_by_id = {m["method_id"]: m for m in methods}
    pack_methods = []
    leakage = []
    for alias in aliases:
        method_id = alias_to_method[alias]
        m = methods_by_id[method_id]
        pack_methods.append({"candidate_id": alias, "analysis_text": m["analysis_text"]})
        lower = m["analysis_text"].lower()
        terms = LEAK_TERMS.get(method_id, [])
        hits = [term for term in terms if term in lower]
        if hits:
            leakage.append({"method_id": method_id, "candidate_id": alias, "terms": hits})
    # Keep reference context but remove run metadata and original method IDs/labels.
    blind_pack = {
        "experiment_id": data.get("experiment_id", "AP-EVAL-UNSPECIFIED"),
        "case_id": data.get("case_id", "UNSPECIFIED"),
        "policy_question": data.get("policy_question", ""),
        "source_packet_sha256": data.get("source_packet_sha256", ""),
        "source_cutoff": data.get("source_cutoff", ""),
        "reference_context": data.get("reference_context", {}),
        "review_instruction": "Review the three candidates as anonymous outputs A, B and C. Do not infer which workflow produced them; assess the analysis against the same reference context. Do not choose a preferred policy or political party. Rate each dimension separately and document material issues with examples.",
        "candidates": sorted(pack_methods, key=lambda x: x["candidate_id"]),
    }
    identity_payload = {
        "experiment_id": blind_pack["experiment_id"],
        "case_id": blind_pack["case_id"],
        "policy_question": blind_pack["policy_question"],
        "source_packet_sha256": blind_pack["source_packet_sha256"],
        "candidates": blind_pack["candidates"],
    }
    blind_pack_id = "APB-" + hashlib.sha256(json.dumps(identity_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12].upper()
    blind_pack["blind_pack_id"] = blind_pack_id
    pack_bytes = json.dumps(blind_pack, ensure_ascii=False, sort_keys=True).encode("utf-8")
    key = {
        "experiment_id": blind_pack["experiment_id"],
        "blind_pack_id": blind_pack_id,
        "mapping": {alias: alias_to_method[alias] for alias in sorted(alias_to_method)},
        "source_packet_sha256": blind_pack["source_packet_sha256"],
        "blind_pack_sha256": hashlib.sha256(pack_bytes).hexdigest(),
        "possible_blinding_leaks": leakage,
        "warning": "PRIVATE. Do not give this file to evaluators until their ratings are locked. Leakage flags are prompts for coordinator review, not proof that unblinding occurred. Do not silently change only one candidate's wording.",
    }
    return blind_pack, key


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input_json", type=Path)
    p.add_argument("--out-dir", type=Path, default=Path("blind_output"))
    p.add_argument("--seed", type=int, default=None, help="Only for a reproducibility exercise; omit for random assignment")
    args = p.parse_args()
    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    pack, key = prepare(data, args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "blind_review_pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out_dir / "PRIVATE_method_mapping_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote blind pack: {args.out_dir / 'blind_review_pack.json'}")
    print(f"Wrote PRIVATE key: {args.out_dir / 'PRIVATE_method_mapping_key.json'}")
    if key["possible_blinding_leaks"]:
        print("WARNING: possible method-identifying language found; inspect output before issuing blind pack.")
    else:
        print("No configured method-name leak terms found. This does not guarantee full blinding.")

if __name__ == "__main__":
    main()
