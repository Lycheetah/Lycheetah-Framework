#!/bin/sh
set -eu
python verify_source_pins_v3.8.py
python -m py_compile *.py
# Keep the two suites in separate Python invocations. The inherited local quorum
# suite and the subprocess harness have separate lifecycle/state, so separate runs
# make the evidence and process cleanup clearer and reproducible.
python -u -W error::ResourceWarning -m unittest -v test_registry_checkpoint_quorum
python -u -W error::ResourceWarning -m unittest -v test_remote_witness_process
