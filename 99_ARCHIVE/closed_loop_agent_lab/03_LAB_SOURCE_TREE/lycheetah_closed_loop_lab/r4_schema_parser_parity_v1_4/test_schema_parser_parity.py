import json
import unittest
from pathlib import Path
import jsonschema
from schema_parser_parity import SECRET, base_body, seal, mutate, baseline_accepts, strict_candidate_accepts, schema_accepts

ROOT=Path(__file__).resolve().parent
CASES=["schema_version_number","finding_title_boolean","confidence_boolean","evidence_integer","control_title_boolean","control_url_boolean","control_framework_number","control_unknown_field"]
class TestSchemaParserParity(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.validator=jsonschema.Draft202012Validator(json.loads((ROOT/"receipt.schema.json").read_text()))
 def test_well_typed_unsigned_and_hmac_receipts_pass(self):
  unsigned=seal(base_body(),None); signed=seal(base_body(),SECRET)
  self.assertTrue(schema_accepts(unsigned,self.validator)[0])
  self.assertTrue(baseline_accepts(unsigned,None)[1])
  self.assertTrue(schema_accepts(signed,self.validator)[0])
  self.assertTrue(baseline_accepts(signed,SECRET)[1])
 def test_source_equivalent_parser_accepts_mutated_normalized_wire_forms(self):
  for case in CASES:
   for signed,key in ((False,None),(True,SECRET)):
    with self.subTest(case=case,signed=signed):
     payload=mutate(seal(base_body(),key),case)
     digest_ok, accepted, hmac_ok=baseline_accepts(payload,key)
     self.assertTrue(digest_ok); self.assertTrue(accepted)
     if signed: self.assertTrue(hmac_ok)
 def test_strict_candidate_rejects_each_mutation(self):
  for case in CASES:
   for key in (None,SECRET):
    with self.subTest(case=case,signed=key is not None):
     payload=mutate(seal(base_body(),key),case)
     self.assertFalse(strict_candidate_accepts(payload)[0])
 def test_schema_catches_top_level_and_finding_mismatches(self):
  for case in ("schema_version_number","finding_title_boolean","confidence_boolean","evidence_integer"):
   with self.subTest(case=case):
    payload=mutate(seal(base_body(),None),case)
    self.assertFalse(schema_accepts(payload,self.validator)[0])
 def test_strict_candidate_schema_rejects_all_typed_mutations(self):
  strict=json.loads((ROOT/"receipt.schema.strict-candidate.json").read_text())
  validator=jsonschema.Draft202012Validator(strict)
  for case in CASES+["policy_digest_invalid","finding_unknown_field"]:
   for key in (None,SECRET):
    with self.subTest(case=case,signed=key is not None):
     if case=="policy_digest_invalid":
      body=base_body(); body["policy"]["sha256"]="not-a-digest"; payload=seal(body,key)
     elif case=="finding_unknown_field":
      body=base_body(); body["findings"][0]["extension"]="unexpected"; payload=seal(body,key)
     else: payload=mutate(seal(base_body(),key),case)
     self.assertFalse(schema_accepts(payload,validator)[0])
 def test_current_schema_has_open_nested_control_object(self):
  for case in ("control_title_boolean","control_url_boolean","control_framework_number","control_unknown_field","finding_unknown_field"):
   with self.subTest(case=case):
    payload=mutate(seal(base_body(),None),case)
    self.assertTrue(schema_accepts(payload,self.validator)[0])

if __name__=="__main__": unittest.main(verbosity=2)
