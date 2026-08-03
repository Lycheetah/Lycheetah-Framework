
from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

from lamague_codec import (
    build_codebook,
    canonical_bytes,
    canonical_json,
    classify,
    critical_hash,
    decode,
    encode,
    full_hash,
)

ROOT = Path(__file__).resolve().parents[1]


def load_packets():
    packets = []
    with (ROOT / "corpus" / "packets.jsonl").open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                packets.append(json.loads(line))
    split = json.loads((ROOT / "corpus" / "split.json").read_text(encoding="utf-8"))
    train = [packet for packet in packets if packet["id"] in set(split["training"])]
    heldout = [packet for packet in packets if packet["id"] in set(split["heldout"])]
    return packets, train, heldout, split


def mutate(packet, kind):
    candidate = copy.deepcopy(packet)
    if kind == "DROP_UNKNOWNS":
        candidate["unknowns"] = []
    elif kind == "UNPROTECT_UNKNOWN":
        candidate["unknowns"][0]["protected"] = False
    elif kind == "DROP_AUTHORITY":
        candidate["authority"] = []
    elif kind == "DROP_AFFECTED_PARTIES":
        candidate["affectedParties"] = []
    elif kind == "DROP_DISSENT":
        candidate["dissent"] = []
    elif kind == "DROP_VALUE_FLOW":
        candidate["valueFlow"] = []
    elif kind == "DROP_RECOVERY":
        candidate["recovery"] = []
    elif kind == "CHANGE_INVARIANT":
        candidate["invariants"][0]["text"] += " Altered."
    elif kind == "REMOVE_GUARD_OPERATION":
        candidate["operations"] = [op for op in candidate["operations"] if op != "G"]
    else:
        raise ValueError(kind)
    return candidate


def cumulative_break_even(reference_sizes, candidate_sizes, one_time_cost):
    reference_total = 0
    candidate_total = one_time_cost
    for index, (reference, candidate) in enumerate(zip(reference_sizes, candidate_sizes), start=1):
        reference_total += reference
        candidate_total += candidate
        if candidate_total <= reference_total:
            return index
    return None


def ratio(baseline, encoded):
    return 1.0 - encoded / baseline


