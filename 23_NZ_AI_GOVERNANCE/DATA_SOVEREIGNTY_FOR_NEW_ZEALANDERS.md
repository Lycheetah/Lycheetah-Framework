# DATA SOVEREIGNTY FOR NEW ZEALANDERS
## One standard. Every citizen. The same rights.
### Draft open standard v0.1 | Lycheetah Framework | Ōtepoti / Dunedin | October 2026

> **Status:** `[PROPOSAL]`. A draft open standard. It is not law, it has not been adopted by any agency, and no lawyer has reviewed it yet.
> **Licence:** documents CC BY 4.0, code MIT.
> **Author:** Mackenzie Conor James Clark, with the Lycheetah Framework.

---

## The principle

**Your data is yours.** That holds the same for every New Zealander, whatever your ancestry, region, faith, age or politics.

An AI system that works with New Zealanders' data answers to every person it touches, equally. No group gets more control over its data than any other, and no group gets less.

## Why now

Overseas AI systems are becoming the default infrastructure here. New Zealanders' records, messages and decisions now pass through models that are hosted, trained and governed offshore. Most people cannot see when an AI touched their data, what it decided, or where that data now lives.

New Zealand is small enough to set a clear rule early, and to set it once for everyone.

---

## The six rights

| # | Right | What it means for you |
|---|---|---|
| 1 | **Right to know** | You are told when an AI system processed your data or shaped a decision about you, and you are told which system. |
| 2 | **Right to the receipt** | You get a record you can keep: what was done, under which policy, and when. Integrity information lets you compare the record with a trusted copy. A hash alone does not prevent rewriting or prove that the recorded event occurred. |
| 3 | **Right to take it back** | You can access your data, request correction, and withdraw specified future AI uses under the proposed standard. Retention duties, exceptions and effects already completed must be disclosed; erasure from trained models is not promised. |
| 4 | **Right to a human** | Any consequential decision about you (a benefit, health care, a job, housing, a legal matter) has a named human path to review it and overturn it. |
| 5 | **Right to know where it lives** | You are told where your data is stored and whether it leaves New Zealand. If it goes offshore, that is disclosed, and it must be protected to at least the same standard as at home. |
| 6 | **Right to equal treatment** | Systems are tested for whether they treat groups of New Zealanders differently, and the results are published. |

## How this builds on the law we already have

The Privacy Act 2020 provides existing protections for individuals, subject to its scope and exceptions. Official references checked 19 October 2026:

- [IPP 6: access](https://www.privacy.org.nz/privacy-principles/6/) allows a person to request their own personal information; lawful withholding grounds remain.
- [IPP 7: correction](https://www.privacy.org.nz/privacy-principles/7/) allows a correction request and, when correction is declined, a request to attach a statement.
- [IPP 12: overseas disclosure](https://www.privacy.org.nz/privacy-principles/12/) sets conditions for covered disclosures outside New Zealand.

These provisions do not by themselves enact this proposal's AI-use notice, universal receipt, withdrawal or human-review package. No citizenship test is inferred from them.

This standard does not replace the Act. It adds the layer the Act was not written for: telling people when AI was used, giving them a receipt, guaranteeing a human path, and publishing equal-treatment tests.

---

## How Lycheetah makes it checkable

A right that cannot be checked is only a wish. Here is what this repository can already do toward each right, and what it cannot do yet.

| Right | Tool in this repository | What it does today | Status |
|---|---|---|---|
| 1 Know · 2 Receipt | [`lycheetah-assure`](../34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md) · [`lycheetah-guard`](../lycheetah/assurance/gateway.py) | Writes verifiable receipts for evaluated text and proposed actions, and keeps a local ledger with Ed25519-signed checkpoints. | `[SCAFFOLD]` runs locally; not deployed anywhere |
| 4 Human | [`lycheetah-sovereign`](../lycheetah/sovereign_harness.py) | Binds an action to a declared authority grant, one scope, one state version, an expiry and a single use. A replayed permit is refused. | `[SCAFFOLD]` an identity string does not prove a real person approved it |
| 3 Take it back | none yet | | **Gap.** Next target. |
| 5 Where it lives | none yet | | **Gap.** Next target. |
| 6 Equal treatment | none yet | [`discrimination_audit.py`](../33_APPLICATIONS/discrimination_audit.py) tests whether a scorer separates labelled text. It is **not** a fairness test between groups of people. | **Gap.** Next target. |

---

## The citizen's receipt (illustrative)

This is what a receipt under Right 2 could look like. It is a sketch, not an implemented schema.

```json
{
  "system": "Example benefits triage model v3",
  "operator": "Example agency",
  "purpose": "Prioritise application for review",
  "ai_used": true,
  "decision": "Flagged for priority human review",
  "human_review": "Ask any office, or reply to this notice, for a named reviewer",
  "data_location": "New Zealand",
  "leaves_nz": false,
  "policy_version": "2026-10-01",
  "issued_at": "2026-10-17T09:00:00+13:00",
  "receipt_digest": "sha256:..."
}
```

## How it fits with the Community AI Warrant of Fitness

The [Community AI WOF](COMMUNITY_AI_WOF.md) is the **annual** check on a system. This standard is the **per-person** promise. A system that fails these rights should not get its WOF.

---

## What this is not

- It is not law, not legal advice, and not adopted by anyone.
- It does not rank New Zealanders by ancestry or by anything else. Everyone gets the full set of rights.
- The tools above are local scaffolds. They are not running infrastructure, and they do not certify that any system is safe.

## Next steps

1. **Build the equal-treatment test (Right 6).** Measure how a system's decisions differ across groups and publish the result.
2. **Turn the citizen's receipt into a real schema** with a `lycheetah-assure` profile, so Rights 1 and 2 can be issued and verified.
3. **Get a legal read** from a New Zealand privacy lawyer.
4. **Run a pilot** with one willing organisation and publish what happens, including whatever fails.

Argue with it, improve it, or fork it. That is what it is for.

---

*Mackenzie Conor James Clark | Lycheetah Framework | Ōtepoti / Dunedin, New Zealand | October 2026*
*github.com/Lycheetah/Lycheetah-Framework*
