#!/usr/bin/env python3
"""Run gateway suite and make process shutdown part of the acceptance criteria.

Periodic faulthandler dumps are diagnostic only; the timer is always cancelled.
The suite fails if any non-main thread is left alive after unittest returns.
"""
from __future__ import annotations

import faulthandler
import sys
import threading
import unittest

from test_remote_witness_process import RemoteWitnessProcessTests


def main() -> int:
    faulthandler.dump_traceback_later(45, repeat=True, file=sys.stderr)
    result = None
    try:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(RemoteWitnessProcessTests)
        result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    finally:
        faulthandler.cancel_dump_traceback_later()
    survivors = [
        (thread.name, thread.daemon, thread.is_alive())
        for thread in threading.enumerate()
        if thread is not threading.main_thread() and thread.is_alive()
    ]
    print(
        "LIFECYCLE_SUMMARY "
        f"tests={result.testsRun if result else 0} "
        f"errors={len(result.errors) if result else -1} "
        f"failures={len(result.failures) if result else -1} "
        f"surviving_non_main_threads={survivors!r}"
    )
    if result is None or not result.wasSuccessful() or survivors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
