# Validation Record

## Structural validator

`validator.py` result:

**PASS — naming forge structural validation**

Checks include:
- exactly 72 unique semantic roots,
- exactly 18 unique Mantles,
- every Mantle references known roots,
- every Mantle has recovery/boundary/trial/shadow/reading,
- allowed title states are valid,
- devotion cannot be EARNED/WITNESSED by the School.

## Unit tests

**3 tests passed.**

The execution environment emitted an unrelated spreadsheet-runtime warmup warning before Python startup. It did not affect validator or unit-test outcomes.
