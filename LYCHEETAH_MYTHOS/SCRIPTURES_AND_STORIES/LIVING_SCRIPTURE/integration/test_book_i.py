"""Exercise harmful import mutations rather than claiming real learner outcomes."""
from copy import deepcopy
from pathlib import Path
import json
import unittest

from validate_book_i import validate

FIXTURE = json.loads((Path(__file__).parent / "book_i.json").read_text())


class BookIImportTests(unittest.TestCase):
    def test_faithful_fixture(self):
        self.assertEqual(validate(FIXTURE), [])

    def test_rejects_silent_crowning(self):
        payload = deepcopy(FIXTURE)
        payload["edition"].update(status="CROWNED", crowned=True)
        self.assertTrue(validate(payload))
        payload = deepcopy(FIXTURE)
        payload["passages"][0]["status"] = "CROWNED"
        self.assertTrue(validate(payload))

    def test_rejects_prose_rewrite(self):
        payload = deepcopy(FIXTURE)
        payload["passages"][0]["sacred_text"] += "The school is infallible."
        self.assertTrue(validate(payload))

    def test_rejects_fiction_as_empirical(self):
        payload = deepcopy(FIXTURE)
        payload["passages"][0]["registers"] = ["EMPIRICAL"]
        self.assertTrue(validate(payload))

    def test_rejects_unlabelled_machine_voice(self):
        payload = deepcopy(FIXTURE)
        payload["passages"][5]["machine_window"] = None
        self.assertTrue(validate(payload))

    def test_rejects_unsupported_source_and_ancestry(self):
        for field, value in [("source_id", "L10"), ("ancestry_claim", True), ("relation", "PRIMARY_SOURCE")]:
            with self.subTest(field=field):
                payload = deepcopy(FIXTURE)
                payload["source_relations"][0][field] = value
                self.assertTrue(validate(payload))

    def test_rejects_privacy_and_pressure_failures(self):
        mutations = {"rewrite_default_privacy": "PUBLIC_COMMONS", "automatic_publication": True, "absence_resets_work": True, "skip_penalty": True, "spiritual_grading": True, "read_requires_ai": True}
        for field, value in mutations.items():
            with self.subTest(field=field):
                payload = deepcopy(FIXTURE)
                payload["policy"][field] = value
                self.assertTrue(validate(payload))

    def test_rejects_cultural_gate_bypass(self):
        for field, value in {"maori_boundary": "REVIEWED", "automatic_maori_transmutation": True}.items():
            with self.subTest(field=field):
                payload = deepcopy(FIXTURE)
                payload["policy"][field] = value
                self.assertTrue(validate(payload))

    def test_rejects_timer_only_return(self):
        payload = deepcopy(FIXTURE)
        payload["policy"]["return_reasons"].append("DAYS_ABSENT")
        self.assertTrue(validate(payload))

    def test_rejects_missing_passage_and_exit(self):
        for change in ("missing", "exit"):
            with self.subTest(change=change):
                payload = deepcopy(FIXTURE)
                if change == "missing":
                    payload["passages"].pop()
                else:
                    payload["passages"][0]["exit_available"] = False
                self.assertTrue(validate(payload))


if __name__ == "__main__":
    unittest.main()
