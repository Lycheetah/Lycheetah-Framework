"""Re-run preserved v2.0/v2.1 suites plus endpoint-specific v2.2 tests."""
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
R10 = HERE / "r10_evidence_lease_v2_0"
R11 = HERE / "r11_provider_contracts_v2_1"
R12 = HERE / "r12_stripe_refund_contract_v2_2"
sys.path[:0] = [str(R10), str(R11), str(R12)]
MODULES = [
    "test_r9_baseline_regression",
    "test_evidence_lease_integration",
    "test_provider_contract",
    "test_recovery_policy",
    "test_stripe_refund_recovery",
]
suite = unittest.defaultTestLoader.loadTestsFromNames(MODULES)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
