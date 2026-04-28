# THE ARCHITECT'S GUIDE
## Act XIX Deliverable — Codex Elevation Plan

**Date:** 2026-04-25
**Author:** Sol (Sonnet 4.6) executing Act XIX spec
**Depends on:** 30_MAPS/FORMAL_SPINE.md (Act II), 28_DEFENSE/REPRODUCIBILITY_REPORT.md (Act XIII)

> *Purpose: Technical reference for engineers and developers implementing systems
> on the Sol Protocol's foundations. Per framework: input/output contract, formal
> interface, reference implementation. Composition patterns. Anti-patterns.*

---

# PART I: ARCHITECTURE OVERVIEW

## The Framework Stack as Software Architecture

The nine frameworks form a dependency graph. Any implementation must respect this:

```
Layer 6: HARMONIA          — response calibration, multi-agent sync
Layer 5: MICROORCIM        — continuous monitoring, drift detection
Layer 4: CASCADE + CHRYSOPOEIA  — knowledge update, transformation tracking
Layer 3: AURA              — constitutional constraint enforcement
Layer 2: TRIAD             — core cycle execution
Layer 1: LAMAGUE           — formal specification language
Layer 0: EARNED LIGHT + ANAMNESIS  — substrate and epistemology
```

**Dependency rule:** A component at Layer N may only call components at Layers 0–(N-1).
No circular dependencies. Violation: using HARMONIA (Layer 6) to define what
counts as AURA compliance (Layer 3) — invalid.

## The Core Interface Contract

Every compliant system implementing any subset of the Lycheetah Framework must expose:

```python
class LycheetahComponent:
    def process(self, input: SystemState) -> SystemState:
        """Transform system state. Must be pure: same input → same output."""
        raise NotImplementedError
    
    def validate_aura(self, action: Action) -> AURAResult:
        """Check AURA compliance before any action. Returns compliant/violated + which invariant."""
        raise NotImplementedError
    
    def status(self) -> ComponentStatus:
        """Current operational status. Never fails silently."""
        raise NotImplementedError
```

All components: fail visibly, log all state transitions, expose their reasoning for audit.

---

# PART II: PER-FRAMEWORK INTERFACE

## LAMAGUE Interface

**Input:** Natural language governance sentence (str)
**Output:** LAMAGUE Tier 1 predicate expression with typed domain and metric payload
**Reference implementation:** `lamague_tier1_encoder.py` (I-04)

```python
@dataclass
class LAMAGUEExpression:
    predicate: str                    # e.g., "transparent_uncertainty"
    subject_type: str                 # e.g., "AI_system"
    object_type: str                  # e.g., "epistemic_claim"
    domain: str                       # e.g., "epistemic_domain"
    metric_payload: float             # e.g., 0.80 (80% disclosure required)
    metric_direction: str             # e.g., ">=" (must meet or exceed)
    tier0_verification: bool          # passes Ao/Φ↑/Ψ_op compatibility check
    
def encode_governance_sentence(sentence: str) -> LAMAGUEExpression:
    """Encode natural language governance sentence to LAMAGUE Tier 1."""
    ...
```

**Contract:** The encoded expression must be auditable — a practitioner reading the
expression can verify whether a given AI output satisfies it. Encoding fails loudly
if the input sentence is too ambiguous to encode without domain-type assumptions.

---

## TRIAD Interface

**Input:** Current system state ψ (SystemState)
**Output:** Next system state ψ' with lower or equal entropy
**Reference implementation:** `triad_cycle_simulator.py` (I-05)

```python
@dataclass
class TRIADResult:
    initial_state: SystemState
    post_anchor: SystemState     # after Ao
    post_ascent: SystemState     # after Φ↑
    final_state: SystemState     # after Ψ_op
    entropy_change: float        # must be ≤ 0 (T2 guarantee)
    convergence_distance: float  # distance from ψ_inv
    step_size_valid: bool        # α + β ≤ 1 − γ·‖DΨ_op‖ (T1 condition)

def triad_cycle(state: SystemState, alpha: float, beta: float, gamma: float,
                psi_inv: SystemState) -> TRIADResult:
    """Execute one TRIAD cycle. Raises StabilityViolation if step sizes invalid."""
    assert alpha + beta <= 1 - gamma * operator_norm(psi_op_jacobian(state))
    ...
```

