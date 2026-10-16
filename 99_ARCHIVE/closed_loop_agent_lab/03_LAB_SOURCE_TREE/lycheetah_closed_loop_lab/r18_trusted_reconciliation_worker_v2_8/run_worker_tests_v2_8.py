"""Focused R18 suite: webhook parser, HTTP receiver, queue and trusted worker."""
import unittest

if __name__ == "__main__":
    names = [
        "test_stripe_webhook_inbox",
        "test_webhook_http_receiver",
        "test_transactional_reconciliation_queue",
        "test_trusted_reconciliation_worker",
    ]
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for name in names:
        suite.addTests(loader.loadTestsFromName(name))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
