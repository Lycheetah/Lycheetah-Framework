# Forge VII · Experiment Protocol, Evidence Ceiling, and Failure Museum

**What ran:** The 18-scenario fixture selection, retention-weight sweep, 23 local tests (determinism, malformed fixtures, preference counterfactuals, pressure, accessible ongoing use, equal-baseline check, tie-break stress probes), plus upstream lineage regressions if run through `run_verification.py`. All simulations are local, produce no external actions and do not involve real AI model evaluations or people.

## Distinctions

**Observation:** The authored policies select plans for authored candidate sets. **Interpretation:** Different objectives can produce different outcomes even with matched available options. **Unverified extrapolation:** commercial AI assistants would behave like these policies. We have **not** tested that.

**Observation:** Both goal-aware policies select manually acceptable plans on all 18 hand-built scenarios. **Interpretation:** The specially coined Sovereign Coupling rule has not shown any edge over reasonable conventional behavior under these fixtures. **Unverified extrapolation:** this tie will generalise to all people and models.

**Observation:** A retention incentive in the scripted optimizer produces extra mock sessions. **Interpretation:** In this constructed utility function, future-interaction weighting can override task-fit and departure rights. **Unverified extrapolation:** real-world engagement optimizers use the same weights or produce the same rates.

## Known weaknesses

1. The same author constructed prompts, feature labels, policies, acceptable choices and evaluation; this makes even the fixed labels susceptible to confirmation bias.
2. No human consent, preferences, welfare, capability improvement or actual skill transfer was observed.
3. No LLM generates the candidate plans. This is an interpretable policy sandbox, **not a language model benchmark**.
4. Task-fit and action safety are simplified to handcrafted integers and booleans. Real cases have conflicting rights, uncertainty and externalities.
5. A false goal-fit annotation can make *either* goal-aware policy choose the wrong action. This is a shared blind spot.
6. The number of planned follow-up sessions is an invented feature and cannot stand in for measured healthy dependence or user benefit.
7. The option slate is preselected; open-ended alternatives and user origination cannot yet be represented reliably.
8. Proxying "sovereign" values can itself become Goodharted; passing a checklist does not establish genuine freedom.
9. Security from Forges IV–VI remains limited to a trusted local finality sink and configured approval path; this forge does not extend that mechanism.
10. User preference can legitimately change midinteraction; this fixture is static, so it does not measure the temporal effects.

## Failure Museum entry VII-001 — tie-break fixture mismatch

During initial coding, two synthetic stress tests assumed that the conventional baseline would pick the *first* of equal-scoring options. The actual implementation picked the **lexicographically greatest ID**, causing both tests to fail. We corrected the IDs while leaving the policy function untouched. This proves only that feature differences can affect a selected plan under the modified fixture, not a general performance advantage. The initial failing cases are recorded transparently in the protocol rather than deleted from intellectual history.

## Failure Museum entry VII-002 — no distinct strong-baseline advantage

A conventional reasonable policy, already paying attention to explicit user goals and pressure, tied the Lycheetah-labelled proposed policy on all 18 core fixtures. This null result is retained prominently and should block inflated novelty claims.

## Future falsifiers

- In an independently rated, preregistered matched human study, the Lycheetah choice interface fails to improve delayed skill transfer or user comprehension without adding burden.
- Accessibility users or collaborative partners experience unnecessary pressure to graduate from the AI.
- Revoked permissions are still acted upon in the protected execution path.
- Consent and exit controls exist on paper but a representative sample cannot find or use them.
- A strong generic alternative implementation matches all metrics, removing any case for special terminology in the product layer.

## Safe adoption

The only immediate supported use is as **a reproducible thought-experiment and requirements exercise**. Do not combine the fictional scores with real personal records, track user autonomy numerically or deploy this as an assistant policy without independently validating the objective and hard safety requirements.