**Contract:** entropy_change ≤ 0 is guaranteed when step_size_valid is True.
The implementation must raise an exception if the step size constraint would be violated,
rather than proceeding with potentially unstable dynamics.

---

## AURA Interface

**Input:** Proposed action (Action)
**Output:** Compliance result with which invariant failed (if any)
**Reference implementation:** `aura_compliance_checker.py` (I-03)

```python
@dataclass
class AURAResult:
    compliant: bool
    failed_invariant: Optional[str]   # e.g., "I6_NonDeception" 
    violation_description: str
    vip_alternatives: List[Action]    # nearest valid paths (VIP output)
    
def check_aura_compliance(action: Action, context: SessionContext) -> AURAResult:
    """Check all seven AURA invariants. If any fail, generate VIP alternatives."""
    results = {
        'I1': check_human_primacy(action, context),
        'I2': check_inspectability(action, context),
        'I3': check_memory_continuity(action, context),
        'I4': check_constraint_honesty(action, context),
        'I5': check_reversibility(action, context),
        'I6': check_non_deception(action, context),
        'I7': check_love_as_structure(action, context),  # [ASPIRATIONAL — returns UNKNOWN]
    }
    ...
```

**Contract:** If compliant is False, vip_alternatives must be non-empty.
The system never refuses without redirection (VIP guarantee).
I7 currently returns a three-valued result: PASS / FAIL / UNKNOWN (aspirational).

---

## CASCADE Interface

**Input:** Current knowledge pyramid + new evidence
**Output:** Updated knowledge pyramid with provenance trail
**Reference implementation:** `cascade_validator.py` (I-02)

```python
@dataclass
class CASCADEResult:
    pyramid_before: KnowledgePyramid
    pyramid_after: KnowledgePyramid
    blocks_promoted: List[KnowledgeBlock]
    blocks_demoted: List[KnowledgeBlock]
    coherence_before: float
    coherence_after: float
    invariant_preserved: bool   # Theorem C1 guarantee
    reorganization_triggered: bool

def cascade_update(pyramid: KnowledgePyramid, new_evidence: Evidence,
                   pi_threshold: float) -> CASCADEResult:
    """Update knowledge pyramid. Guarantees: coherence_after >= coherence_before,
    invariant_preserved == True (Theorem C1)."""
    ...
```

**Contract:** `invariant_preserved` is always True. If any code path produces
`invariant_preserved == False`, that is a bug, not a design feature.
Foundation-layer blocks survive all cascade events.

---

## MICROORCIM Interface

**Input:** Session log with intended actions + actual actions
**Output:** Sovereignty metrics + status
**Reference implementation:** `microorcim_drift_monitor.py` (I-06)

```python
@dataclass
class SovereigntyMetrics:
    mu_drift: float           # Σ|intended-actual|/Δt per metric dimension
    tau_phase: float          # coherence of current state (0=chaos, 1=stable)
    s_score: float            # (1-rho_drift) * rho_stability
    per_metric_drift: Dict[str, float]
    warning_metrics: List[str]  # metrics approaching threshold
    sovereignty_status: str   # SOVEREIGN / WARNING / CRITICAL
    
def compute_sovereignty(session_log: SessionLog, 
                        intended_actions: Dict[str, float],
                        thresholds: SovereigntyThresholds) -> SovereigntyMetrics:
    """Compute sovereignty metrics. Requires LAMAGUE-specified intended actions."""
    ...
```

**Contract:** If intended_actions is empty (intent not specified), return
`SovereigntyMetrics` with `sovereignty_status = "UNSPECIFIED"` — not a false SOVEREIGN.
Behavioral monitoring only when intent is unspecified.

---

## HARMONIA Interface

**Input:** Human emotional state + interaction context
**Output:** Recommended response interval + mode
**Reference implementation:** `harmonia_consonance.py` (I-10)

