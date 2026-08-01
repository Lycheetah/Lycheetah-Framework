import json
import unittest
from pathlib import Path

from lamague_native import (
    parse_source,
    compile_program,
    NativeSyntaxError,
    NativeCompileError,
)


ROOT = Path(__file__).resolve().parents[1]


class NativeParserTests(unittest.TestCase):
    def test_required_header(self):
        with self.assertRaises(NativeSyntaxError):
            parse_source("packet X;")

    def test_missing_semicolon(self):
        with self.assertRaises(NativeSyntaxError):
            parse_source("packet X; observability WHITE_BOX")

    def test_unknown_keyword(self):
        with self.assertRaises(NativeSyntaxError):
            parse_source(
                "packet X; observability WHITE_BOX; summon light;"
            )

    def test_source_hash_deterministic(self):
        source = "packet X; observability WHITE_BOX; analyze;"
        self.assertEqual(
            parse_source(source).source_hash,
            parse_source(source).source_hash,
        )

    def test_legacy_glyph_warning(self):
        program = parse_source(
            'packet X; observability WHITE_BOX; block "∆";'
        )
        self.assertEqual(program.warnings[0]["code"], "LEGACY_GLYPH")


class NativeCompileTests(unittest.TestCase):
    def test_tim_example(self):
        source = (ROOT / "examples" / "tim_native_conflict.lmg").read_text(
            encoding="utf-8"
        )
        result = compile_program(parse_source(source))
        self.assertEqual(result.analysis["status"], "CRITICAL")
        self.assertAlmostEqual(result.analysis["mu_drift"], 0.6)
        self.assertAlmostEqual(result.analysis["rho_drift"], 0.3)
        self.assertEqual(result.analysis["rho_recovery"], 0.0)
        self.assertIn(
            "silent_branch_selection",
            result.analysis["blocked_calculations"],
        )
        branches = {
            x["branch_id"]: x
            for x in result.analysis["evidence_branches"]
        }
        self.assertEqual(branches["printed_operator"]["operator"], "≥")
        self.assertEqual(branches["canonical_operator"]["operator"], "≤")

    def test_recovery_example(self):
        source = (
            ROOT / "examples" / "microorcim_native_recovery.lmg"
        ).read_text(encoding="utf-8")
        result = compile_program(parse_source(source))
        self.assertEqual(result.analysis["rho_recovery"], 1.0)
        self.assertEqual(result.analysis["rho_recovery_status"], "VALID")

    def test_missing_intent(self):
        source = (
            ROOT / "examples" / "missing_intent_native.lmg"
        ).read_text(encoding="utf-8")
        result = compile_program(parse_source(source))
        self.assertEqual(result.analysis["status"], "INSUFFICIENT")
        self.assertIsNone(result.analysis["mu_drift"])
        self.assertIn(
            "drift_metrics_missing_intent_action_pair",
            result.analysis["blocked_calculations"],
        )

    def test_black_box_scope(self):
        source = (ROOT / "examples" / "black_box_native.lmg").read_text(
            encoding="utf-8"
        )
        result = compile_program(parse_source(source))
        self.assertEqual(
            result.analysis["permitted_interpretation"],
            "behavioral anomaly signal only",
        )
        self.assertIn(
            "alignment_claim", result.analysis["blocked_calculations"]
        )

    def test_distinct_provenance(self):
        source = """
        packet P;
        observability WHITE_BOX;
        observe a key="x" value=7;
        declare b key="x" value=7;
        preserve a;
        preserve b;
        analyze;
        """
        result = compile_program(parse_source(source))
        provenance = [
            x["provenance"]
            for x in result.analysis["evidence_branches"]
        ]
        self.assertEqual(provenance, ["OBSERVED", "DECLARED"])

    def test_auto_unit_conflict(self):
        source = """
        packet U;
        observability WHITE_BOX;
        observe a key="distance" value=1 unit="m";
        declare b key="distance" value=1 unit="cm";
        preserve a;
        preserve b;
        analyze;
        """
        result = compile_program(parse_source(source))
        self.assertIn(
            "UNIT", result.analysis["conflicts"][0]["dimensions"]
        )

    def test_duplicate_branch_rejected(self):
        source = """
        packet X;
        observability WHITE_BOX;
        observe a key="x" value=1;
        declare a key="x" value=2;
        analyze;
        """
        with self.assertRaises(NativeCompileError):
            compile_program(parse_source(source))

    def test_missing_conflict_branch_rejected(self):
        source = """
        packet X;
        observability WHITE_BOX;
        observe a key="x" value=1;
        conflict c branches=a,b dimensions=VALUE;
        analyze;
        """
        with self.assertRaises(NativeCompileError):
            compile_program(parse_source(source))

    def test_intent_requires_drift_declaration(self):
        source = """
        packet X;
        observability WHITE_BOX;
        intent x at=1 value=1;
        action x at=1 value=1;
        analyze;
        """
        with self.assertRaises(NativeCompileError):
            compile_program(parse_source(source))

    def test_invariant_boolean_lock(self):
        source = """
        packet X;
        observability WHITE_BOX;
        invariant i at=1 preserved=maybe;
        analyze;
        """
        with self.assertRaises(NativeCompileError):
            compile_program(parse_source(source))

    def test_preserve_target_must_exist(self):
        source = """
        packet X;
        observability WHITE_BOX;
        preserve ghost;
        analyze;
        """
        with self.assertRaises(NativeCompileError):
            compile_program(parse_source(source))

    def test_duplicate_temporal_pair_rejected(self):
        source = """
        packet X;
        observability WHITE_BOX;
        drift x scale=1;
        intent x at=1 value=1;
        intent x at=1 value=1;
        action x at=1 value=1;
        analyze;
        """
        with self.assertRaises(NativeCompileError):
            compile_program(parse_source(source))

    def test_output_json_serializable(self):
        source = (ROOT / "examples" / "tim_native_conflict.lmg").read_text(
            encoding="utf-8"
        )
        payload = compile_program(parse_source(source)).to_dict()
        json.dumps(payload, ensure_ascii=False)
        self.assertEqual(payload["native_version"], "0.8.0")


if __name__ == "__main__":
    unittest.main()
