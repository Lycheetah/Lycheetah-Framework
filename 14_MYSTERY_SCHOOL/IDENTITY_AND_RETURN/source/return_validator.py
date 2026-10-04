from pathlib import Path
import json, sys
BASE = Path(__file__).parent

def main():
    c = json.loads((BASE/"return_constitution.json").read_text())
    errors=[]
    if c["optimization_target"] != "meaningful_voluntary_return":
        errors.append("wrong optimization target")
    required_forbidden = {
        "punitive_streaks","daily_login_rewards","variable_ratio_loot",
        "global_xp_rank","artificial_scarcity","guilt_notifications",
        "engagement_maximizing_recommender"
    }
    missing = required_forbidden - set(c["forbidden_design"])
    if missing: errors.append("missing forbidden mechanics: "+",".join(sorted(missing)))
    if c["max_default_return_doors"] > 3:
        errors.append("too many default return doors")
    if c["skip_penalty_allowed"]:
        errors.append("skip penalty must be false")
    if c["absence_resets_progress"]:
        errors.append("absence must not reset progress")
    if not c["winter_mode"]:
        errors.append("winter mode required")
    if errors:
        print("\n".join("ERROR: "+e for e in errors))
        sys.exit(1)
    print("PASS: non-predatory return constitution v0.3")

if __name__=="__main__":
    main()
