"""Unique decodability of the spoken LAMAGUE inventories (review RV17, 2026-10-22).

The Sardinas-Patterson checker must refuse a known-bad code however late its
ambiguity surfaces, and its verdicts must agree with a constructive two-parse
search that shares no code with it.
"""
import heapq
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SPL = Path(__file__).resolve().parents[1] / "03_LAMAGUE_L1" / "23_SPOKEN_LAMAGUE"


def _load():
    spec = importlib.util.spec_from_file_location("spl_phonology_rv17", SPL / "spl_phonology.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phonology = _load()
REGISTRY = json.loads((SPL / "spl_registry_v0.1.json").read_text(encoding="utf-8"))


def two_parses(code, max_len=400):
    """Shortest string with two segmentations into `code`, or None (Dijkstra on length)."""
    code = sorted(set(code))
    heap = [(len(u), u[len(v):], (u,), (v,)) for u in code for v in code if u != v and u.startswith(v)]
    heapq.heapify(heap)
    done = set()
    while heap:
        n, rest, ahead, behind = heapq.heappop(heap)
        if n > max_len:
            return None
        if rest in done:
            continue
        done.add(rest)
        for w in code:
            if w == rest:
                return "".join(ahead), list(ahead), list(behind) + [w]
            if rest.startswith(w):
                heapq.heappush(heap, (n, rest[len(w):], ahead, behind + (w,)))
            elif w.startswith(rest):
                heapq.heappush(heap, (n + len(w) - len(rest), w[len(rest):], behind + (w,), ahead))
    return None


@pytest.mark.parametrize("n", [1, 10, 64, 65, 200])
def test_a_late_ambiguity_is_still_refused(n):
    code = {"0", "0" * n + "1", "1"}
    assert two_parses(code) is not None
    assert phonology.uniquely_decodable(code) == (False, "1")


@pytest.mark.parametrize("code, decodable", [
    ({"0", "10", "110"}, True),
    ({"0", "01", "11"}, True),
    ({"a", "ab", "bb"}, True),
    ({"a", "ba", "bb"}, True),
    ({"a", "ab", "b"}, False),
    ({"a", "c", "ad", "abb", "bad", "deb", "bbcde"}, False),
])
def test_controls_match_the_definition(code, decodable):
    assert phonology.uniquely_decodable(code)[0] is decodable
    assert (two_parses(code) is None) is decodable


def _inventories():
    n36 = REGISTRY["native36_spoken_forms"]
    native = set(n36["numerals"].values()) | set(n36["operators"].values())
    core = {f.replace("-", "") for f in REGISTRY["core_phonemes"] if not f.startswith("_")}
    merged = set(phonology.load_inventory(REGISTRY))
    return {
        "native36": (native, True),
        "core": (core, False),
        "core, sai-an as a compound": (core - {"saian"}, True),
        "merged": (merged, False),
        "merged, sai-an as a compound": (merged - {"saian"}, False),
    }


@pytest.mark.parametrize("name", list(_inventories()))
def test_inventory_verdicts_agree_with_the_constructive_search(name):
    code, decodable = _inventories()[name]
    assert phonology.uniquely_decodable(code)[0] is decodable
    assert (two_parses(code) is None) is decodable


def test_merging_is_ambiguous_even_with_the_compound_read_apart():
    code = set(phonology.load_inventory(REGISTRY)) - {"saian"}
    text, first, second = two_parses(code)
    assert "".join(first) == "".join(second) == text and first != second
