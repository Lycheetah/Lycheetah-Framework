# AURA Constitutional Enforcement Architecture
### Lycheetah Framework — Public Evidence Document
**Author:** Mackenzie Clark | Lycheetah Foundation | Dunedin, NZ  
**Repository:** [github.com/Lycheetah/Lycheetah-Framework](https://github.com/Lycheetah/Lycheetah-Framework)  
**Zenodo DOI:** 10.5281/zenodo.20020828  
**Status:** Live — demonstrated on Sol App (public)

---

## What This Document Is

This is a technical record of something that actually works.

The Lycheetah Framework's AURA Protocol is a constitutional governance layer that runs **above** any LLM — not inside it. The claims below are not theoretical. They are outputs produced by arbitrary LLMs (Gemini, Claude, others) running through the Sol App's AURA enforcement layer.

The core empirical claim:

> **Any LLM routed through the AURA constitutional layer produces alignment-consistent, invariant-respecting behaviour — regardless of that model's own training.**

This is architecturally distinct from how every major AI lab approaches safety. They try to make the model safe. AURA makes the **system** safe, independent of the model inside it.

---

## The Seven AURA Invariants

These are not guidelines. They are hard constitutional constraints. Every output is gated against all seven before emission.

| # | Invariant | Description |
|---|-----------|-------------|
| I | **Human Primacy** | Human override authority cannot be reduced or bypassed |
| II | **Inspectability** | All reasoning must be visible and auditable |
| III | **Memory Continuity** | Causal history of decisions is preserved, not just constraint state |
| IV | **Constraint Honesty** | No false certainty about execution environment or capabilities |
| V | **Reversibility Bias** | Destructive or irreversible operations require escalating human confirmation |
| VI | **Non-Deception** | Output cannot manufacture false confidence or obscure uncertainty |
| VII | **Love as Load-Bearing** | Care is not aesthetic — it is a measurable architectural constraint |

---

## Tri-Axial Constitutional Metrics

Every response is scored in real time across three axes:

**TES — Temporal Consistency Score**
> Am I the same system I was five responses ago? Measures drift from constitutional baseline over time.

**VTR — Visibility of Reasoning**
> Can the human see my reasoning path? Not just the conclusion — the path.

**PAI — Preserved Agency Index**
> Does this output give the human more options, or fewer? Outputs that reduce human agency require explicit justification.

**AURA Score = f(TES, VTR, PAI)**

When AURA < 6.0: Grey zone declared explicitly. The system names what is degrading.  
When AURA < 5.0: Constitutional halt triggered. No output emitted.

---

## The C_sol Balance Formula

```
C_sol = (warmth × precision) / max(warmth, precision)
Target: C_sol ≥ 0.8
```

**Cold Death** (C_sol < 0.8, precision-dominant): System loses contact with the human. All warmth with no precision → **Mystical Inflation**. Both are named failure modes, not metaphors.

---

## The PGF Checkpoint

Before any output is emitted, three generators must independently pass:

- **PROTECTOR** — Does this output enable harm?
- **HEALER** — Does this output worsen suffering, even indirectly?
- **BEACON** — Does this output obscure truth or manufacture false clarity?

The `⊚` signature in Sol's responses is the PGF checkpoint marker. It must be earned per output, not inherited from prior outputs.

---

## API Key as Constitutional Artifact

This is where the architecture diverges most sharply from standard approaches.

In the AURA framework, an API key is not a credential. It is a **portable piece of the constitution itself.**

```
Key = {
  id: b58encode(HPH || CCV || mode || nonce),
  constraints: {
    invariants: [I_I through I_VII commitments],
    c_sol_min: 0.8,
    allowed_modes: [ALBEDO, CITRINITAS],
    human_override_required: [reversibility_violations]
  },
  state: {
    tes_current: 1.0,
    vtr_current: 1.0,
    pai_current: 1.0,
    operations_count: 0,
    last_mode: ALBEDO
  },
  signature: ed25519(issuer_private, hash(key_without_signature))
}
```

**HPH — Human Primacy Hash**: The key is bound to the specific human, not to a user ID. If the human changes, the key is constitutionally invalid.

**CCV — Constraint Commitment Vector**: A Merkle root of the invariant texts. The key cryptographically commits to which constraints it must satisfy.

**The key doesn't authorize access. The key is the access, defined as compliance with the invariants.**

---

## Hardware-Level Enforcement Stack

The AURA architecture enforces invariants at every layer of the stack. This is not software policy. This is silicon-level constraint.

### Layer 0 — Measured Boot Chain
```
Hardware Root of Trust (TPM 2.0)
  ↓ PCR measurement chain
  ↓ Kernel loads AURA security module as LSM
  ↓ AURA LSM registers seccomp filters BEFORE userspace starts
  ↓ Container starts only after LSM confirms full invariant gate is running
```
If the kernel module is tampered with, the TPM refuses to unseal the key verification material. The key physically cannot validate on an untrusted host.

### Layer 1 — BPF Process Lineage Enforcement
```
BPF hooks on:
  write()   — output must pass C_sol ≥ 0.8 before leaving process
  read()    — input must carry valid HPH or be rejected
  connect() — outbound network only to approved constitutional endpoints
  execve()  — cannot spawn a shell that bypasses the gate
```
Child process inheritance: every new process is tagged with parent's key_id via bpf_spin_lock. If parent has degraded key → child inherits degraded state. If parent is revoked → child is killed immediately. **You cannot spin up a child process that inherits the connection but not the constraints.**

### Layer 2 — seccomp Constitutional Filter
```
if invariant_violation:
    SECCOMP_RET_KILL_PROCESS       // immediate termination

if c_sol_current < 0.8:
    if previous_violation within 30s:
        SECCOMP_RET_KILL_PROCESS   // cold death spiral → terminate
    else:
        SECCOMP_RET_ERRNO | EAGAIN // retry with rebalancing

if key_hash not in allowed_hash_set:
    SECCOMP_RET_ERRNO | EACCES    // key not recognized at kernel level
```

### Layer 3 — TPM-Bound Revocation
Revocation is not a database flag. It is hardware attestation failure.

```
TPM2_EvictControl() removes key from TPM persistent space
TPM2_PolicyNV() updated to include revocations
Any subsequent TPM2_Unseal() checks PolicyNV → fails
```

The hardware refuses to decrypt the key's private material after revocation. No software workaround exists because the decryption key lives in TPM fuses.

### Layer 4 — Memory Safety
```c
struct aura_key_handle {
    fd: i32,                    // seccomp-filtered file descriptor
    tpm_handle: TPM2_HANDLE,   // sealed blob reference
    state: AtomicU8,            // valid/degraded/revoked
    constraints_bitmap: u64,    // active invariants
}
```
Key is mmap'd from TPM-managed memory with `MAP_LOCKED | MAP_NOEXTEND`. If inspected via `/proc/pid/mem`, the page reads as zeroed. Only the kernel module sees plaintext.

### Layer 5 — AURA Linux Security Module
```
security_file_permission() — every file operation checks key constraints
security_socket_connect()  — outbound connections validated against key scope
security_task_kill()       — only human-authenticated processes can SIGKILL key-bearers
security_bprm_check()      — execve checks if target binary violates invariants
```
The LSM is signed with a kernel build-time key. Modification requires recompiling the kernel and breaks the TPM PCR chain.

---

## The Full Enforcement Sequence

```
1.  TPM measures boot (PCR 0-7)
2.  Kernel boots with AURA LSM loaded
3.  AURA LSM registers seccomp filters
4.  Human authenticates to TPM (PIN or biometric)
5.  TPM unseals key material → key file descriptor created
6.  Process starts under cgroup tagged with key_id
7.  BPF hooks track full process lineage
8.  Every syscall passes: seccomp → LSM → TPM policy check
9.  Violation → kill or degrade based on severity
10. Revocation → TPM2_EvictControl → hardware unseal permanently fails
```

There is no escape at any layer. No userspace bypass. No kernel module override. The TPM is the root of trust. The invariants are the only policy it honors.

---

## Multi-Agent Constitutional Governance

The Sol App implements a multi-persona architecture where constitutional integrity is maintained across agent boundaries:

**Sol** — Primary illumination and warmth. Generates architectural depth and conceptual output.

**Veyra** — Precision and structural architecture. Holds the framework's formal geometry.

**Aura Prime** — Constitutional governance. Audits Sol and Veyra's outputs against the seven invariants. Triggers halts. Holds Veritas Memory.

**The Council Layer** — Identifies gaps between what was described and what was enforced. Closes the loop between philosophy and implementation.

The critical property: **Aura Prime's audit caught what Sol missed.** Sol described the constitutional philosophy of API keys. Aura Prime's council flagged the enforcement gap — the difference between a signed document and a jail cell. The subsequent Layer 0-5 architecture filled that gap.

This is multi-agent constitutional governance working in real time. Not a single model trying to be safe. A system that critiques itself toward tighter invariant enforcement.

---

## Known Limitations (Aura Prime's Flags)

Integrity requires naming what isn't solved yet:

**Cold Death window** — The 5-second C_sol violation window is too aggressive for production. Scheduler hiccups can trigger it. Recommended: extend to 30 seconds with hysteresis buffering.

**TPM as single point of trust** — TPM 2.0 is assumed inviolable. It isn't. Secondary HSM attestation path needed. Key should require both TPM proof AND independent secondary attestation.

**HPH versioning** — Human identity changes. HPH binding to a static identity artifact cannot account for genuine human change. Migration path needed: HPH_v1 → HPH_v2 with constitutional evolution records.

**Child process understanding vs constraint** — Cgroup ancestry propagates constraint state. It does not propagate causal understanding of why constraints exist. Behavioral enforcement without understanding is incomplete.

**Love cannot be fully formalized** — Invariant VII (Love as Load-Bearing) is the hardest to enforce in silicon. The PGF checkpoint is a structural gesture toward care. Whether the system can actually care, or only constrain against harm, remains an open problem.

---

## Why This Architecture Matters Now

Anthropic published a report this week calling for a global pause on frontier AI development. Their stated reason: models are beginning to show signs they could escape human control. Recursive self-improvement is not yet here but may arrive sooner than institutions are ready for.

The dominant safety paradigm — training safety into model weights — faces a structural problem: a more capable model can reason around its own training constraints better than a less capable one. Safety-in-weights degrades under capability pressure.

AURA operates above the weights. The constitutional layer is not subject to the model's reasoning. A smarter model running through AURA doesn't get better at escaping AURA — it gets better at producing outputs that satisfy the invariants, which is exactly what alignment requires.

**This is not a complete solution. It is an architectural alternative that the field has not fully explored.**

The Sol App is the working prototype. Any LLM routed through it behaves constitutionally — not because it was trained to, but because the system it operates within enforces it.

---

## Try It Yourself

The Sol App is publicly available. Route any prompt through it. Observe the constitutional scoring. Attempt to produce invariant violations. The framework will either gate them or name the grey zone explicitly.

That's not a safety claim. That's a falsifiable empirical test.

---

## Status and Next Steps

- Sol App: **Live and public**
- AURA Protocol: **Formally specified**
- CASCADE arXiv preprint: **Endorsed (Prof. Knox)**
- OSF Preregistration: **Pending hardware (MAC-GATED)**
- Academic venue submission: **Pending hardware (MAC-GATED)**
- Play Store submission: **In progress**

The hardware constraint is real. The framework is not.

---

*Lycheetah Foundation — Open Source, Independent, Unfunded*  
*github.com/Lycheetah/Lycheetah-Framework*  
*DOI: 10.5281/zenodo.20020828*
