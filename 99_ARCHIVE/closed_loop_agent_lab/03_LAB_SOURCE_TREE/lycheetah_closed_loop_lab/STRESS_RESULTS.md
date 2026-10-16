# Observer sensitivity grid — results

**Status: ANALYTICAL SENSITIVITY SCENARIOS, NOT EMPIRICAL RESULTS.**

## What was run

`observer_stress.py` calculates expected decision counts across 72 combinations:

- 10,000 hypothetical tasks per combination;
- invalid-task prevalence 5%, 20%, or 50%;
- assumed observer sensitivity 50%, 70%, 80%, 90%, 95%, or 98%;
- assumed observer specificity 80%, 90%, 95%, or 98%;
- assumed 2% unknown rate on both valid and invalid tasks.

All rates are inputs. No LLM outputs, repository patches, benchmark tasks, or human-labeled observations were collected. Fractional expected counts are probability expectations, not literal fractional tasks and not Monte Carlo samples.

The baseline in this isolated model accepts every task that has already passed conventional process gates. This focuses on the extra observer only; it does not compare entire agent frameworks.

## One illustrative setting

Assume 20% of the already-green tasks are actually invalid; assume observer sensitivity is 90%, specificity is 95%, and both unknown rates are 2%.

| Expected result per 10,000 | Conventional baseline | Added observer |
|---|---:|---:|
| Invalid tasks automatically accepted | 2,000 | 160 |
| Invalid tasks blocked | 0 | 1,800 |
| Invalid tasks sent to review | 0 | 40 |
| Valid tasks automatically accepted | 8,000 | 7,600 |
| Valid tasks blocked | 0 | 240 |
| Valid tasks sent to review | 0 | 160 |
| Total new review load | 0 | 200 |

The observer is assumed to identify 90% of invalid tasks as `failed`, and another 2% as `unknown`; the remaining 8% are falsely marked `satisfied` and auto-accepted. On valid tasks, 95% are correctly accepted, 3% falsely blocked, and 2% sent for review.

This example illustrates the trade-off; it does **not** demonstrate that any current observer achieves these rates. The most important empirical task is to measure its false-negative and false-positive rates against independent, high-quality labels.

## Reproduce

```bash
python observer_stress.py
python -m unittest -v
```

Outputs: `observer_stress_results.json` and `observer_stress_grid.csv`.

## What the grid contributes—and doesn't

It makes three assumptions visible rather than hiding them inside one toy score: invalid-task prevalence, the observer's ability to detect invalid outcomes, and its ability to leave valid outcomes alone. It also counts `unknown` as review work rather than quietly treating review as success.

It does not estimate real rates, establish a universal threshold, model an error-prone human reviewer, or prove that task labels are trustworthy. The companion [Observer Validation Protocol](OBSERVER_VALIDATION_PROTOCOL.md) defines the work needed to measure those quantities.
