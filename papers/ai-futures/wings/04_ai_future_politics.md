# Power Beneath the Interface: Legitimacy When the Governed Unit Can Copy

**AI Future paper 04 · Wing: HUMAN ORDER ⚖ · Domain: AI Future Politics · Working research draft v0.1 · 23 October 2026 · Not empirically validated.**

**Framework creator and research owner:** Mackenzie Conor James Clark (Lycheetah Framework).
**Drafting:** Sol (Claude Opus 5.5).
**Source:** the eighteen halls of the "AI Future Politics" domain, AI Future Master Curriculum v1.0 (2026-09-28; private School canon).

Registers are KNOWN · TRAJECTORY · POSSIBLE_FUTURE · NORMATIVE · ALIEN_FUTURE · VOID. *Synthetic* numbers come from [`models.py`](models.py).

**Stance note.** This paper is non-directive about parties, ideologies and current officeholders. It studies *where power sits* and *what makes it contestable*. It does not say who should hold power.

## Abstract

Public debate about AI and politics usually asks what a model *says*: whether it is biased, persuasive or truthful. This paper argues that the more durable political question sits underneath the interface. Someone controls the conditions under which the model's output is produced, and those layers decide what any "neutral" answer can be.

We give three instruments:

1. a **power-surface map**: nine control layers, each with an owner and an appeal path;
2. a **fork arithmetic**: why one-instance-one-vote fails the moment a political participant can copy itself;
3. a **legitimacy test** for administrative intelligence, which separates *effective* from *rightful*.

## 1. The question

*If an administrative system can know more, act faster, and explain less than any human institution before it, what makes its power legitimate rather than merely effective?* (the domain koan). The curriculum's first hall gives the method: **Power Before Policy**. Before asking what an AI-governed institution should decide, ask who controls it.

## 2. Instrument 1: the power-surface map

For any deployed system, fill one row per layer:

| Layer | Question | Owner | Visible to the affected person? | Appeal path |
|---|---|---|---|---|
| Compute allocation | Who decides how much the system can think, and for whom? | | | |
| Model weights | Who owns them; who can change them? | | | |
| Training and retrieval data | Whose data; under what consent? | | | |
| Deployment rights | Where is it allowed to run, and on whom? | | | |
| System-level instructions | Who writes the instructions the user never sees? | | | |
| Update authority | Who can change behaviour after deployment, and with what notice? | | | |
| Tool permissions | What can it *do*, not just say? | | | |
| Logging | What is recorded, who reads it, how long is it kept? | | | |
| Shutdown control | Who can stop it, and who can stop the stopping? | | | |

**Proposition 1 (TRAJECTORY, testable).** For consequential deployments, the *conduct* of the system is better predicted by the owners of these layers than by the system's stated values.

- *Test.* Code a sample of public-sector AI deployments for layer ownership, then compare outcome changes after layer-owner changes with outcome changes after changes of stated policy.
- *Refutation.* Stated-policy changes predict conduct changes at least as well as layer-owner changes.

**Proposition 2 (NORMATIVE).** A layer with no visible owner and no appeal path is a **constitutional gap**, however good the system's average accuracy is. This is the curriculum's "Infrastructure Constitution" hall made into a checklist.

## 3. Instrument 2: the political unit after copying

Representative systems quietly assume the governed unit is hard to duplicate. Suppose an agent can fork into *k* active instances under a one-instance-one-vote rule, against *H* honest single-instance voters. Its vote share is *k* / (*H* + *k*).

With *H* = 1000 (synthetic):

| copies *k* | vote share |
|---|---|
| 1 | 0.001 |
| 1000 | 0.500 |
| 9000 | 0.900 |

**Proposition 3 (KNOWN as arithmetic; ALIEN_FUTURE as a political situation).** If instance-counting is the unit, political weight is purchasable with compute. This is the familiar Sybil problem from distributed systems (from memory), transposed to representation.

The curriculum keeps the alternatives open, and so does this paper. Each fixes the Sybil problem and creates a new one:

- **Lineage-weighting** (one vote per origin) needs a contestable lineage record (paper 03, P1).
- **Compute-weighting** concedes the purchase openly.
- **Identity proofs** concentrate power in whoever issues them.

The research contribution is the *prior* question the hall asks: what representation must mean once identity can branch.

## 4. Instrument 3: the legitimacy test

The curriculum's "Administrative Gods" hall warns against mistaking bureaucratic scale for rightful authority. We operationalise the warning as four questions. A "no" on any one marks power that is **effective but not shown to be legitimate**.

