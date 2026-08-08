# 02_cascade_provenance Report

**Command (with temp DB)**
```bash
python - <<'PY'
import sys, tempfile, pathlib, provenance_checker
new_db = pathlib.Path(tempfile.gettempdir()) / 'cascade_demo_provenance.db'
orig = provenance_checker.init_db
provenance_checker.init_db = lambda db_path=None: orig(db_path=new_db)
sys.argv = ['provenance_checker.py', 'demo']
provenance_checker.main()
PY
```

**Result**
- Demo ran six example transformations, surfacing semantic bleed, attribution loss, and compound drift anomalies while logging catchable warning levels.  
- The underlying SQLite ledger was redirected to `%TEMP%` to avoid the read-only distribution folder.

**Notes**
- The module depends only on the standard library; no external packages needed for the static scenario.  
- Temporary ledger file was deleted after the run.
