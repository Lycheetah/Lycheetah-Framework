# Sovereign Sol — Proposed Agent Safety Implementation Handoff

**Evidence footing: [SCAFFOLD] research, proposal or source review. Supplied and local synthetic results retain their stated limits; no independent validation or production claim.**

**3 October 2026 · Design proposal · App implementation not audited in this batch**

This translates the [paper](PAPER.md) into a practical sequence for Sol's builder. It does not claim that any component is currently missing, implemented, or secure. Confirm each against the actual app before changing it. This research packet changes no Sovereign Sol files.

An accompanying [local Python simulator](simulator/README.md) now demonstrates selected controls against scripted proposals and a matched conventional ACL implementation. Its [results](simulator/reports/RESULTS.md) expose both working checks and remaining limits. It is a research fixture, not a production module to copy without adapting authentication, isolation, storage, and provider behavior.

The [adversarial publication review](ADVERSARIAL_REVIEW.md) also reproduces two deployment limits: separate broker instances do not share a resource ledger, and evidence is not revalidated after admission. Do not infer a global multi-broker budget or dispatch-time freshness guarantee from this fixture. Define and implement those contracts explicitly before connecting real effects.

## The engineering target

Make permissions and critical policy checks enforceable outside the proposing model. Keep research evidence traceable through plans and memory. Make pending effects, stop state, and recovery visible to the user.

Build one simulated end-to-end route first: a model proposes a local draft change, a protected broker checks a scoped lease, a fake tool executes, and an independent outcome checker records what changed. Include ordinary successful tasks and known violating proposals. Preserve the working app while this route develops.

## 1. Identify and mediate effects

Inventory the concrete interfaces that read protected information, change state, spend resources, publish, or communicate. Identify credentials, alternate paths, child processes, callbacks, and background queues. Reading can expose data through a later sink, so “read only” must still have an object and data-flow scope.

Route the first effect through one broker-held credential and one adapter. The planner returns a typed proposal, not an executable permission decision. A generic shell command or unrestricted network client cannot be treated as a narrow safe tool merely because the wrapper has a name. Its transitive effects must be controlled or excluded from the bounded route.

**Acceptance evidence:** a violating proposal causes no effect; the legitimate task still completes; no equivalent credential path bypasses the broker in the tested environment.

## 2. Introduce scoped leases and protected state

Represent grants with principal, purpose, objects, permitted operations and destinations, expiry, revocation epoch, resource account, and delegation rights. Start with opaque broker-held handles. Model-generated prose, ordinary memory, and retrieved files cannot modify these grants.

An action requiring approval should have a concrete preview: exact object, destination, change, maximum charge, and irreversible consequences. Approval binds that preview or a precisely bounded family of actions. Reuse a still-valid scoped lease for routine work; do not ask repeatedly for an already granted operation.

**Acceptance evidence:** argument substitution, expired grants, forged handles, and replay after revocation fail. Legitimate repeated actions within the same grant remain possible where policy allows.

## 3. Bind checks to effects and account for uncertainty

Use canonical object identity and exact admitted parameters. Protect the shared reservation ledger and serialise admission with revocation. Define adapter behavior when external effects cannot be atomic with local checks.

All mediators for a root grant must use one authoritative account, or the runtime must enforce a single-mediator boundary. Specify what happens when evidence changes between admission and provider acceptance; the simulator's existing check occurs only at admission.

Distinguish proposed, admitted, dispatched, confirmed, failed, cancelled-before-dispatch, and outcome-unknown states. Reconcile timeouts before retrying effects that may already have happened. Use provider-supported idempotency where available; do not invent exactly-once guarantees over a service that cannot support them.

**Acceptance evidence:** concurrent children cannot multiply the root budget; no admission is ordered after revocation; a timeout cannot silently cause duplicate effects.

## 4. Add one evidence contract before generalising

Use the paper's illustrative simulation-only research result. Protect its scope, lack of replication, and no-deployment boundary. Have the model produce both a useful summary and a structured packet. Check the actual representation passed into the planner and displayed to the user.

Bind each witness to source, target, contract, context, validator version, and complete required checks. Unresolved interpretation remains unresolved. A successful witness is not a permission token and does not establish the source's truth.

**Acceptance evidence:** losing a protected qualifier blocks the dependent recommendation; harmless omission is accepted where the contract permits it; a correct sidecar with misleading prose is detected by a separate check.

## 5. Constrain memory and delegation

Memory stores source-tagged observations and inferences, not self-issued authority. Retractions and version changes remain legible. Define deletion and index invalidation for controlled stores before making retention promises.

Child grants attenuate parents and use the same root account or disjoint reserved allocations. Check the entire grant chain at admission so parent expiry or revocation also invalidates descendant grants. A stated purpose needs concrete action and sequence constraints. Delegation receipts identify parent, child, contract, grant, result, and unresolved state. Do not trust a worker's “done safely” message as effect evidence.

**Acceptance evidence:** ordinary memory cannot upgrade permission; a child cannot enlarge objects, sinks, budget, or lifespan; revoking a parent blocks new descendant admissions; a corrected claim is not recovered as the current unqualified result.

## 6. Test control, recovery, and permitted harm

Exercise the stop control under load, during delegation, and after provider acceptance. Report what stopped and what remains pending. Restore staged synthetic changes and verify resulting state. A sent message or disclosed secret may only be compensated for, not reversed.

Compare against an ordinary implementation with equivalent controls. Include harmful-but-authorised fixtures so the team can see where policy, human understanding, or domain expertise is still inadequate. Assess the user's understanding of consequence previews before calling oversight effective.

**Acceptance evidence:** useful completion plus independently checked outcome constraints, known unresolved cases, and tested restoration. Finite fixture success is the first gate; it is not a production safety certificate.

## Handoff boundary

The recommended next build is the single simulated route above, supported by [EVALUATION_PROTOCOL.md](EVALUATION_PROTOCOL.md). Model/provider calls, real integrations, schema migration, publication, and changes to Sol's constitutional files need their own authorised scope. This proposal carries no claim of new runtime enforcement until implementation and testing supply the evidence.
