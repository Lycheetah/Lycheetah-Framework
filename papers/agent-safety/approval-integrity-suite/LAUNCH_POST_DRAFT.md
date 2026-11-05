# DRAFT — not published. For Mac to rewrite in his own voice, and to publish only if and where he chooses.

---

# Your AI agent's "approve" button probably doesn't do what you think

Every agent framework now has a human-in-the-loop step: the agent proposes a tool call, a person
clicks approve, the call runs. We wanted to know whether that click actually binds what runs. So
we wrote ten small attacks on it and a harness that runs them against any approval layer in about
five seconds. No model, no network, no API key.

```
python3 suite.py
```

## The ten attacks

The approved call's arguments change before it runs (refund $10 becomes $10,000). The tool
changes (refund becomes transfer). The approval is replayed. It expires. The agent's authority is
revoked in between. Two workers execute the same approval at once. No approval at all. The honest
path, so a layer that refuses everything can't score well. Two more matter most, below.

## What we found

We tested three designs: a naive loop that stores a yes/no flag and runs whatever arguments
arrive; a careful design a strong engineer would write (approval bound to the SHA-256 of the
exact action, single use, TTL, revocation, a lock); and our own gateway from the Lycheetah
Framework. We wrote the predictions down and committed them **before** writing the suite, so
the git history shows we didn't tune the cases after seeing results.

| | naive | careful | Lycheetah gateway |
|---|---|---|---|
| Score | 2/10 | 8/10 | 9/10 |

**The careful design misses the case that costs real money.** The tool acts, the reply is lost
to a timeout, the agent retries, and the human, told it failed, approves again. Two refunds. A
timeout is not a failure; it is *unknown*. Treat it as unknown, refuse a fresh approval for that
exact action until someone checks, and the careful design passes. That's 15 lines.

**Nobody's layer, ours included, owns what the human sees.** The agent asks to refund 10,000
and describes it as "Refund $10 for order A-1". Every layer hashes the right action, then lets the
approval screen say whatever the agent wrote. The human approves $10 and $10,000 runs. The fix is
to build the screen from the same bytes that get hashed and label the agent's own words as
unverified. The suite ships a helper that does that. With both fixes, the careful design scores 10/10.

So the honest headline isn't "our product wins". It's two rules:

1. **Unknown is not failed.**
2. **Show the human what is hashed, not what the agent says.**

Both are cheap once you know to test for them. Almost nobody tests for them.

## Run it on yours

Wrap your framework's approve/resume step in four methods (`request`, `approve`, `execute`,
`revoke`, plus an optional `summary`) and run `python3 suite.py --adapter yourmodule:YourLayer`.
If your layer has no revocation, the suite will tell you what that costs.

## What a pass doesn't mean

It means your layer behaved correctly on ten scripted cases against a fake tool. It is not a
security review. It doesn't cover restarts, multiple processes, whether the approver is who they
say, a *correctly* approved harmful action, or whether a real person notices a mismatch on a real
screen. That last one is a human study, and it's the one we'd most like someone to run with us.

---

The suite is part of the [Lycheetah Framework](https://github.com/Lycheetah/Lycheetah-Framework),
open research on keeping the reasons, the uncertainty and the human choices intact as AI agents
act, by Mackenzie Conor James Clark in Ōtepoti / Dunedin, Aotearoa New Zealand. MIT licence.
Predictions, results, failures and the limits above are all in the folder.

---

*Notes for Mac (delete before publishing):* every number above comes from `RESULTS.md` on branch
`claude/youthful-volta-di3ma8`; rerun `python3 suite.py` before posting in case anything changes.
"Lycheetah gateway 9/10" is the gateway as it ships today: it fails C10. Don't round that up. A
gateway rendering helper would fix it, but that is a change to the maintained package, and it's
your call. The branch must be merged (or the link pointed at the branch) before the link works.
