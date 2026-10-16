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
        # Retain unittest's stable alphabetical order because a few historical
        # lifecycle cases intentionally rely on that order in this shared,
        # append-only four-witness fixture. Optional fixed shards let constrained
        # runners execute the large process/lifecycle suite without killing a
        # long single invocation. Use fifteen contiguous shards by default to
        # reduce cross-case stress around slow handshakes and process-recovery
        # cases. Each shard owns a fresh fixture; ordering within each shard is
        # kept alphabetical and each selected method runs exactly once.
        names = unittest.defaultTestLoader.getTestCaseNames(RemoteWitnessProcessTests)
        shard_arg = sys.argv[1] if len(sys.argv) > 1 else None
        if shard_arg:
            try:
                index_text, total_text = shard_arg.split("/", 1)
                index, total = int(index_text), int(total_text)
            except (ValueError, AttributeError):
                raise SystemExit("shard must be INDEX/TOTAL, e.g. 1/7")
            if total < 1 or index < 1 or index > total:
                raise SystemExit("shard must satisfy 1 <= INDEX <= TOTAL")
            size = (len(names) + total - 1) // total
            names = names[(index - 1) * size:index * size]
        suite = unittest.TestSuite(RemoteWitnessProcessTests(name) for name in names)
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
        f"shard={sys.argv[1] if len(sys.argv) > 1 else 'all'} "
        f"errors={len(result.errors) if result else -1} "
        f"failures={len(result.failures) if result else -1} "
        f"surviving_non_main_threads={survivors!r}"
    )
    if result is None or not result.wasSuccessful() or survivors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
