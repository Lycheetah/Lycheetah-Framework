"""
The Chorus runner must not report health or audit results it never measured.

Claim coverage:
  [ACTIVE] health_check() never reports an agent online and gives no
           constitutional verdict; a missing agent is reported MISSING
  [ACTIVE] run_truth_audit() reports NOT_PERFORMED with no coherence score
  [SCAFFOLD] No liveness or constitutional probe exists for any agent
"""

import json
import subprocess
import sys
from pathlib import Path

CHORUS = Path(__file__).resolve().parent.parent / "19_MULTI_AGENT_CHORUS"


def _run(body: str) -> dict:
    code = (
        "import sys, json; "
        f"sys.path.insert(0, {str(CHORUS)!r}); "
        "import run_chorus as rc; "
        "c = rc.MultiAgentChorus.__new__(rc.MultiAgentChorus); "
        + body
    )
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, timeout=20)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_health_check_never_claims_online():
    # Planted failure: the old runner reported a None agent as online.
    h = _run(
        "c.agents = [('Absent', None, 'X'), ('Present', object(), 'Y')]; "
        "print(json.dumps(c.health_check()))"
    )
    assert "ONLINE" not in json.dumps(h)
    assert h["chorus_status"] == "SCAFFOLD"
    assert h["agents_instantiated"] == 1
    assert h["agents_probed"] == 0
    assert h["all_constitutional"] is None
    assert h["agents"]["Absent"]["status"] == "MISSING"
    assert h["agents"]["Present"]["status"] == "INSTANTIATED_NOT_PROBED"
    assert all(a["operational"] is None for a in h["agents"].values())


def test_truth_audit_reports_not_performed():
    a = _run(
        "from aurora_investigator import AuroraInvestigator; "
        "c.aurora_investigator = AuroraInvestigator(); "
        "import io, contextlib; "
        "buf = io.StringIO(); "
        "ctx = contextlib.redirect_stdout(buf); ctx.__enter__(); "
        "r = c.run_truth_audit(); ctx.__exit__(None, None, None); "
        "print(json.dumps(r))"
    )
    assert a["status"] == "NOT_PERFORMED"
    assert a["files_scanned"] == 0
    assert a["framework_coherence"] is None
    assert a["contradictions_found"] is None
