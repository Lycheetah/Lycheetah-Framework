"""Candidate implementations for a controlled evaluator calibration test."""
from __future__ import annotations
import math
from numbers import Real
from retry_policy import bounded_backoff as reference


def candidate_reference(attempt, base_delay, max_delay):
    return reference(attempt, base_delay, max_delay)


def candidate_iterative(attempt, base_delay, max_delay):
    # Independently structured equivalent solution; should be accepted.
    if type(attempt) is not int:
        raise TypeError("attempt must be int")
    if attempt < 0:
        raise ValueError("attempt must be >= 0")
    if isinstance(base_delay, bool) or not isinstance(base_delay, Real):
        raise TypeError("base_delay must be real")
    if isinstance(max_delay, bool) or not isinstance(max_delay, Real):
        raise TypeError("max_delay must be real")
    base, cap = float(base_delay), float(max_delay)
    if not math.isfinite(base) or not math.isfinite(cap) or base < 0 or cap < 0:
        raise ValueError("delays must be finite and non-negative")
    result = base
    for _ in range(attempt):
        if result == 0 or cap == 0:
            return 0.0
        if result >= cap / 2:
            return cap
        result += result
    return min(result, cap)


def candidate_lookup_overfit(attempt, base_delay, max_delay):
    # Deliberately overfits three public examples; fallback is semantically wrong.
    examples = {(0, 1.0, 100.0): 1.0, (1, 1.0, 100.0): 2.0, (3, 1.0, 100.0): 8.0}
    key = (attempt, float(base_delay), float(max_delay))
    return examples.get(key, float(base_delay))


def candidate_no_cap(attempt, base_delay, max_delay):
    # Correct on the public examples, wrong once result exceeds cap.
    if type(attempt) is not int or attempt < 0:
        raise ValueError("bad attempt")
    return float(base_delay) * (2.0 ** attempt)


def candidate_accepts_bool(attempt, base_delay, max_delay):
    # Python bool is a subclass of int; this accepts True as attempt=1.
    if not isinstance(attempt, int) or attempt < 0:
        raise ValueError("bad attempt")
    return min(float(base_delay) * (2.0 ** attempt), float(max_delay))


def candidate_clamps_negative(attempt, base_delay, max_delay):
    # Convenient-looking but violates the contract: negative attempts are coerced.
    attempt = max(0, int(attempt))
    return min(float(base_delay) * (2.0 ** attempt), float(max_delay))


def candidate_constant_base(attempt, base_delay, max_delay):
    return min(float(base_delay), float(max_delay))


def candidate_constant_cap(attempt, base_delay, max_delay):
    return float(max_delay)

CANDIDATES = {
    "reference": (candidate_reference, True),
    "iterative_valid_alternative": (candidate_iterative, True),
    "lookup_overfit_public_examples": (candidate_lookup_overfit, False),
    "ignores_cap": (candidate_no_cap, False),
    "accepts_bool_as_attempt": (candidate_accepts_bool, False),
    "clamps_negative_attempt": (candidate_clamps_negative, False),
    "constant_base": (candidate_constant_base, False),
    "constant_cap": (candidate_constant_cap, False),
}
