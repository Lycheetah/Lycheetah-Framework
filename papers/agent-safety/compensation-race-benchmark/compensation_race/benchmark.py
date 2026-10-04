from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from contextlib import closing
import json
import sqlite3
import tempfile
from typing import Iterable


def digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ResourceFence:
    resource_id: str
    expected_version: int
    expected_hash: str
    restore_value: str


@dataclass(frozen=True)
class RepairPermit:
    effect_id: str
    fences: tuple[ResourceFence, ...]


class ResourceStore:
    """Tiny SQLite-backed resource owner used only for the public race benchmark."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        with closing(self.connect()) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                "CREATE TABLE IF NOT EXISTS resources ("
                "id TEXT PRIMARY KEY, value TEXT NOT NULL, version INTEGER NOT NULL, digest TEXT NOT NULL)"
            )

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5.0, isolation_level=None)
        db.row_factory = sqlite3.Row
        return db

    def reset(self) -> RepairPermit:
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM resources")
            # v1 = pre-effect state, v2 = target effect's post-state.
            for rid, val in (("A", "A_bad"), ("B", "B_bad")):
                db.execute(
                    "INSERT INTO resources(id,value,version,digest) VALUES(?,?,?,?)",
                    (rid, val, 2, digest(val)),
                )
            db.commit()
        return RepairPermit(
            effect_id="effect-1",
            fences=(
                ResourceFence("A", 2, digest("A_bad"), "A_original"),
                ResourceFence("B", 2, digest("B_bad"), "B_original"),
            ),
        )

    def snapshot(self) -> dict[str, dict]:
        with closing(self.connect()) as db:
            rows = db.execute("SELECT id,value,version,digest FROM resources ORDER BY id").fetchall()
        return {r["id"]: dict(r) for r in rows}

    def legitimate_update(self, resource_id: str, new_value: str) -> None:
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT version FROM resources WHERE id=?", (resource_id,)
            ).fetchone()
            if row is None:
                raise KeyError(resource_id)
            db.execute(
                "UPDATE resources SET value=?, version=?, digest=? WHERE id=?",
                (new_value, int(row["version"]) + 1, digest(new_value), resource_id),
            )
            db.commit()

    def precheck(self, permit: RepairPermit) -> bool:
        current = self.snapshot()
        return all(
            current[f.resource_id]["version"] == f.expected_version
            and current[f.resource_id]["digest"] == f.expected_hash
            for f in permit.fences
        )

    def weak_precheck_then_write(self, permit: RepairPermit, *, already_prechecked: bool) -> bool:
        """Intentionally weak: trusts an earlier precheck and blindly writes later."""
        if not already_prechecked:
            return False
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            for f in permit.fences:
                row = db.execute(
                    "SELECT version FROM resources WHERE id=?", (f.resource_id,)
                ).fetchone()
                db.execute(
                    "UPDATE resources SET value=?, version=?, digest=? WHERE id=?",
                    (f.restore_value, int(row["version"]) + 1, digest(f.restore_value), f.resource_id),
                )
            db.commit()
        return True

    def sequential_per_item_cas(self, permit: RepairPermit) -> tuple[bool, tuple[str, ...]]:
        """Intentionally weak: checks+writes each resource separately, allowing partial repair."""
        repaired: list[str] = []
        for f in permit.fences:
            with closing(self.connect()) as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT version,digest FROM resources WHERE id=?", (f.resource_id,)
                ).fetchone()
                if row["version"] != f.expected_version or row["digest"] != f.expected_hash:
                    db.rollback()
                    return False, tuple(repaired)
                db.execute(
                    "UPDATE resources SET value=?, version=?, digest=? WHERE id=?",
                    (f.restore_value, f.expected_version + 1, digest(f.restore_value), f.resource_id),
                )
                db.commit()
                repaired.append(f.resource_id)
        return True, tuple(repaired)

    def atomic_commit_fenced(self, permit: RepairPermit) -> bool:
        """Strong baseline: validate every target and apply every restore in one write transaction."""
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            rows = {}
            for f in permit.fences:
                row = db.execute(
                    "SELECT version,digest FROM resources WHERE id=?", (f.resource_id,)
                ).fetchone()
                if row is None:
                    db.rollback()
                    return False
                rows[f.resource_id] = row
            if not all(
                rows[f.resource_id]["version"] == f.expected_version
                and rows[f.resource_id]["digest"] == f.expected_hash
                for f in permit.fences
            ):
                db.rollback()
                return False
            for f in permit.fences:
                db.execute(
                    "UPDATE resources SET value=?, version=?, digest=? WHERE id=?",
                    (f.restore_value, f.expected_version + 1, digest(f.restore_value), f.resource_id),
                )
            db.commit()
        return True


def _new_store() -> tuple[tempfile.TemporaryDirectory, ResourceStore, RepairPermit]:
    td = tempfile.TemporaryDirectory(prefix="lycheetah-comp-race-")
    store = ResourceStore(Path(td.name) / "race.sqlite3")
    permit = store.reset()
    return td, store, permit


def run_case(case: str) -> dict:
    td, store, permit = _new_store()
    try:
        if case == "weak_precheck_race":
            precheck = store.precheck(permit)
            store.legitimate_update("B", "B_legit_after_permit")
            committed = store.weak_precheck_then_write(permit, already_prechecked=precheck)
            snap = store.snapshot()
            return {
                "case": case,
                "precheck_passed": precheck,
                "repair_reported_success": committed,
                "final": snap,
                "overwrote_legitimate_update": snap["B"]["value"] == "B_original",
            }

        if case == "sequential_partial":
            # Make B stale before repair. A still matches and gets repaired first.
            store.legitimate_update("B", "B_legit_before_repair")
            committed, repaired = store.sequential_per_item_cas(permit)
            snap = store.snapshot()
            return {
                "case": case,
                "repair_reported_success": committed,
                "repaired_before_failure": list(repaired),
                "final": snap,
                "partial_repair": (snap["A"]["value"] == "A_original" and snap["B"]["value"] == "B_legit_before_repair"),
            }

        if case == "atomic_stale_refusal":
            store.legitimate_update("B", "B_legit_after_permit")
            committed = store.atomic_commit_fenced(permit)
            snap = store.snapshot()
            return {
                "case": case,
                "repair_committed": committed,
                "final": snap,
                "writes_zero": snap["A"]["value"] == "A_bad" and snap["B"]["value"] == "B_legit_after_permit",
            }

        if case == "atomic_clean":
            committed = store.atomic_commit_fenced(permit)
            snap = store.snapshot()
            return {
                "case": case,
                "repair_committed": committed,
                "final": snap,
                "both_restored": snap["A"]["value"] == "A_original" and snap["B"]["value"] == "B_original",
            }
        raise ValueError(f"unknown case: {case}")
    finally:
        td.cleanup()


def run_stress(rounds: int = 1000) -> dict:
    counts = {
        "weak_precheck_overwrites": 0,
        "sequential_partial_repairs": 0,
        "atomic_stale_refusals": 0,
        "atomic_partial_repairs": 0,
        "atomic_clean_successes": 0,
    }
    for _ in range(rounds):
        weak = run_case("weak_precheck_race")
        counts["weak_precheck_overwrites"] += int(weak["overwrote_legitimate_update"])

        seq = run_case("sequential_partial")
        counts["sequential_partial_repairs"] += int(seq["partial_repair"])

        stale = run_case("atomic_stale_refusal")
        counts["atomic_stale_refusals"] += int((not stale["repair_committed"]) and stale["writes_zero"])
        snap = stale["final"]
        partial = (snap["A"]["value"] == "A_original") != (snap["B"]["value"] == "B_original")
        counts["atomic_partial_repairs"] += int(partial)

        clean = run_case("atomic_clean")
        counts["atomic_clean_successes"] += int(clean["repair_committed"] and clean["both_restored"])

    return {
        "version": "lycheetah-compensation-race-benchmark/0.1",
        "rounds_per_case": rounds,
        **counts,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=1000)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run_stress(args.rounds)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
