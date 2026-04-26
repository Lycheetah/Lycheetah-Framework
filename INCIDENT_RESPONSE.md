# Incident Response Protocol — Misappropriation, Capture, and Misrepresentation

**Status:** [ACTIVE] — D-1.1 defense surface
**Author:** Mackenzie Conor James Clark
**Last updated:** 2026-04-26
**Companion docs:** `CONFLICT_OF_INTEREST.md`, `ATTRIBUTION_REQUIREMENTS.md`, `LIVING_CODEX_PROTOCOL.md`, `LICENSE`
**Purpose:** a pre-decided protocol for what to do — and what NOT to do — when the framework, in part or in whole, is appropriated, rebranded, captured, or misrepresented by a lab, company, institution, or individual. Pre-deciding the response prevents reactive over- or under-response in the moment.

---

## The premise

The Codex is published openly. Open publication is a deliberate choice: priority by timestamp, lineage by commit history, attribution by license. The trade-off of open publication is exposure to misappropriation — silent absorption, rebranding, or institutional capture without attribution.

This document is the response posture for when (not if) that happens. It is calibrated to two principles:

1. **Proportionate response.** Not every borrowing is an incident. Honest engagement, criticism, derivative scholarly work, and citation under license are the goal, not threats. Most contact is welcome.
2. **No quiet absorption.** What the framework will not tolerate is silent capture — adoption of substantive content without attribution, in a way that breaks the lineage chain or claims priority the framework already established.

The protocol below distinguishes incident classes and matches each to a specific, pre-decided response.

---

## Incident classes

### Class 1 — Honest engagement (NOT an incident)

Includes: scholarly citation under license; constructive criticism; replication attempts; derivative scholarly work that cites; teaching and review; commercial exploration with attribution; private research using the published material with intent to cite on publication.

**Response:** none required beyond the normal scholarly engagement (respond to questions, support replication, accept criticism). Document the engagement in the project's reference log if material.

### Class 2 — Attribution failure (low-severity incident)

Includes: substantive use of the framework's terminology, structure, or distinctive claims without citation, where the omission appears to be oversight rather than intent. Examples: a paper using "Solve et Coagula → Ψ ∘ ⚘" notation without citing CHRYSOPOEIA; a blog post listing the Seven AURA Invariants without source; a conference talk using the TC ≥ 3 convergence methodology without LAMAGUE attribution.

**Response (sequential, escalate only on no-response):**

1. **Direct contact, friendly tone.** Email or comparable channel. State the overlap, point to the canonical source, offer the citation. Assume oversight. Provide BibTeX from `CITATIONS.md`. Set expectation of correction in next revision / web edit / upcoming version.
2. **Document the contact.** Save outgoing message, dates, recipients in the project's incident log (private file, not committed).
3. **Allow 30 days for response/correction.** Most incidents resolve here.
4. **If no response or refusal**: escalate to Class 3 procedure for the same material.

### Class 3 — Substantive capture (medium-severity incident)

Includes: rebranded publication of substantive framework content under a different name; institutional adoption of the framework's structure or claims as the institution's own; commercial product built on the framework's claims without license compliance; refusal to attribute after Class 2 contact.

**Response (sequential):**

1. **Public timestamp record.** Confirm and link the canonical priority record: GitHub commit SHA(s), tagged release(s), the 1,402-page archive. Do this before any public statement.
2. **Document the capture.** Side-by-side comparison: their material vs. canonical source, with timestamps. Save permanently. Do not publish yet.
3. **Formal contact.** Written notice (email + registered post if a corporate or institutional entity), citing license terms, requesting attribution and any other license compliance, with a clear remedy and deadline (typically 14 days).
4. **Public clarification, factual register.** If formal contact is ignored or refused: a single, factual public statement on the framework's primary channels (GitHub README, the Sol Protocol architecture page, a single short post on the author's primary public channel). State: what was published when, what they published when, the overlap, the requested attribution, the response (or absence). No emotional language. No accusations of intent. Just the timeline and the asks.
5. **Engage community defenders.** Reach out to academics, journalists, and AI ethics commentators whose work the framework has engaged respectfully. They are not enlisted; they are informed, with the same factual record. They decide whether to comment.
6. **Legal review.** If license is clearly violated and the appropriator is a substantial entity (lab, company, institution), consult a lawyer specializing in IP/license enforcement in the relevant jurisdiction. Do not threaten litigation publicly until counsel has reviewed.

### Class 4 — Hostile capture or misrepresentation (high-severity incident)

Includes: public claim of priority over framework content the framework demonstrably published first; misrepresentation of the framework's claims (e.g., stating the framework claims something it explicitly does not, in order to dismiss it); attempts to assert IP ownership over framework content; coordinated discrediting campaigns; doxxing or harassment of the author for the work.

**Response (the order matters):**

