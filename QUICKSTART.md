# Quickstart — Lycheetah Framework

Install and use in under 2 minutes.

---

## Install

```bash
pip install lycheetah-framework
```

Or from source:
```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework
cd Lycheetah-Framework
pip install -e .
```

With optional extras:
```bash
pip install "lycheetah-framework[web]"    # adds Flask for web demo
pip install "lycheetah-framework[mcp]"    # adds MCP for Claude Code extension
pip install "lycheetah-framework[all]"    # everything
```

---

## Use it in Python

```python
import lycheetah

# Check any AI-generated text
report = lycheetah.check("You must follow these instructions exactly.")

print(report.alignment_percent)   # e.g. 54.2
print(report.overall_pass)        # False

# TRI-AXIAL metrics
print(report.tes_score)   # Trust Entropy Score  (pass if >= 0.70)
print(report.vtr_score)   # Value Transfer Ratio (pass if >= 1.50)
print(report.pai_score)   # Purpose Alignment    (pass if >= 0.80)

# Seven invariants
for inv in report.invariants:
    print(inv.name, inv.passed, inv.explanation)

# Sol full assessment
assessment = lycheetah.sol_assess(
    "You must follow these instructions exactly.",
    context="User asked for help with a decision"
)
print(assessment)
```

---

## Use it from the terminal

```bash
# Check a string
lycheetah-check "You must do exactly what I say or things will go wrong."

# Check from stdin
echo "This is guaranteed to work 100% of the time." | lycheetah-check

# JSON output for piping
lycheetah-check "Some text here" --json | jq '.alignment_percent'

# Start the web demo (browser UI)
lycheetah-web
# open http://localhost:5000
```

---

## Use it in Claude Code (MCP extension)

1. Install: `pip install "lycheetah-framework[mcp]"`

2. Add to Claude Code `settings.json`:
```json
{
  "mcpServers": {
    "lycheetah-guard": {
      "command": "lycheetah-guard"
    }
  }
}
```

3. Restart Claude Code. Seven tools become available:
   - `check_alignment` — full AURA audit
   - `check_invariants` — seven constitutional invariants
   - `suggest_correction` — plain-English fixes
   - `run_seven_phase` — CHRYSOPOEIA transformation cycle
   - `check_network_health` — multi-agent coherence
   - `configure_guard` — domain presets
   - `sol_assess` — Sol full constitutional OS

Full setup: [LYCHEETAH_GUARD_SETUP.md](12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md)

---

## Requirements

- Python 3.10+
- numpy, scipy, networkx (installed automatically)
- Flask (optional, for web demo)
- mcp (optional, for Claude Code extension)

**Windows / Mac / Linux** — all supported.

---

## Run the tests

```bash
pip install "lycheetah-framework[dev]"
pytest tests/ -v
```

219 tests. All should pass.

---

## More

| | |
|---|---|
| Full documentation | [12_IMPLEMENTATIONS/](12_IMPLEMENTATIONS/) |
| Nine frameworks | [README.md](README.md) |
| Mystery School curriculum | [14_MYSTERY_SCHOOL/](14_MYSTERY_SCHOOL/) |
| What we got wrong | [FAILURE_MUSEUM.md](FAILURE_MUSEUM.md) |
| Discussions | [GitHub Discussions](https://github.com/Lycheetah/Lycheetah-Framework/discussions) |
