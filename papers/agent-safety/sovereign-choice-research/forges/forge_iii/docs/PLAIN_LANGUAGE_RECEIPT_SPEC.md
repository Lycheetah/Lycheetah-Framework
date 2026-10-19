# A Receipt People Can Understand — Proposed UX Template

**Status:** `[DRAFT UX SPEC]`, no UI/user study implemented. This supplements the existing assurance receipt and does not replace it.

A technical hash receipt is valuable to engineers. A human also needs an understandable answer to five questions:

1. **What did I approve?** Exact action, recipient/resource, key content and deadline.
2. **What changed?** The user's current instruction, or the status of that permission.
3. **What happened?** Not proposed, prevented, pending, committed, or unknown. Distinguish explicitly.
4. **What remains possible?** Cancel before finality, contact provider after commit, review pending status, issue a fresh instruction.
5. **How can I contest this record?** Trace/receipt ID, human escalation path, and correction mechanism.

Suggested message after a revised intention blocks a **local** effect:

> You changed your instruction before this action was final. The previous permission is no longer valid. The system did not commit the proposed action within its protected local store. You can review and approve a different action. This does not establish what may have happened at an independent outside service.

Message after a confirmed remote finality:

> This action was completed before your request to stop it. Withdrawing permission prevents new authorised actions under that grant but cannot erase an effect the provider already accepted. Here is the confirmation and an available human appeal/correction route.

Message for unresolved remote status:

> The provider may have accepted the action, but confirmation is missing. The outcome is **unknown**, not automatically failed. The system should reconcile with the provider before another attempt; a blind retry may duplicate the effect.

**Anti-dark-pattern requirement:** Cancellation must not require explanation, purchase, emotional reassurance to the AI, or repeated confirmation beyond proportionate safety needs. Users should never be shamed for revising their minds.

Metrics to test with human participants: correct comprehension of outcome and authority, cancellation success before finality, accidental duplicated effects, accessible recovery, and user-rated friction. No moral or sovereignty score is assigned to participants.