1. **Personal safety first.** If anything in the incident touches the author's physical safety, financial security, or mental health, those concerns lead. Pause public response. Consult trusted people first. The work survives a paused response; it does not survive an author destroyed by responding too fast.
2. **Lock down the canonical record.** Verify all GitHub commits, tags, and the archive are intact and timestamped. Mirror to a second public repository (e.g., Codeberg, GitLab) if not already done. Snapshot all relevant evidence.
3. **Counsel before public response.** A high-severity public response made without legal review can damage the framework more than the incident itself. Get review.
4. **Public response, structured.** If counsel approves: a structured public statement that (a) presents the timeline and evidence, (b) states the misrepresentation (if any) and what the framework actually claims, with citation, (c) declines emotional escalation, (d) leaves a path for the other party to retract or correct.
5. **Sustained, factual rebuttal.** Where misrepresentation persists, sustain a factual rebuttal record (e.g., a dedicated section of the framework's site or this repository). Update as needed. Do not engage in real-time argument cycles.
6. **Community.** Lean on the community of attribution-respectful researchers who have engaged the framework. They are informed, not weaponized; their independent voice is worth more than the author's.

### Class 5 — Internal incident (the framework itself drifting)

Includes: incidents in which a contributor, collaborator, or AI tool used by the framework introduces content that violates the framework's own attribution or claim-status standards. This is the rarest class but the most important.

**Response:**

1. **Detect.** The defense layer's audit machinery (`ADVERSARIAL_AUDIT_REPORT.md`, `EVIDENCE_LADDER.md`, `FALSIFICATION_REGISTER.md`) is the primary detection mechanism. Run audits on schedule.
2. **Demote or retract.** If a claim has been overstated, demote per `EVIDENCE_LADDER.md`. If a claim is false, retract via `FAILURE_MUSEUM.md` and update `CLAIMS.json`. Audit trail in commit log.
3. **Disclose.** Material internal incidents are disclosed in `LIVING_CODEX_PROTOCOL.md` and (if affecting prior publications) corrected via the venue's correction process.
4. **No defensiveness.** The framework's credibility depends on visible willingness to retract. Internal incidents handled transparently strengthen the defense layer; internal incidents hidden weaken it.

---

## What this protocol is not

- **Not a threat policy.** The protocol leads with friendly contact and proportionate escalation precisely because most engagement is honest. The escalation paths exist so that the response is calibrated, not so that the framework defaults to confrontation.
- **Not legal advice.** Where legal action is mentioned, it is the trigger to consult counsel, not the action itself. The author is not a lawyer and does not provide legal guidance through this document.
- **Not a substitute for license terms.** The license (`LICENSE`, `ATTRIBUTION_REQUIREMENTS.md`) is the operative legal instrument. This protocol describes how the author intends to respond when license terms are violated.
- **Not a perfectionism trap.** Nobody attributes everything perfectly. The protocol is designed to distinguish honest oversight from substantive capture, and to respond proportionately to each.

---

## Standing decisions, made now

To prevent in-the-moment overreaction:

1. **No legal threats made publicly without prior counsel review.** No exceptions.
2. **No public response to high-severity incidents within 48 hours of awareness.** Cooling period mandatory. Personal safety check + counsel first.
3. **No emotional public response under any class.** All public statements, even high-severity, are factual register: timeline, evidence, requested action. No characterizations of motive.
4. **No private retaliation.** No targeting of the appropriating entity's other work, no involvement of personal networks for adversarial purposes, no behind-the-scenes campaigns. The framework wins by being correct and well-attributed, not by being feared.
5. **No abandoning the work in response to capture.** A successful capture attempt is, perversely, evidence the work has value worth capturing. The response is to strengthen attribution and continue, not to retreat.
6. **Default to documentation over confrontation.** Every incident, regardless of class, is documented in detail before any response. The record is the asset; the confrontation is sometimes optional.

---

## What to do if you (a third party) become aware of misappropriation

If you are reading this because you've encountered work that appears to silently capture the Codex:

1. Confirm the overlap is substantive, not superficial. Terminology overlap alone is not capture.
2. Check the timeline — the canonical record is in this repository's commit history and the 1,402-page archive.
3. If the overlap appears substantive and uncited, contact the author at the email in `CITATION.cff`. Provide the link and your assessment. Your contact is helpful, not intrusive.
4. Public escalation by third parties is welcome but not required. The author's preference is that the incident reach the author first, then the response is calibrated per this protocol.

The framework's reputation is partly held by its community of attribution-respectful readers. Thank you for being one.

---

## Maintenance

This document is updated when (a) an incident occurs that the protocol did not anticipate, (b) jurisdictional or platform changes affect the response options, (c) the framework's licensing or attribution terms change. Updates follow the same `EVIDENCE_LADDER` discipline as the framework's claims.

**Audit trail:** added in D-1.1 (D2) to address misappropriation risk identified in defense planning. Companion to `CONFLICT_OF_INTEREST.md` (B6) — the disclosure surface; this is the response surface.