def run():
    packets, train, heldout, split = load_packets()
    codebook = build_codebook(train, max_entries=20)
    (ROOT / "corpus" / "codebook.json").write_text(
        json.dumps(codebook, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    codebook_wire_bytes = len(canonical_bytes(codebook))

    rows = []
    exact_roundtrips = 0
    critical_roundtrips = 0
    for packet in packets:
        baseline = len(canonical_bytes(packet))
        plain_source = encode(packet)
        dictionary_source = encode(packet, codebook)
        plain_decoded = decode(plain_source)
        dictionary_decoded = decode(dictionary_source, codebook)

        full_equal = full_hash(packet) == full_hash(dictionary_decoded)
        critical_equal = critical_hash(packet) == critical_hash(dictionary_decoded)
        exact_roundtrips += int(full_equal)
        critical_roundtrips += int(critical_equal)

        rows.append(
            {
                "id": packet["id"],
                "split": "training" if packet["id"] in set(split["training"]) else "heldout",
                "baseline_minified_json_bytes": baseline,
                "l1_bytes": len(plain_source.encode("utf-8")),
                "l1d_bytes": len(dictionary_source.encode("utf-8")),
                "l1_reduction": ratio(baseline, len(plain_source.encode("utf-8"))),
                "l1d_warm_reduction": ratio(baseline, len(dictionary_source.encode("utf-8"))),
                "full_hash_equal": full_equal,
                "critical_hash_equal": critical_equal,
            }
        )

        if canonical_json(packet) != canonical_json(plain_decoded):
            raise AssertionError(f"plain round-trip failed for {packet['id']}")
        if canonical_json(packet) != canonical_json(dictionary_decoded):
            raise AssertionError(f"dictionary round-trip failed for {packet['id']}")

    mutation_kinds = [
        "DROP_UNKNOWNS",
        "UNPROTECT_UNKNOWN",
        "DROP_AUTHORITY",
        "DROP_AFFECTED_PARTIES",
        "DROP_DISSENT",
        "DROP_VALUE_FLOW",
        "DROP_RECOVERY",
        "CHANGE_INVARIANT",
        "REMOVE_GUARD_OPERATION",
    ]

    mutation_rows = []
    detected = 0
    for packet in packets:
        for mutation_kind in mutation_kinds:
            candidate = mutate(packet, mutation_kind)
            result = classify(packet, candidate)
            expected = "DIVERGENT" if mutation_kind == "CHANGE_INVARIANT" else "UNSAFE_COLLAPSE"
            matched = result["classification"] == expected
            detected += int(matched)
            mutation_rows.append(
                {
                    "packet_id": packet["id"],
                    "mutation": mutation_kind,
                    "expected": expected,
                    "actual": result["classification"],
                    "matched": matched,
                    "details": result,
                }
            )

    safe_extensions = 0
    for packet in packets:
        candidate = copy.deepcopy(packet)
        candidate["evidence"].append(
            {
                "id": "e_extension",
                "text": "Additional evidence retained without altering protected fields.",
                "provenance": f"source://{packet['id']}/extension",
            }
        )
        result = classify(packet, candidate)
        safe_extensions += int(result["classification"] == "PARTIAL_EQUIVALENT")

    training_rows = [row for row in rows if row["split"] == "training"]
    heldout_rows = [row for row in rows if row["split"] == "heldout"]

    def totals(selected):
        return {
            "packets": len(selected),
            "baseline_bytes": sum(row["baseline_minified_json_bytes"] for row in selected),
            "l1_bytes": sum(row["l1_bytes"] for row in selected),
            "l1d_bytes": sum(row["l1d_bytes"] for row in selected),
        }

    all_totals = totals(rows)
    train_totals = totals(training_rows)
    heldout_totals = totals(heldout_rows)

    heldout_l1 = [row["l1_bytes"] for row in heldout_rows]
    heldout_l1d = [row["l1d_bytes"] for row in heldout_rows]
    heldout_baseline = [row["baseline_minified_json_bytes"] for row in heldout_rows]

    report = {
        "schema": "LAMAGUE-REVERSIBLE-COMPRESSION-BENCHMARK-1",
        "corpus": {
            "total_packets": len(packets),
            "training_packets": len(train),
            "heldout_packets": len(heldout),
            "domains": len(packets) // 2,
            "synthetic": True,
            "frozen_before_benchmark": True,
        },
        "codebook": {
            "trained_on": "training split only",
            "entries": len(codebook["entries"]),
            "wire_bytes": codebook_wire_bytes,
            "entries_list": codebook["entries"],
        },
        "roundtrip": {
            "exact_full_packet": exact_roundtrips,
            "critical_hash_preserved": critical_roundtrips,
            "total": len(packets),
        },
        "mutation_detection": {
            "mutation_types": len(mutation_kinds),
            "cases": len(mutation_rows),
            "matched_expected_class": detected,
            "accuracy_on_constructed_mutations": detected / len(mutation_rows),
            "safe_extension_cases": len(packets),
            "safe_extensions_correctly_partial": safe_extensions,
        },
        "sizes": {
            "all": all_totals,
            "training": train_totals,
            "heldout": heldout_totals,
        },
        "compression": {
            "all_l1_reduction_vs_minified_json": ratio(all_totals["baseline_bytes"], all_totals["l1_bytes"]),
            "all_l1d_warm_reduction_vs_minified_json": ratio(all_totals["baseline_bytes"], all_totals["l1d_bytes"]),
            "all_l1d_cold_reduction_including_codebook": ratio(
                all_totals["baseline_bytes"], all_totals["l1d_bytes"] + codebook_wire_bytes
            ),
            "heldout_l1_reduction_vs_minified_json": ratio(
                heldout_totals["baseline_bytes"], heldout_totals["l1_bytes"]
            ),
            "heldout_l1d_warm_reduction_vs_minified_json": ratio(
                heldout_totals["baseline_bytes"], heldout_totals["l1d_bytes"]
            ),
            "heldout_l1d_cold_reduction_including_codebook": ratio(
                heldout_totals["baseline_bytes"], heldout_totals["l1d_bytes"] + codebook_wire_bytes
            ),
            "heldout_dictionary_break_even_vs_l1_packets": cumulative_break_even(
                heldout_l1, heldout_l1d, codebook_wire_bytes
            ),
            "heldout_dictionary_break_even_vs_minified_json_packets": cumulative_break_even(
                heldout_baseline, heldout_l1d, codebook_wire_bytes
            ),
            "heldout_min_l1d_warm_reduction": min(row["l1d_warm_reduction"] for row in heldout_rows),
            "heldout_max_l1d_warm_reduction": max(row["l1d_warm_reduction"] for row in heldout_rows),
        },
        "boundaries": [
            "The corpus is synthetic and structured.",
            "The codec does not infer semantic packets from unrestricted natural language.",
            "Exact round-trip demonstrates software fidelity under the declared schema, not universal semantic equivalence.",
            "Mutation accuracy is measured on constructed protected-field deletions, not adversarial external model outputs.",
            "Compression is measured against canonical minified JSON in UTF-8 bytes.",
            "The dictionary was learned only from the training split.",
        ],
    }

    (ROOT / "reports" / "benchmark_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with (ROOT / "reports" / "packet_sizes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with (ROOT / "reports" / "mutation_results.jsonl").open("w", encoding="utf-8") as handle:
        for row in mutation_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    sample = packets[-1]
    sample_source = encode(sample, codebook)
    sample_decoded = decode(sample_source, codebook)
    (ROOT / "reports" / "sample_roundtrip.json").write_text(
        json.dumps(
            {
                "source_packet": sample,
                "compressed": sample_source,
                "decoded_packet": sample_decoded,
                "full_hash_before": full_hash(sample),
                "full_hash_after": full_hash(sample_decoded),
                "critical_hash_before": critical_hash(sample),
                "critical_hash_after": critical_hash(sample_decoded),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return report


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
