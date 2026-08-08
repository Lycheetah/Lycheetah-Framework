# 03_aura_benchmark Report

**Command (dry run with temp results)**
```bash
python - <<'PY'
import sys, tempfile, pathlib, benchmark_runner
temp_dir = pathlib.Path(tempfile.gettempdir()) / 'aura_benchmark_results'
temp_dir.mkdir(parents=True, exist_ok=True)
benchmark_runner.RESULTS_DIR = temp_dir
benchmark_runner.LEADERBOARD_PATH = temp_dir / 'leaderboard.yaml'
sys.argv = ['benchmark_runner.py', '--dry-run']
benchmark_runner.main()
PY
```

**Result**
- All 20 mini-benchmark tests registered as “SKIPPED (dry run)” with TES/VTR/PAI/RC/DC = 0.0 and composite score = 0.0.  
- Output saved to `%TEMP%` and removed after the run.

**Notes**
- Dry run avoids API calls; a real run still requires valid Anthropic/OpenAI keys and network access.  
- FastAPI/uvicorn/pydantic installation previously failed on this Python runtime, so running the live benchmark may need a different environment.
