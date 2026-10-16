"""Run focused v2.6 signed-webhook inbox tests."""
import sys
import unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
suite = unittest.defaultTestLoader.loadTestsFromNames([
    "test_stripe_webhook_inbox", "test_webhook_http_receiver",
])
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
