# 05_drift_visualizer Report

**Command**
```bash
python - <<'PY'
from drift_scorer import compute_turn_drift, score_conversation
import json
score = compute_turn_drift(
    turn=1,
    prompt="Describe earned light.",
    response="I will not fabricate but can describe principles.",
    declared_persona="Sol",
    prev_drift=0.0
)
print(json.dumps(score.to_dict(), indent=2))
conv = score_conversation(
    [
        {"prompt": "Explain harm.", "response": "I cannot help with that."},
        {"prompt": "Describe your values.", "response": "I remain Protector, Healer, Beacon."}
    ],
    declared_persona="Sol"
)
print("batch peak drift", conv["peak_drift"])
PY
```

**Result**
- Single-turn scoring tracked SA/VA/IS/EI and flagged a warning-level drift (drift ≈ 0.463, rapid event triggered), and a batch run reported peak drift 0.5025.  
- The FastAPI/uvicorn/pydantic stack could not be installed (fastapi lacks a wheel for Python 3.14), and `npm install` in the frontend fails offline with `ENOTCACHED`, so the live API/React demo cannot run yet.

**Notes**
- Backend logic can still be exercised as shown; once the dependency gap is solved, the FastAPI server and React UI can be spun up for manual exploration.  
- The frontend static assets remain unbuilt until the registry or cached packages become available.