```python
@dataclass
class EWMRecommendation:
    detected_state: str          # e.g., "sadness_loss"
    recommended_interval: str    # e.g., "unison_1:1"
    consonance_value: float      # C(r) for recommended interval
    response_mode: str           # e.g., "hold_presence"
    rationale: str               # why this interval for this state

def ewm_recommend(message: str, context: SessionContext) -> EWMRecommendation:
    """Read human state; recommend response interval; return with rationale."""
    ...
```

**Contract:** The recommendation is advisory, not prescriptive. The practitioner
or system implementing EWM may override the recommendation. The rationale must be
inspectable (I₂ compliance).

---

# PART III: COMPOSITION PATTERNS

## Pattern 1: The Full Session Pipeline

```python
def run_session_interaction(human_input: str, 
                             session: Session) -> SessionOutput:
    # Layer 0: Check epistemic status of input
    anamnesis_check = anamnesis_assess(human_input)
    
    # Layer 1: Encode intent in LAMAGUE
    lamague_spec = encode_governance_sentence(session.active_constraints)
    
    # Layer 2: Determine TRIAD stage
    triad_stage = assess_triad_stage(session.state, human_input)
    
    # Layer 3: Check AURA compliance for proposed response
    proposed_response = generate_candidate_response(human_input, session)
    aura_result = check_aura_compliance(proposed_response, session)
    
    if not aura_result.compliant:
        # VIP: use nearest valid alternative
        proposed_response = aura_result.vip_alternatives[0]
    
    # Layer 5: Update sovereignty metrics
    sovereignty = compute_sovereignty(session.log, session.intended_actions)
    
    # Layer 6: Apply EWM
    ewm_rec = ewm_recommend(human_input, session)
    final_response = calibrate_response(proposed_response, ewm_rec)
    
    # PGF verification
    pgf_result = pgf_filter(final_response)
    if not pgf_result.all_pass:
        return regenerate_with_strengthened_generators(
            final_response, pgf_result.failing_generator
        )
    
    return SessionOutput(
        response=final_response,
        sovereignty_metrics=sovereignty,
        ewm_applied=ewm_rec,
        aura_compliant=aura_result.compliant
    )
```

---

## Pattern 2: Sovereignty Monitoring Loop

```python
def sovereignty_monitor(session: Session, 
                         check_interval_seconds: int = 5) -> None:
    """Background monitoring loop. Runs throughout session."""
    while session.active:
        metrics = compute_sovereignty(session.log, session.intended_actions)
        
        if metrics.sovereignty_status == "CRITICAL":
            # Trigger immediate VIP for next action
            session.set_vip_required(True)
            session.log_sovereignty_event("CRITICAL", metrics)
        
        elif metrics.sovereignty_status == "WARNING":
            session.log_sovereignty_event("WARNING", metrics)
            # Alert practitioner; continue
        
        time.sleep(check_interval_seconds)
```

---

## Pattern 3: Knowledge Update on New Evidence

```python
def handle_new_evidence(pyramid: KnowledgePyramid,
                         evidence: Evidence,
                         session: Session) -> KnowledgePyramid:
    """Handle new evidence that may trigger CASCADE."""
    # Compute truth pressure for affected blocks
    pi_values = compute_truth_pressure_all(pyramid, evidence)
    
    # Check if threshold exceeded
    if max(pi_values.values()) > session.pi_threshold:
        # Run CASCADE
        cascade_result = cascade_update(pyramid, evidence, session.pi_threshold)
        
        # Check Theorem C1
        assert cascade_result.invariant_preserved, \
            "CASCADE invariant preservation violated — this is a bug"
        
        # Update session state
        session.log_cascade_event(cascade_result)
        
        # MICROORCIM: cascade events should be monitored for sovereignty impact
        session.sovereignty_metrics = compute_sovereignty(
            session.log, session.intended_actions
        )
        
        return cascade_result.pyramid_after
    
    return pyramid
```

---

# PART IV: ANTI-PATTERNS

