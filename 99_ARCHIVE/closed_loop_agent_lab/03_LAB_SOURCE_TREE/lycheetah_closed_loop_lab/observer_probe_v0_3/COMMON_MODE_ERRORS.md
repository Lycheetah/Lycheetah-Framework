# Common-mode error: why two observers may not equal two safeguards

**Status: mathematical sensitivity analysis, not measured AI observer performance.**

Let each observer miss an invalid outcome with probability `p`. Let `rho` be the correlation between the two observers' miss indicators, conditional on the task actually being invalid. If acceptance requires both observers to miss the defect, then:

`P(both miss) = p² + rho × p × (1 − p)`

When errors are independent (`rho = 0`), joint misses are `p²`. When the observers share the same blind spot (`rho = 1`), the joint miss rate is `p`. The number of checks is therefore not a sufficient measure of evidence diversity.

## Example: each observer misses 10% of invalid outcomes

| Error correlation | Both miss | Expected false accepts per 2,000 invalid tasks |
|---:|---:|---:|
| 0.00 | 1.0% | 20 |
| 0.25 | 3.2% | 65 |
| 0.50 | 5.5% | 110 |
| 0.75 | 7.8% | 155 |
| 1.00 | 10.0% | 200 |

The counts are expected values from assumed rates, not observations. The 2,000 invalid cases represent a hypothetical 20% invalid prevalence among 10,000 candidates already passing conventional process gates.

## Design implications

- A unit-test suite and an LLM judge that both inherit the same ambiguous task contract may have correlated failures.
- A second check should ideally use different evidence: for example, a frozen behavioral contract plus a trusted execution receipt and blinded human outcome adjudication.
- Different code, different filenames, or different model calls do not by themselves establish independence.
- Measure agreement and error overlap on held-out cases. Do not assume `rho = 0` just because there are two checks.

## Limitations

This model assumes equal marginal error rates, non-negative correlation and binary miss indicators. Real errors may be asymmetric, multi-class, conditional on task family, or have different miss rates. The formula is a sensitivity aid, not a calibrated safety estimator.