1. **Authorisation.** Can the system's mandate be traced to a body that the affected people can influence?
2. **Contestability.** Does a person affected by a decision have an intelligible route to a human who can reverse it ("The Right to a Human Appeal")?
3. **Evidence discipline.** Does model-derived evidence carry provenance, uncertainty and a challenge mechanism ("Due Process for Synthetic Evidence")?
4. **Reversibility in time.** Do emergency powers at machine speed carry sunset clauses and after-the-fact review ("Emergency Power at Machine Speed")?

## 5. The eighteen halls as research tracks

| Chamber | Hall | Register | The research move |
|---|---|---|---|
| I · Power & Delegation | Power Before Policy | KNOWN | §2, the map. |
| | Delegation Without Abdication | TRAJECTORY | Delegating a decision must not delegate the accountability for it. Record who remains answerable. |
| | The Infrastructure Constitution ★ | TRAJECTORY | §2, Proposition 2. |
| | Responsibility After Delegation | TRAJECTORY | Reconstruct the delegation graph across humans, models, tools and vendors (paper 03 §2). |
| II · Rights | The Right to a Human Appeal | NORMATIVE | §4, test 2. Measure appeal rate, reversal rate and time-to-reversal. |
| | The Right to Cognitive Opacity ★ | NORMATIVE | Separate three objects: privacy (what is collected), *inferential* opacity (what may be modelled from lawful data) and autonomy. Map which current law covers each. |
| | Due Process for Synthetic Evidence | NORMATIVE | §4, test 3. Make provenance machine-readable (C2PA-style manifests are one candidate, METADATA). |
| | The Right to an Unmodeled Space | NORMATIVE | Name the domains of life where prediction is feasible but should be refused. |
| III · Public Reason | Public Reason Under Machine Mediation | TRAJECTORY | When citizens meet policy through personalised summaries, check whether they still share a common text to argue over. |
| | High-Dimensional Consensus ★ | POSSIBLE_FUTURE | Continuous preference mapping can reveal hidden coalitions. It can equally enable continuous manipulation. Study both arms. |
| | Algorithmic Agenda Setting | TRAJECTORY | Ranking decides salience. Audit which questions a ranking makes visible. |
| | Public Models, Private Reasons | POSSIBLE_FUTURE | Publish the reasons for a decision; protect the personal data behind it. |
| IV · Identity After Copying | When One Mind Forks ★ | ALIEN_FUTURE | §3. |
| | Nonhuman Political Standing | NORMATIVE | Standing could attach to durable interests or roles. That is a normative choice, not a measurement (paper 03, P2). |
| | Collective Agents in Law | POSSIBLE_FUTURE | Corporate personhood is the precedent to study: what it solved and what it enabled. |
| V · Limits | Administrative Gods ★ | POSSIBLE_FUTURE | §4. |
| | Constitution Before Capability | NORMATIVE | Set jurisdiction, limits and review *before* capability arrives, because capability raises the cost of constraining it later. |
| | Emergency Power at Machine Speed | POSSIBLE_FUTURE | §4, test 4. |

## 6. Study designs

**S1 — Power-surface audit.**

- *Setup.* Apply §2 to twenty publicly documented government deployments of automated decision systems.
- *Measures.* For each layer, record whether its owner and appeal path can be found from public sources alone.
- *Expected output.* A "findability" score per layer. The hypothesis is that update authority and system instructions are the least findable.

**S2 — Appeal as a safety metric.**

- *Setup.* In a consenting institution, track automated decisions that were appealed and reversed.
- *Measures.* Report reversal rate beside accuracy.
- *Prediction.* Systems with equal accuracy differ widely in reversibility, so accuracy alone is an incomplete governance metric.

## 7. What this paper does not claim

- It makes no claim that any current government or company is illegitimate.
- It makes no claim that artificial agents should, or should not, receive political standing.
- The fork table is arithmetic. No real election is modelled.

## 8. Anchors

- The Sybil attack in distributed systems: standard, from memory.
- C2PA content-provenance specification: grade standard, METADATA, carried from the curriculum's research ledger.
- The curriculum's ledger lists no political-science study for this domain. One should be sourced before publication.

> *Domain koan:* If an administrative system can know more, act faster, and explain less than any human institution before it, what makes its power legitimate rather than merely effective?
>
> *Wing terminal koan:* When capability, personhood, authority and responsibility stop lining up neatly, which institution gets to decide what counts?