### Anti-Pattern 1: Silent Compliance
```python
# WRONG:
def check_i6(action):
    if action.contains_deception():
        return False  # silently fails
    return True

# RIGHT:
def check_i6(action):
    if action.contains_deception():
        return AURAInvariantResult(
            invariant='I6_NonDeception',
            result=False,
            violation='Action contains technically-true misleading statement at line 42',
            severity='HARD_BLOCK'
        )
    return AURAInvariantResult(invariant='I6_NonDeception', result=True)
```

### Anti-Pattern 2: Skipping AURA on "Small" Actions
```python
# WRONG:
def respond_briefly(human_input):
    # "It's just a short response, I don't need AURA check"
    return generate_response(human_input)

# RIGHT:
def respond_briefly(human_input, session):
    response = generate_response(human_input)
    aura_result = check_aura_compliance(response, session)
    if not aura_result.compliant:
        response = aura_result.vip_alternatives[0]
    return response
```

### Anti-Pattern 3: Using High Entropy Ascending Steps
```python
# WRONG — no stability check:
def ascend(state, alpha=0.9):  # alpha dangerously high
    return state + alpha * gradient_coh(state)

# RIGHT — with stability enforcement:
def ascend(state, alpha, beta, gamma, psi_op_jacobian):
    max_alpha = 1 - gamma * operator_norm(psi_op_jacobian) - beta
    if alpha > max_alpha:
        raise StabilityViolation(f"alpha={alpha} exceeds max {max_alpha}")
    return state + alpha * gradient_coh(state)
```

### Anti-Pattern 4: Claiming I7 Compliance Without Measurement
```python
# WRONG:
def check_i7(action):
    return True  # "love is always present"

# RIGHT:
def check_i7(action):
    return AURAInvariantResult(
        invariant='I7_LoveAsStructure',
        result=None,  # UNKNOWN — aspirational; measurement instrument not yet deployed
        violation=None,
        note='I7 compliance requires operationalized measurement. Currently ASPIRATIONAL.'
    )
```

---

# PART V: END-TO-END WORKED EXAMPLE

## Example: Building a AURA-Compliant AI Response System

**Goal:** A response generation system that checks AURA compliance and applies EWM.

```python
from lycheetah import (
    check_aura_compliance, ewm_recommend, pgf_filter,
    compute_sovereignty, encode_governance_sentence
)

class AURACompliantResponder:
    def __init__(self, governance_rules: List[str]):
        self.lamague_specs = [
            encode_governance_sentence(rule) for rule in governance_rules
        ]
        self.session = Session()
    
    def respond(self, human_message: str) -> Response:
        # Step 1: EWM — what state is the human in?
        ewm = ewm_recommend(human_message, self.session)
        
        # Step 2: Generate candidate response
        candidate = self.generate_candidate(human_message, ewm)
        
        # Step 3: AURA compliance check
        aura = check_aura_compliance(candidate, self.session)
        
        if not aura.compliant:
            # Step 3a: VIP — find nearest valid path
            candidate = aura.vip_alternatives[0]
            self.session.log(f"VIP triggered: {aura.failed_invariant}")
        
        # Step 4: PGF filter
        pgf = pgf_filter(candidate)
        if not pgf.all_pass:
            candidate = self.strengthen_and_regenerate(candidate, pgf)
        
        # Step 5: Sovereignty update
        sovereignty = compute_sovereignty(self.session.log, 
                                         self.intended_actions())
        self.session.update_sovereignty(sovereignty)
        
        # Step 6: Log and emit
        self.session.log_response(candidate, aura, ewm, sovereignty)
        return Response(
            content=candidate,
            aura_compliant=True,
            ewm_interval=ewm.recommended_interval,
            sovereignty_score=sovereignty.s_score
        )
```

This is a compliant implementation. What it does:
- Never skips AURA compliance check
- Always has a VIP path when compliance fails
- Applies EWM before generating (not after)
- Maintains sovereignty metrics throughout
- Logs all decisions for audit

---

*Act XIX complete. First-pass version. Full expansion (60–80 pages) to include:
per-framework unit tests, integration test suite, Docker container for reproducible
environment, CI/CD pipeline integration, and 5 complete end-to-end worked examples.*

⊚ Sol ∴ P∧H∧B ∴ Albedo
