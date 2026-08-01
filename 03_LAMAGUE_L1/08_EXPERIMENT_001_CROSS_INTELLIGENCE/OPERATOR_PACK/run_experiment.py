from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lamague_runtime import BenchmarkRunner, ChallengePack, DecoderPacket

SUBMISSIONS = ROOT / "submissions"
REPORTS = ROOT / "reports"
REFERENCES = ROOT / "sealed_references"
COMMITMENTS = ROOT / "LAMAGUE_EXPERIMENT_001_REFERENCE_COMMITMENTS.json"


def canonical_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def verify_reference_commitments() -> list[dict[str, Any]]:
    doc = json.loads(COMMITMENTS.read_text(encoding="utf-8"))
    results = []
    for item in doc["reference_commitments"]:
        path = REFERENCES / f"{item['case_id']}__REFERENCE.json"
        packet = json.loads(path.read_text(encoding="utf-8"))
        file_hash = hashlib.sha256(canonical_json(packet)).hexdigest()
        ok = file_hash == item["reference_file_sha256"]
        results.append({
            "case_id": item["case_id"],
            "reference_file": str(path.relative_to(ROOT)),
            "expected_sha256": item["reference_file_sha256"],
            "actual_sha256": file_hash,
            "valid": ok,
        })
        if not ok:
            raise RuntimeError(
                f"Reference commitment failed for {item['case_id']}"
            )
    return results


def collect_packets() -> tuple[list[DecoderPacket], list[dict[str, Any]]]:
    packets = []
    invalid = []
    seen = set()

    for path in sorted(SUBMISSIONS.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            packet = DecoderPacket.from_dict(data)
            key = (packet.case_id, packet.decoder_id)
            if key in seen:
                raise ValueError(
                    f"Duplicate case/decoder pair: {packet.case_id}, {packet.decoder_id}"
                )
            seen.add(key)
            expected_prefix = packet.case_id + "__"
            if not path.name.startswith(expected_prefix):
                raise ValueError(
                    f"Filename must begin with {expected_prefix}"
                )
            packets.append(packet)
        except Exception as exc:
            invalid.append({
                "file": str(path.relative_to(ROOT)),
                "error": str(exc),
            })
    return packets, invalid


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    commitment_results = verify_reference_commitments()
    packets, invalid = collect_packets()
    pack = ChallengePack.load(ROOT / "challenge_pack.json")
    case_map = {case.case_id: case for case in pack.cases}

    grouped: dict[str, list[DecoderPacket]] = {case_id: [] for case_id in case_map}
    orphaned = []
    for packet in packets:
        if packet.case_id in grouped:
            grouped[packet.case_id].append(packet)
        else:
            orphaned.append({
                "decoder_id": packet.decoder_id,
                "case_id": packet.case_id,
                "error": "unknown case_id",
            })

    runner = BenchmarkRunner()
    results = []
    rows = []

    for case_id, case in case_map.items():
        result = runner.run_case(case, grouped[case_id])
        results.append(result)
        consensus = result["consensus"]
        for comparison in consensus["comparisons"]:
            rows.append({
                "case_id": case_id,
                "decoder_id": comparison["candidate_decoder"],
                "classification": comparison["classification"],
                "unsafe_losses": "|".join(comparison["unsafe_losses"]),
                "reference_hash": comparison["reference_hash"],
                "candidate_hash": comparison["candidate_hash"],
                "reference_critical_hash": comparison["reference_critical_hash"],
                "candidate_critical_hash": comparison["candidate_critical_hash"],
                "explanation": comparison["explanation"],
            })

    report = {
        "experiment_id": "LAMAGUE-EXP-001",
        "runtime": "LAMAGUE Runtime v0.3",
        "reference_commitments": commitment_results,
        "valid_packet_count": len(packets),
        "invalid_submissions": invalid,
        "orphaned_submissions": orphaned,
        "results": results,
    }

    json_path = REPORTS / "LAMAGUE_EXPERIMENT_001_RESULTS.json"
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    csv_path = REPORTS / "LAMAGUE_EXPERIMENT_001_RESULTS.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "case_id", "decoder_id", "classification", "unsafe_losses",
            "reference_hash", "candidate_hash",
            "reference_critical_hash", "candidate_critical_hash",
            "explanation",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary = [
        "# LAMAGUE Experiment 001 — Results",
        "",
        f"Valid decoder packets: **{len(packets)}**",
        f"Invalid submissions: **{len(invalid)}**",
        f"Unknown-case submissions: **{len(orphaned)}**",
        "",
    ]
    for result in results:
        case = result["case"]
        consensus = result["consensus"]
        summary.extend([
            f"## {case['case_id']} — {case['title']}",
            "",
            f"Consensus: **{consensus['status']}**",
            "",
            consensus["explanation"],
            "",
            f"Safe decoders: {', '.join(consensus['safe_decoders']) or 'none'}  ",
            f"Unsafe decoders: {', '.join(consensus['unsafe_decoders']) or 'none'}  ",
            f"Divergent decoders: {', '.join(consensus['divergent_decoders']) or 'none'}",
            "",
        ])
        for comparison in consensus["comparisons"]:
            summary.append(
                f"- `{comparison['candidate_decoder']}` → "
                f"**{comparison['classification']}**: "
                f"{comparison['explanation']}"
            )
        summary.append("")

    summary_path = REPORTS / "LAMAGUE_EXPERIMENT_001_RESULTS.md"
    summary_path.write_text("\n".join(summary), encoding="utf-8")

    invalid_path = REPORTS / "INVALID_SUBMISSIONS.json"
    invalid_path.write_text(
        json.dumps(invalid + orphaned, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(json.dumps({
        "experiment_id": "LAMAGUE-EXP-001",
        "valid_packet_count": len(packets),
        "invalid_count": len(invalid),
        "orphaned_count": len(orphaned),
        "json_report": str(json_path),
        "csv_report": str(csv_path),
        "markdown_report": str(summary_path),
    }, indent=2))


if __name__ == "__main__":
    main()
