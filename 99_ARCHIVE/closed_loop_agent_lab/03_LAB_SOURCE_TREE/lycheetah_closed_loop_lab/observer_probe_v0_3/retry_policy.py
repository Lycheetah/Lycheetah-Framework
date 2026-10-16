"""Reference implementation for the evaluator-calibration microtask.

This is not a production retry library. It exists to test whether an evaluation
setup detects known defects without rejecting a correct alternative design.
"""
from __future__ import annotations
import math
from numbers import Real


def bounded_backoff(attempt: int, base_delay: Real, max_delay: Real) -> float:
    """Return zero-indexed exponential backoff, capped at max_delay.

    Contract:
    - attempt is an int but not bool, and must be >= 0.
    - base_delay and max_delay are finite, non-negative real values, but not bool.
    - returns float(min(base_delay * 2**attempt, max_delay)).
    - if the unbounded exponential would overflow, the cap still applies.
    - invalid types raise TypeError; negative or non-finite values raise ValueError.
    """
    if type(attempt) is not int:
        raise TypeError("attempt must be an integer, not bool")
    if attempt < 0:
        raise ValueError("attempt must be non-negative")

    def checked_float(value: Real, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"{name} must be a real number, not bool")
        try:
            result = float(value)
        except (OverflowError, ValueError) as exc:
            raise ValueError(f"{name} must be representable as a finite float") from exc
        if not math.isfinite(result):
            raise ValueError(f"{name} must be finite")
        if result < 0:
            raise ValueError(f"{name} must be non-negative")
        return result

    base = checked_float(base_delay, "base_delay")
    cap = checked_float(max_delay, "max_delay")
    if base == 0.0 or cap == 0.0:
        return 0.0
    if base >= cap:
        return cap

    value = base
    remaining = attempt
    # Stop after at most log2(cap/base) iterations, even for huge attempts.
    while remaining > 0 and value < cap:
        if value >= cap / 2.0:
            return cap
        value *= 2.0
        remaining -= 1
    return min(value, cap)
