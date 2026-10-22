"""RV37 reproductions: Hexie marginal claim, ResearchPipeline single-study FOUNDATION, TitleReceipt EARNED."""
import importlib.util, json, sys
from pathlib import Path
R = str(Path(__file__).resolve().parents[2]) + "/"
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, R + path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

print("== L4 Hexie")
hx = load("hx", "32_TIANXIA/implementations/hexie_five_fold.py")
s = hx.HexieState(0.28, 0.72, 0.81, 0.76, 0.69, "G_A")
base = hx.hexie_five_fold(s)[5]
names = ["innovation", "coordination", "ecological", "openness", "sharing"]
for i, n in enumerate(names):
    v = [s.innovation, s.coordination, s.ecological, s.openness, s.sharing]; v[i] += 0.05
    print(f"  +0.05 on {n:13s} -> dH5 = {hx.hexie_five_fold(hx.HexieState(*v))[5]-base:+.4f}")
tie = hx.HexieState(0.5, 0.9, 0.5, 0.9, 0.9)
print("  tie I=E=0.5 -> binding_constraint:", hx.binding_constraint(tie), "(claim: unique)")

print("== L2 ResearchPipeline")
rp = load("rp", "14_MYSTERY_SCHOOL/implementations/research_pipeline.py")
db = rp.load_example_data()
for name, ev in db.practices.items():
    print(f"  example {name:30s} Pi={ev.calculate_truth_pressure():.3f} layer={ev.get_layer_recommendation()} n_studies={len(ev.studies)}")
one = rp.PracticeEvidence("X")
one.add_study(rp.ResearchStudy("X", 0.15, 200, 0.04, rp.StudyType.RCT, rp.QualityRating.HIGH, 2020, "single"))
print(f"  single RCT d=0.15 n=200 p=.04 HIGH: Pi={one.calculate_truth_pressure():.3f} -> {one.get_layer_recommendation()}")
for kind in (rp.StudyType.RCT, rp.StudyType.CASE_STUDY):
    e = rp.PracticeEvidence("X")
    e.add_study(rp.ResearchStudy("X", 0.16, 200, 0.04, kind, rp.QualityRating.HIGH, 2020, "single"))
    print(f"  single {kind.name:10s} d=0.16 n=200 p=.04 HIGH: Pi={e.calculate_truth_pressure():.3f} -> {e.get_layer_recommendation()} (FOUNDATION before the RV37 cap)")
for d2 in (0.16, 0.30):
    e = rp.PracticeEvidence("X")
    e.add_study(rp.ResearchStudy("X", 0.16, 200, 0.04, rp.StudyType.RCT, rp.QualityRating.HIGH, 2020, "first"))
    e.add_study(rp.ResearchStudy("X", d2, 200, 0.01, rp.StudyType.RCT, rp.QualityRating.HIGH, 2021, "replication"))
    print(f"  d=0.16 + replication d={d2:.2f}:           Pi={e.calculate_truth_pressure():.3f} -> {e.get_layer_recommendation()} (consistency is range-based)")
two = rp.PracticeEvidence("X")
two.add_study(rp.ResearchStudy("X", 0.15, 200, 0.04, rp.StudyType.RCT, rp.QualityRating.HIGH, 2020, "single"))
two.add_study(rp.ResearchStudy("X", 0.30, 200, 0.01, rp.StudyType.RCT, rp.QualityRating.HIGH, 2021, "replication, larger effect"))
print(f"  + a stronger replication d=0.30:   Pi={two.calculate_truth_pressure():.3f} -> {two.get_layer_recommendation()}")
big = rp.PracticeEvidence("Y")
big.add_study(rp.ResearchStudy("Y", 0.9, 30, 0.04, rp.StudyType.CASE_STUDY, rp.QualityRating.HIGH, 2020, "case study rated HIGH"))
print(f"  CASE_STUDY rated HIGH d=0.9 n=30: Pi={big.calculate_truth_pressure():.3f} -> {big.get_layer_recommendation()} (study_type unused in Pi)")

print("== L3 TitleReceipt")
import jsonschema
src = R + "14_MYSTERY_SCHOOL/IDENTITY_AND_RETURN/source/"
schema = json.load(open(src + "title_receipt.schema.json"))
V = jsonschema.Draft202012Validator(schema)
bad = {"receipt_version": "lycheetah.title-receipt.v0.1", "title_name": "T", "title_definition_version": "0.1",
       "state": "EARNED", "bearer_choice": False, "boundary": "b"}
print("  EARNED, bearer_choice=false, no gate/evidence/witness: errors =", len(list(V.iter_errors(bad))))
bad2 = dict(bad, witness_type="NONE", gate_id=None, evidence_uri=None)
print("  same + witness NONE, gate null, evidence null:        errors =", len(list(V.iter_errors(bad2))))
tm = dict(bad, state="TRANSMUTED")
print("  TRANSMUTED with bearer_choice=false:                  errors =", len(list(V.iter_errors(tm))))
ctrl = dict(bad, state="MASTER")
print("  control: unknown state MASTER:                        errors =", len(list(V.iter_errors(ctrl))))
ex = json.load(open(src + "examples.json"))
print("  examples.json entries:", [ (e.get("state"), e.get("bearer_choice"), e.get("gate_id"), e.get("witness_type")) if isinstance(e, dict) else type(e).__name__ for e in ex])
