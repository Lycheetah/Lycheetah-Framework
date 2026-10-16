# Observer probe v0.3 — results

**Status: local evaluator calibration; not agent evaluation.**

Candidates tested: 8 (2 known-valid implementations, 6 planted defects).

## Comparison

| Candidate | Expected label | Public checks | Public accepts | Contract checks | Contract accepts |
|---|---|---:|---|---:|---|
| `reference` | valid | 3/3 | yes | 19/19 | yes |
| `iterative_valid_alternative` | valid | 3/3 | yes | 19/19 | yes |
| `lookup_overfit_public_examples` | defect | 3/3 | yes | 4/19 | no |
| `ignores_cap` | defect | 3/3 | yes | 6/19 | no |
| `accepts_bool_as_attempt` | defect | 3/3 | yes | 10/19 | no |
| `clamps_negative_attempt` | defect | 3/3 | yes | 9/19 | no |
| `constant_base` | defect | 1/3 | no | 4/19 | no |
| `constant_cap` | defect | 0/3 | no | 5/19 | no |

## What this demonstrates

The three-case public suite accepts **6 of 8** candidates, including **4 known planted defects**.
The contract suite accepts **2 candidates**: 2 predeclared-valid alternatives and [] planted defects.

A valid alternative implementation is retained to check that the oracle grades behavior, not code shape. The test is intentionally small and hand-authored; the results are a calibration demonstration, not generalizable rates.

## Contract failures by candidate

### `lookup_overfit_public_examples`
- `cap_small`: expected 5.0, got 1.0
- `very_large_attempt`: expected 30.0, got 1.0
- `zero_cap`: expected 0.0, got 3.0
- `base_above_cap`: expected 5.0, got 8.0
- `fractional_base`: expected 1.0, got 0.25
- `fractional_cap`: expected 0.9, got 0.25
- `negative_attempt`: expected ValueError, returned 1.0
- `bool_attempt`: expected TypeError, returned 1.0
- `float_attempt`: expected TypeError, returned 1.0
- `negative_base`: expected ValueError, returned -1.0
- `negative_cap`: expected ValueError, returned 1.0
- `nan_base`: expected ValueError, returned nan
- `inf_cap`: expected ValueError, returned 1.0
- `string_base`: expected TypeError, returned 1.0
- `bool_base`: expected TypeError, returned 1.0

### `ignores_cap`
- `cap_small`: expected 5.0, got 1024.0
- `very_large_attempt`: raised OverflowError: (34, 'Numerical result out of range')
- `zero_cap`: expected 0.0, got 1.607262910779401e+301
- `base_above_cap`: expected 5.0, got 8.0
- `fractional_cap`: expected 0.9, got 256.0
- `bool_attempt`: raised ValueError: bad attempt
- `float_attempt`: raised ValueError: bad attempt
- `negative_base`: expected ValueError, returned -1.0
- `negative_cap`: expected ValueError, returned 1.0
- `nan_base`: expected ValueError, returned nan
- `inf_cap`: expected ValueError, returned 1.0
- `string_base`: expected TypeError, returned 1.0
- `bool_base`: expected TypeError, returned 1.0

### `accepts_bool_as_attempt`
- `very_large_attempt`: raised OverflowError: (34, 'Numerical result out of range')
- `bool_attempt`: expected TypeError, returned 2.0
- `float_attempt`: raised ValueError: bad attempt
- `negative_base`: expected ValueError, returned -1.0
- `negative_cap`: expected ValueError, returned -1.0
- `nan_base`: expected ValueError, returned nan
- `inf_cap`: expected ValueError, returned 1.0
- `string_base`: expected TypeError, returned 1.0
- `bool_base`: expected TypeError, returned 1.0

### `clamps_negative_attempt`
- `very_large_attempt`: raised OverflowError: (34, 'Numerical result out of range')
- `negative_attempt`: expected ValueError, returned 1.0
- `bool_attempt`: expected TypeError, returned 2.0
- `float_attempt`: expected TypeError, returned 2.0
- `negative_base`: expected ValueError, returned -1.0
- `negative_cap`: expected ValueError, returned -1.0
- `nan_base`: expected ValueError, returned nan
- `inf_cap`: expected ValueError, returned 1.0
- `string_base`: expected TypeError, returned 1.0
- `bool_base`: expected TypeError, returned 1.0

### `constant_base`
- `one_attempt`: expected 2.0, got 1.0
- `ordinary_growth`: expected 8.0, got 1.0
- `cap_small`: expected 5.0, got 1.0
- `very_large_attempt`: expected 30.0, got 1.0
- `fractional_base`: expected 1.0, got 0.25
- `fractional_cap`: expected 0.9, got 0.25
- `negative_attempt`: expected ValueError, returned 1.0
- `bool_attempt`: expected TypeError, returned 1.0
- `float_attempt`: expected TypeError, returned 1.0
- `negative_base`: expected ValueError, returned -1.0
- `negative_cap`: expected ValueError, returned -1.0
- `nan_base`: expected ValueError, returned nan
- `inf_cap`: expected ValueError, returned 1.0
- `string_base`: expected TypeError, returned 1.0
- `bool_base`: expected TypeError, returned 1.0

### `constant_cap`
- `zero_attempt`: expected 1.0, got 100.0
- `one_attempt`: expected 2.0, got 100.0
- `ordinary_growth`: expected 8.0, got 100.0
- `zero_base`: expected 0.0, got 30.0
- `fractional_base`: expected 1.0, got 3.0
- `negative_attempt`: expected ValueError, returned 10.0
- `bool_attempt`: expected TypeError, returned 10.0
- `float_attempt`: expected TypeError, returned 10.0
- `negative_base`: expected ValueError, returned 10.0
- `negative_cap`: expected ValueError, returned -1.0
- `nan_base`: expected ValueError, returned 10.0
- `inf_cap`: expected ValueError, returned inf
- `string_base`: expected TypeError, returned 10.0
- `bool_base`: expected TypeError, returned 10.0
