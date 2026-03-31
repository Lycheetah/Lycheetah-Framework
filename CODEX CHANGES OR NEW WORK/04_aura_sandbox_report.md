# 04_aura_sandbox Report

**Command (history query with temp DB)**
```bash
python - <<'PY'
import sys, tempfile, pathlib, aura_sandbox
temp_dir = pathlib.Path(tempfile.gettempdir()) / 'aura_sandbox_runs'
temp_dir.mkdir(parents=True, exist_ok=True)
aura_sandbox.DB_PATH = temp_dir / 'sandbox_runs.db'
aura_sandbox.RESULTS_DIR = temp_dir / 'results'
aura_sandbox.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.argv = ['aura_sandbox.py', 'history']
aura_sandbox.main()
PY
```

**Result**
- History command reports “No sandbox runs recorded yet”; the DB/res directory was kept in `%TEMP%` and removed afterward.

**Notes**
- Running `run`/`demo` requires a valid Anthropic/OpenAI API key and the same dependencies noted above are needed for back-end REST serving.  
- The module demonstrates the CLI entry point and confirms database connectivity.
