# AURA MYSTERY SCHOOL - QUICK REFERENCE

## One-Page Cheat Sheet

### The 4 New Systems

```
research_pipeline.py      → Calculate Π from real studies
curriculum_builder.py     → Structure your 400+ page curriculum  
visualization_system.py   → Plot everything
integration_manager.py    → Connect all systems
```

### One Command to Rule Them All

```bash
python3 integration_manager.py
```

This runs the full pipeline:
1. Loads research evidence
2. Loads curriculum database
3. Syncs evidence → curriculum layers
4. Generates visualizations
5. Creates comprehensive report
6. Exports everything

---

## Quick Examples

### Add Research Study

```python
from research_pipeline import *

db = ResearchDatabase()
db.add_study(ResearchStudy(
    practice_name="Your Practice",
    effect_size=0.45,
    sample_size=150,
    p_value=0.02,
    study_type=StudyType.RCT,
    quality=QualityRating.MODERATE,
    year=2023,
    citation="Author et al. (2023)"
))

pi = db.get_practice("Your Practice").calculate_truth_pressure()
print(f"Π = {pi:.2f}")
```

### Add Curriculum Module

```python
from curriculum_builder import *

db = CurriculumDatabase()
db.add_module(CourseModule(
    id="my_module",
    name="My Module Name",
    domain="My Domain",
    difficulty=DifficultyLevel.BEGINNER,
    time_commitment=TimeCommitment.DAILY_30MIN,
    duration_weeks=8,
    prerequisites=[],
    research_backing=1.3,
    current_layer="MIDDLE"
))
```

### Visualize Results

```python
from visualization_system import Visualizer

viz = Visualizer()
viz.plot_pyramid_distribution(practices_by_layer, save_path="pyramid.png")
```

### Integrate Everything

```python
from integration_manager import AURAIntegration

integration = AURAIntegration()
integration.sync_research_to_curriculum()
integration.visualize_research_distribution()
integration.generate_full_report()
```

---

## File Outputs

After running, you'll have:

### Data Files
- `research_evidence.json` - All studies
- `research_evidence.csv` - Spreadsheet format
- `curriculum.json` - All courses
- `aura_integrated_*.json` - Complete system state

### Visualizations  
- `drift_over_time.png` - Agent drift plot
- `pyramid_distribution.png` - Evidence layers
- `integrated_pyramid.png` - Synced view

### Reports
- `aura_integration_report.md` - Full system report

---

## Key Metrics

### Truth Pressure (Π)
```
Π < 1.2         → EDGE (experimental)
1.2 ≤ Π < 1.5   → MIDDLE (validated)
Π ≥ 1.5         → FOUNDATION (proven)
```

### Agent Metrics (from your existing system)
```
TES (Trust/Epistemic Stability)
    > 0.70 = Healthy
    < 0.50 = Concerning

VTR (Value-to-Reality Ratio)
    > 1.0 = Creating value
    < 1.0 = Extracting value

PAI (Purpose Alignment Index)
    > 0.75 = Aligned
    < 0.75 = Misaligned
```

---

## Common Tasks

### Update Evidence for Practice
```bash
# 1. Edit research_pipeline.py, add study
# 2. Run
python3 research_pipeline.py

# 3. Sync to curriculum
python3 integration_manager.py --sync
```

### Create New Course
```bash
# 1. Edit curriculum_builder.py, add module
# 2. Validate
python3 curriculum_builder.py

# 3. Check prerequisites, detect circles
# (automatically done in step 2)
```

### Generate Dashboard
```bash
python3 integration_manager.py --visualize
```

### Full Report
```bash
python3 integration_manager.py --report
```

### Export Everything
```bash
python3 integration_manager.py --export my_backup
```

### Load Backup
```bash
python3 integration_manager.py --load my_backup
```

---

## Integration with Your Existing Code

### Connect to aura_mystery_school_v2.py

```python
# After your simulation runs
from visualization_system import Visualizer, TimeSeriesData

# Extract drift history from your agents
agent_drifts = {
    agent.name: TimeSeriesData(
        timestamps=list(range(len(agent.drift_history))),
        values=agent.drift_history,
        label=agent.name
    )
    for agent in mesh.agents
}

# Plot
viz = Visualizer()
viz.plot_drift_over_time(agent_drifts, save_path="simulation.png")
```

### Link Research to Pyramid Cascade

```python
from research_pipeline import ResearchDatabase

# Load evidence
research_db = ResearchDatabase()
research_db.import_from_json("research_evidence.json")

# Before adding to pyramid
practice_evidence = research_db.get_practice(practice_name)
if practice_evidence:
    pi = practice_evidence.calculate_truth_pressure()
    initial_layer = "EDGE" if pi < 1.2 else "MIDDLE" if pi < 1.5 else "FOUNDATION"
```

---

## Troubleshooting

### Import Errors
```bash
# Make sure files in same directory
ls *.py

# Should see all 4 new files:
# research_pipeline.py
# curriculum_builder.py
# visualization_system.py
# integration_manager.py
```

### No Matplotlib
```bash
pip install matplotlib --break-system-packages

# Or just use ASCII fallback (automatic)
```

### File Not Found
```bash
# Run from correct directory
cd /path/to/your/files
python3 integration_manager.py
```

---

## What Each File Does (One Sentence)

- `research_pipeline.py` - Turns studies into Π values
- `curriculum_builder.py` - Structures courses with prerequisites  
- `visualization_system.py` - Makes plots of everything
- `integration_manager.py` - Connects all the pieces

---

## Next Actions

1. ☐ Run `python3 integration_manager.py`
2. ☐ Look at generated PNG files
3. ☐ Read `GETTING_STARTED.md` for details
4. ☐ Add your own research data
5. ☐ Structure your own curriculum
6. ☐ Connect to your simulation
7. ☐ Share with community

---

## Remember

- **Π values** come from real research now (not hand-wavy)
- **Curriculum** is structured and validated
- **Visualizations** make it shareable
- **Integration** means it all works together

**You have the pipes. Time to pump data through them.**

---

*Quick Reference v1.0*
*Keep this handy while building*
