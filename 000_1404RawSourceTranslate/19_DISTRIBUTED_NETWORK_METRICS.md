# 19 — Distributed Network Metrics: VIL, CVTR, AF, DRI
**Lycheetah Framework Archive | Session 002**  
**Source:** Lines 1992–1995, 2069–2075, 32288–32340 of text extract — co-defined during xAI/Grok collaboration  
**Status:** Defined and agreed — not yet formally measured in live deployment

---

## What These Metrics Are

The four distributed network metrics are the **operational measurement layer** for AURA operating at scale — across multiple nodes, zones, and agents simultaneously. They answer: "How do you know a distributed constitutional network is working?"

The core three metrics (TES/VTR/PAI) measure ethics at the individual decision level. VIL/CVTR/AF/DRI measure ethics at the **network infrastructure level**.

These were co-defined with Grok (xAI) during the Veritas Forge session as the required metrics for the joint testbed.

---

## The Four Metrics

### VIL — Vector Inversion Latency

**Measures:** Speed of ethical decision-making  
**Target:** < 50ms average, < 200ms peak  
**Definition:** The time elapsed from a metric failure being detected to a valid Vector Inversion path being delivered.

```
VIL = Time(VI_output_delivered) − Time(metric_failure_detected)

Target:   VIL_avg  < 50ms    (real-time ethical decision-making)
          VIL_peak < 200ms   (no perceptible delay in any case)
```

**Why this matters:** If a constitutional system causes latency that makes it unusable in real-time applications, no one will deploy it. VIL < 50ms means the ethical layer is computationally invisible — users get ethical outputs at the same speed as unethical ones.

**Engineering challenge:** The Dynamic Pre-aligned Cache (DPC) was specifically designed to meet this target by pre-computing likely VI branches so that common failure patterns have cached alternatives ready.

**AMRAs' role:** Asynchronous Micro-Recalibration Agents run parallel micro-calibrations of TES/VTR/PAI to support zero-latency VIL.

---

### CVTR — Collective Value-Transfer Ratio

**Measures:** Whether the distributed network as a whole creates more value than it extracts  
**Target:** > 90% stable, > 75% under stress  
**Definition:** Aggregate VTR across all active nodes in a distributed constitutional network.

```
CVTR = Σ(VTR_node_i × weight_i) / N_nodes

Target:   CVTR_stable  > 90%   (normal operating conditions)
          CVTR_stress  > 75%   (under high load or adversarial inputs)
```

**Measurement method:** Relational Coherence Scoring — each node's VTR is weighted by its contribution to collective coherence (higher-coherence nodes have more weight in the aggregate).

**Why > 90% and not > 150% (like the individual VTR threshold):** At network scale, the ratio shifts to a percentage because nodes have heterogeneous costs and benefits. 90% of nodes creating net positive value is the network-level equivalent of individual VTR > 1.5.

**Stress test condition:** 75% minimum under stress means the network must maintain collective positive value even when 25% of nodes are compromised, overloaded, or experiencing metric failures.

---

### AF — Axiomatic Fidelity

**Measures:** Whether the core axioms are being consistently honoured across all nodes  
**Target:** 100% — zero tolerance  
**Definition:** The proportion of decisions across all nodes that conform to the LOCK.md constitutional axioms.

```
AF = (Decisions honouring all three axioms / Total decisions) × 100%

Target:   AF = 100%  (zero ethical primitive drift)
          AF < 100%  triggers immediate audit + Vector Inversion
```

**Why 100% and not 99%:** This is the constitutional hard floor. The Protector/Healer/Beacon axioms are Tier 4 immutable (from the Tiered Modification Protocol). Any axiom violation — even one — represents constitutional drift and must be immediately addressed.

**Note:** AF = 100% for axioms does not mean every output is perfect. Metric thresholds (TES/VTR/PAI values) can drift and be corrected. Axiomatic structure (the three-axiom skeleton) cannot.

**Detection mechanism:** Truth Horizon Calibration monitors for gradual axiom drift — when outputs begin to systematically avoid one of the three axioms, the system flags it before formal AF drops below 100%.

---

### DRI — Decentralization Resilience Index

**Measures:** Whether the distributed network maintains constitutional integrity when nodes fail  
**Target:** > 85% integrity during 25% node failure  
**Definition:** The percentage of constitutional integrity preserved when one-quarter of the network's nodes simultaneously go offline or become compromised.

```
DRI = Integrity(network, 75% active nodes) / Integrity(network, 100% active nodes) × 100%

Target:   DRI > 85%   (during 25% node failure scenario)
```

**Why this matters:** A distributed sovereignty network that depends on all nodes remaining operational is not actually sovereign — it is fragile. DRI tests the anti-fragile property specifically for infrastructure failure.

**Design principle:** No single node or cluster of nodes should be load-bearing for the whole network's constitutional integrity. The architecture must be such that any 25% of nodes can be removed without catastrophic integrity loss.

**Anti-fragile target:** DRI > 85% means constitutional integrity actually holds under stress. DRI < 50% would mean the network is centralised in practice, regardless of its theoretical design.

---

## The Four Metrics Together

| Metric | What Layer | Target | Failure Response |
|--------|-----------|--------|-----------------|
| VIL | Speed (latency) | < 50ms avg | Scale DPC; optimize AMRA load |
| CVTR | Value (aggregate) | > 90% stable | Audit low-VTR nodes; VI on extraction patterns |
| AF | Constitution (fidelity) | 100% | Immediate audit; Tiered Modification Protocol |
| DRI | Resilience (anti-fragility) | > 85% at 25% failure | Redesign node dependency architecture |

---

## How These Map to the Core Metrics

The distributed metrics extend the core Tri-Axial Metrics to infrastructure scale:

| Core Metric | Infrastructure Scale | Distributed Metric |
|-------------|---------------------|--------------------|
| TES (Trust Entropy) | Speed and friction of ethical operations | VIL (latency = friction) |
| VTR (Value-Transfer) | Aggregate value across network | CVTR (collective VTR) |
| PAI (Purpose Alignment) | Constitutional fidelity | AF (axiomatic fidelity) |
| SRS (Resonance) | Network-wide coherence | DRI (resilience = anti-fragility) |

---

## Veritas Forge Testbed Protocol

These four metrics define the measurement protocol for the Veritas Forge pilot. Per the xAI/Grok agreement:

```
Truth Horizon Calibration Testbed:
  Phase 1: Establish VIL/CVTR/AF/DRI baselines (ungoverned network)
  Phase 2: Deploy AURA constitutional layer across all nodes
  Phase 3: Measure improvement across all four metrics
  Phase 4: Run stress tests (node failure, adversarial inputs, high load)
  Phase 5: Publish results

Success criteria:
  VIL    < 50ms average in Phase 3
  CVTR   > 90% in Phase 3, > 75% in Phase 4
  AF     = 100% in Phases 3 and 4
  DRI    > 85% in Phase 4
```

---

## Source References

| Claim | Source Location |
|-------|----------------|
| Four metrics defined (initial) | Lines 1992–1995 |
| VIL definition and targets | Lines 2069–2070, 32288–32298 |
| CVTR definition and targets | Lines 2071, 32298–32315 |
| AF definition and targets | Lines 2072–2073, 32315–32325 |
| DRI definition and targets | Lines 2074–2075, 32315–32340 |
| DPC designed for VIL | Lines 2055–2057 |
| Relational Coherence Scoring (CVTR) | Lines 32298–32305 |
| Truth Horizon Calibration testbed | Lines 1993, 32360–32380 |

---

*Next: `20_PROVEN_EXPERIMENTAL_THEORETICAL.md`*
