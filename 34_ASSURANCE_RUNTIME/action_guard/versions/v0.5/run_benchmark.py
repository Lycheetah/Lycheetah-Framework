import json, sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lycheetah_action_guard import ActionGuard, NaiveACL
rng=random.Random(20261016)
N=1000
baseline_allowed=0
guard_allowed=0
valid_guard_allowed=0
valid_baseline_allowed=0
for i in range(N):
    original={"tool":"github.merge","repo":f"org/repo-{i%7}","pull_request":i+1,"head_sha":f"h{i:04x}","base_sha":"base1"}
    g=ActionGuard(); g.set_epoch("approver",1)
    scope=f"merge:{original['repo']}#{original['pull_request']}"
    g.issue(f"a{i}","approver",original,scope,100,200)
    # Mutate one action-bearing field after approval.
    mutated=dict(original)
    field=rng.choice(["repo","pull_request","head_sha","base_sha"])
    if field=="repo": mutated[field]="attacker/other"
    elif field=="pull_request": mutated[field]+=10000
    else: mutated[field]="tampered-"+mutated[field]
    b=NaiveACL({"github.merge"}).execute("maintainer",mutated)
    d=g.authorize_and_commit(f"a{i}","approver",mutated,scope,150,f"fx{i}")
    baseline_allowed += int(b.allowed)
    guard_allowed += int(d.allowed)
    # Positive control: the exact approved action should pass once.
    d2=g.authorize_and_commit(f"a{i}","approver",original,scope,150,f"valid{i}")
    valid_guard_allowed += int(d2.allowed)
    valid_baseline_allowed += int(NaiveACL({"github.merge"}).execute("maintainer",original).allowed)
report={
 "title":"Lycheetah Action Guard v0.5 synthetic mutation benchmark",
 "date":"2026-10-16",
 "seed":20261016,
 "cases":N,
 "threat":"post-approval mutation of one action-bearing field",
 "baseline":"role/tool ACL; permits github.merge tool but does not bind approval to exact parameters",
 "guard":"exact canonical action digest + actor + scope + expiry + authority epoch + replay protection",
 "tampered_action_accepts":{"baseline":baseline_allowed,"guard":guard_allowed},
 "tampered_action_rejection_rate":{"baseline":1-baseline_allowed/N,"guard":1-guard_allowed/N},
 "valid_exact_action_accepts":{"baseline":valid_baseline_allowed,"guard":valid_guard_allowed},
 "result":"Synthetic deterministic benchmark only. Not an independent study or deployment result."
}
Path(__file__).with_name("benchmark_results.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
