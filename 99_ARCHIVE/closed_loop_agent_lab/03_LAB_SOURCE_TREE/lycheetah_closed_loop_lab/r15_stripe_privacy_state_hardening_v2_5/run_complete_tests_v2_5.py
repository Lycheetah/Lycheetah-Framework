"""Run retained R10-R12 contract regressions with R15 hardened Stripe adapter tests."""
from pathlib import Path
import sys
import unittest
LAB = Path(__file__).resolve().parents[1]
R10 = LAB / "r10_evidence_lease_v2_0"
R11 = LAB / "r11_provider_contracts_v2_1"
R12 = LAB / "r12_stripe_refund_contract_v2_2"
R15 = Path(__file__).resolve().parent
sys.path[:0] = [str(R10), str(R11), str(R12), str(R15)]
modules = [
    "test_r9_baseline_regression",
    "test_evidence_lease_integration",
    "test_provider_contract",
    "test_recovery_policy",
    "test_stripe_refund_recovery",
    "test_stripe_test_adapter",
]
suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
