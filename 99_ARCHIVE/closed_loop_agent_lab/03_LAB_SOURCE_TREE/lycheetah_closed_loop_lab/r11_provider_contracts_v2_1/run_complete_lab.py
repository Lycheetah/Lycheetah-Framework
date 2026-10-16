"""Re-run preserved v2.0 and current v2.1 suites; stdlib only."""
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
R10 = LAB / "r10_evidence_lease_v2_0"
R11 = HERE
sys.path[:0] = [str(R10), str(R11)]
MODULES = ["test_r9_baseline_regression", "test_evidence_lease_integration",
           "test_provider_contract", "test_recovery_policy"]
suite = unittest.defaultTestLoader.loadTestsFromNames(MODULES)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
