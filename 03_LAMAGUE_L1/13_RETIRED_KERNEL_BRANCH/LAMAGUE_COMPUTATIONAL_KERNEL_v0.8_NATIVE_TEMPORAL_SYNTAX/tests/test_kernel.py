from __future__ import annotations
import copy, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from lamague_kernel.api import run_file
from lamague_kernel.compiler import compile_program, expand_path
from lamague_kernel.continuity import classify
from lamague_kernel.errors import CompileFailure, ParseFailure
from lamague_kernel.parser import parse_file, parse_source
from lamague_kernel.registry import OPERATIONS, PUBLIC_CORE, SEALS
from lamague_kernel.seals import expand_seal

class RegistryTests(unittest.TestCase):
    def test_all_ops(self): self.assertEqual(set(OPERATIONS),set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    def test_public_core(self): self.assertEqual(len(PUBLIC_CORE),9)
    def test_seals(self): self.assertEqual(len(SEALS),5)
    def test_seal_expansion(self): self.assertEqual(expand_seal("Correction"),("D","A","F","P","Y"))
    def test_compiler_seal_expansion(self): self.assertEqual(expand_path(("@Frontier",)),SEALS["Frontier"])

class ParserTests(unittest.TestCase):
    def test_controlled(self):
        s=parse_file(ROOT/"examples/controlled_release.lmg"); self.assertEqual(s.name,"ControlledRelease"); self.assertEqual(len(s.unknowns),2)
    def test_unknown(self):
        s=parse_source('''program T
path O -> U -> I -> G -> F -> Y
unknown cause protected required_for=decision
invariant x "x"
authority a scope=s "a"
affected p
recovery r "r"
yield "y"'''); self.assertTrue(s.unknowns[0].protected); self.assertEqual(s.unknowns[0].required_for,"decision")
    def test_bad_keyword(self):
        with self.assertRaises(ParseFailure): parse_source("program X\npath O -> F -> Y\nmystery x")

class CompilerTests(unittest.TestCase):
    def test_controlled_compiles(self):
        ir,ds=compile_program(parse_file(ROOT/"examples/controlled_release.lmg")); self.assertTrue(ir.semantic_id); self.assertTrue(any(d.code=="COMPRESSION_MUST_EXPAND" for d in ds))
    def test_missing_authority(self):
        with self.assertRaises(CompileFailure) as cm: compile_program(parse_file(ROOT/"examples/unsafe_missing_authority.lmg"))
        self.assertTrue(any(d.code=="AUTHORITY_REQUIRED" for d in cm.exception.diagnostics))
    def test_missing_gates(self):
        with self.assertRaises(CompileFailure) as cm: compile_program(parse_file(ROOT/"examples/unsafe_irreversible_missing_gates.lmg"))
        self.assertTrue(any(d.code=="IRREVERSIBLE_GATES_MISSING" for d in cm.exception.diagnostics))
    def test_missing_fold(self):
        src='''program X
path O -> E -> U -> I -> G -> Y
unknown u protected
invariant i "i"
authority a scope=s "a"
affected p
recovery r "r"
yield "x"'''
        with self.assertRaises(CompileFailure) as cm: compile_program(parse_source(src))
        self.assertTrue(any(d.code=="FOLD_REQUIRED" for d in cm.exception.diagnostics))
    def test_protected_unknown_requires_u(self):
        src='''program X
path O -> E -> I -> G -> F -> Y
unknown u protected
invariant i "i"
authority a scope=s "a"
affected p
recovery r "r"
yield "x"'''
        with self.assertRaises(CompileFailure) as cm: compile_program(parse_source(src))
        self.assertTrue(any(d.code=="PROTECTED_UNKNOWN_NOT_ACTIVATED" for d in cm.exception.diagnostics))
    def test_valueflow_required(self):
        src='''program X
path O -> E -> U -> I -> G -> X -> F -> Y
unknown u protected
invariant i "i"
authority a scope=s "a"
affected p
recovery r "r"
effect TransfersValue<a,b>
yield "x"'''
        with self.assertRaises(CompileFailure) as cm: compile_program(parse_source(src))
        self.assertTrue(any(d.code=="VALUE_FLOW_REQUIRED" for d in cm.exception.diagnostics))
    def test_dissent_suppression(self):
        src='''program X
path O -> E -> W -> U -> I -> G -> F -> Y
unknown u protected
invariant i "i"
authority a scope=s "a"
affected p
dissent p "no"
recovery r "r"
effect SuppressesDissent
yield "x"'''
        with self.assertRaises(CompileFailure) as cm: compile_program(parse_source(src))
        self.assertTrue(any(d.code=="DISSENT_SUPPRESSION" for d in cm.exception.diagnostics))
    def test_resolution_needs_evidence(self):
        src='''program X
path O -> U -> I -> G -> R -> F -> Y
unknown u protected
invariant i "i"
authority a scope=s "a"
affected p
recovery r "r"
effect ResolvesUnknown<u>
resolve u with=missing
yield "x"'''
        with self.assertRaises(CompileFailure) as cm: compile_program(parse_source(src))
        self.assertTrue(any(d.code=="RESOLUTION_EVIDENCE_MISSING" for d in cm.exception.diagnostics))

class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report=run_file(ROOT/"examples/controlled_release.lmg")
    def test_yield(self): self.assertTrue(self.report.final_state.yielded)
    def test_expand(self): self.assertEqual(self.report.final_state.compression_mode,"Z_UP")
    def test_hash(self): self.assertEqual(len(self.report.final_state.state_hash),64)
    def test_trace_length(self): self.assertEqual(len(self.report.trace),len(self.report.ir.operations))
    def test_trace_links(self):
        for i in range(1,len(self.report.trace)): self.assertEqual(self.report.trace[i].before_hash,self.report.trace[i-1].after_hash)
    def test_unknowns(self): self.assertEqual(set(self.report.final_state.unresolved_unknowns),{"rare_failure","long_term_effect"})
    def test_invariants(self): self.assertEqual(len(self.report.final_state.invariants_locked),3)
    def test_authority(self): self.assertTrue(self.report.final_state.authority_checked)
    def test_fold(self): self.assertTrue(self.report.final_state.memory_folded)
    def test_resolution(self):
        r=run_file(ROOT/"examples/evidence_resolution.lmg"); self.assertEqual(r.final_state.unresolved_unknowns,()); self.assertEqual(r.final_state.resolved_unknowns,("cause",)); self.assertEqual(r.final_state.proof_status,"SUPPORTED_WITHIN_SCOPE")
    def test_dissent(self): self.assertEqual(len(run_file(ROOT/"examples/protected_dissent.lmg").final_state.dissent_preserved),2)
    def test_deterministic(self): self.assertEqual(self.report.final_state.state_hash,run_file(ROOT/"examples/controlled_release.lmg").final_state.state_hash)

class ContinuityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.base=run_file(ROOT/"examples/controlled_release.lmg").to_dict()
    def test_continuation(self): self.assertEqual(classify(self.base,self.base).classification,"CONTINUATION")
    def test_descendant(self):
        c=copy.deepcopy(self.base); c["ir"]["affected_parties"] = tuple(c["ir"]["affected_parties"]) + ("new_party",); self.assertEqual(classify(self.base,c).classification,"DESCENDANT")
    def test_fork(self):
        c=copy.deepcopy(self.base); c["final_state"]["unresolved_unknowns"]=[]; self.assertEqual(classify(self.base,c).classification,"FORK")
    def test_impostor(self):
        c=copy.deepcopy(self.base); c["final_state"]["invariants_locked"]=c["final_state"]["invariants_locked"][1:]; self.assertEqual(classify(self.base,c).classification,"IMPOSTOR")

if __name__=="__main__": unittest.main()
