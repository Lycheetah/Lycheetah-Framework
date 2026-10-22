"""Layer assignment in the Mystery School research pipeline (RV37).

  [ACTIVE]  One HIGH-rated study cannot reach FOUNDATION on its Π alone.
  [ACTIVE]  Uncontrolled designs cannot reach FOUNDATION, however high their Π.
  [ACTIVE]  Replicated controlled evidence (the worked CBT example) still does.
"""

import importlib.util
import os
import sys

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                     "14_MYSTERY_SCHOOL", "implementations", "research_pipeline.py")
_spec = importlib.util.spec_from_file_location("research_pipeline", _PATH)
rp = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("research_pipeline", rp)
_spec.loader.exec_module(rp)


def _evidence(*studies):
    ev = rp.PracticeEvidence("X")
    for d, n, p, kind in studies:
        ev.add_study(rp.ResearchStudy("X", d, n, p, kind, rp.QualityRating.HIGH, 2020, "test"))
    return ev


def test_single_high_study_is_capped_at_middle():
    ev = _evidence((0.16, 200, 0.04, rp.StudyType.RCT))
    assert ev.calculate_truth_pressure() >= 1.5
    assert ev.get_layer_recommendation() == "MIDDLE"


def test_uncontrolled_designs_are_capped_at_middle():
    ev = _evidence((0.5, 200, 0.01, rp.StudyType.CASE_STUDY),
                   (0.5, 200, 0.01, rp.StudyType.OBSERVATIONAL))
    assert ev.calculate_truth_pressure() >= 1.5
    assert ev.get_layer_recommendation() == "MIDDLE"


def test_replicated_controlled_evidence_reaches_foundation():
    cbt = rp.load_example_data().get_practice("Cognitive Behavioral Therapy")
    assert cbt.get_layer_recommendation() == "FOUNDATION"
