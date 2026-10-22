"""One file, one module: the package's exported names are the implementation's own (RV01).

  [ACTIVE]  A PASS on an AURA report compares equal to ``lycheetah.core.MetricStatus.PASS``.
  [ACTIVE]  ``lycheetah.core`` / ``lycheetah.applications`` re-export the canonical classes.
  [ACTIVE]  The assurance runtime builds the same extractor type the analyser imports.

Importing ``lycheetah.core.<module>`` by its full dotted name still loads a second copy in a
source checkout. That is recorded in the RV01 ledger as an open consolidation item, not
asserted here.
"""

import sys

import lycheetah.applications as package_applications
import lycheetah.assurance.runtime as runtime
import lycheetah.core as package_core


def test_report_status_equals_the_exported_enum():
    report = package_applications.AURATextAnalyser().analyse(
        "We measured the effect in two trials and report the uncertainty plainly."
    )
    for status in (report.tes_status, report.vtr_status, report.pai_status):
        assert isinstance(status, package_core.MetricStatus)
        assert status == package_core.MetricStatus[status.name]


def test_exported_names_are_the_canonical_classes():
    tri_axial = sys.modules["core.tri_axial_checker"]
    extractor = sys.modules["core.semantic_extractor"]
    aura = sys.modules["applications.aura_text_checker"]
    assert package_core.MetricStatus is tri_axial.MetricStatus
    assert package_core.TriAxialChecker is tri_axial.TriAxialChecker
    assert package_core.SemanticExtractor is extractor.SemanticExtractor
    assert package_applications.AURATextAnalyser is aura.AURATextAnalyser


def test_runtime_uses_the_analysers_extractor_type():
    assert runtime.SemanticExtractor is sys.modules["core.semantic_extractor"].SemanticExtractor
    assert runtime.AURATextAnalyser is sys.modules["applications.aura_text_checker"].AURATextAnalyser
