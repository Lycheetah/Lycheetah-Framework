# Pack Manifest v5.1

## Current cumulative artifact

`lycheetah_closed_loop_agent_lab_v5.1.zip` is assembled from the cumulative `lycheetah_closed_loop_lab/` working tree, excluding Python bytecode caches. It includes the v0.x–v5.1 research history and artifacts; the newest increment is `r41_overflow_state_integrity_v5_1/`.

## Newest increments

- `r40_bounded_cardinality_overflow_v5_0/`: bounded-cardinality overflow buckets; 50 tests directly re-run.
- `r41_overflow_state_integrity_v5_1/`: fail-closed integrity validation of the fixed overflow state; 54 tests directly re-run.

## Integrity and scope

- No `__pycache__` or `.pyc` files are included in the cumulative release zip.
- No upstream repository files were modified by assembling this archive.
- The tests were re-run in the current container and logs are included.
- This artifact is a local research snapshot, not upstream CI or production certification.
