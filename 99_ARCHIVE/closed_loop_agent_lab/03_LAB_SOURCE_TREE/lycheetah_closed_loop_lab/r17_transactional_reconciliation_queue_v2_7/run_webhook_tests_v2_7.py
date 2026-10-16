"""Run signed webhook, loopback receiver, and transactional queue tests."""
import sys
import unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
suite = unittest.defaultTestLoader.loadTestsFromNames([
    "test_stripe_webhook_inbox",
    "test_webhook_http_receiver",
    "test_transactional_reconciliation_queue",
])
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
