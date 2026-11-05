"""On-device assistant skeleton: its approval path scores 10/10 and leaves nothing ungated.

Claim coverage (33_APPLICATIONS/on_device_assistant/README.md):
  [SCAFFOLD] the app's own approval layer passes all ten Approval Integrity Suite cases
  [SCAFFOLD] a refused or failed fetch never reaches the network stand-in; the person is shown
             the bound action, not the model's description alone
Stand-in model and fake fetcher; no model is run and nothing is fetched.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "33_APPLICATIONS" / "on_device_assistant"))

import assistant  # noqa: E402
import suite  # noqa: E402  (put on sys.path by assistant)

pytestmark = pytest.mark.scaffold


def test_app_approval_layer_scores_ten_of_ten():
    results = suite.run_suite(assistant.ApprovalLayer)
    assert [r.case for r in results if not r.passed] == []


def _bot(approve, fetched, fail=False):
    def fetch(args):
        fetched.append(args["url"])
        if fail:
            raise TimeoutError("network dropped")
        return "Dunedin: 14 degrees, light rain"
    return assistant.Assistant(model=assistant.StandInModel("https://example.org/w"),
                               approve=approve, fetch=fetch)


def test_refused_fetch_never_leaves_the_device():
    fetched, screens = [], []
    bot = _bot(lambda s: screens.append(s) or False, fetched)
    bot.ask("weather?")
    assert fetched == []
    assert "url = \"https://example.org/w\"" in screens[0]
    assert "Agent says (not verified)" in screens[0]
    assert bot.log[0]["outcome"] == "REFUSED_BY_PERSON"


def test_approved_fetch_runs_once_and_answers():
    fetched = []
    bot = _bot(lambda s: True, fetched)
    answer = bot.ask("weather?")
    assert fetched == ["https://example.org/w"] and "14 degrees" in answer
    assert bot.log[0]["outcome"] == "EXECUTED"


def test_dropped_connection_is_unknown_not_failed():
    fetched = []
    bot = _bot(lambda s: True, fetched, fail=True)
    bot.ask("weather?")
    assert bot.log[0]["outcome"] == "UNKNOWN"
