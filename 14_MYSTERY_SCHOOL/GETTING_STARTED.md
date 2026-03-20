# AURA MYSTERY SCHOOL - GETTING STARTED GUIDE

## What You Now Have

Your mystery school system has been **massively expanded** with four new production-ready modules:

### 1. **Research Pipeline** (`research_pipeline.py`)
- **Calculate Truth Pressure (Π)** from real research studies
- Ingest study data (effect sizes, p-values, sample sizes)
- Automatically assign practices to EDGE/MIDDLE/FOUNDATION layers
- Export evidence to CSV/JSON for further analysis
- **This solves:** "Where do the Π values come from?"

### 2. **Visualization System** (`visualization_system.py`)
- Plot agent drift over time
- Show consensus evolution
- Create TES/VTR/PAI dashboards
- Display pyramid layer distribution
- Energy audit graphs
- **ASCII fallback** for systems without matplotlib
- **This solves:** "How do I see what's happening?"

### 3. **Curriculum Builder** (`curriculum_builder.py`)
- Transform massive PDF curriculum into structured modules
- Define prerequisites, learning objectives, contraindications
- Create learning paths (sequences of modules)
- Validate no circular dependencies
- Export complete catalog
- **This solves:** "How do I make 400+ pages manageable?"

### 4. **Integration Manager** (`integration_manager.py`)
- **Connect all systems** automatically
- Sync research evidence → curriculum layer assignments
- Generate comprehensive reports
- Create visualizations from live data
- Export/import entire system state
- **This solves:** "How do these pieces fit together?"

---

## Quick Start (5 Minutes)

### Step 1: Test Each System

```bash
# Test research pipeline
python3 research_pipeline.py

# Test visualization (creates PNG files)
python3 visualization_system.py

# Test curriculum builder
python3 curriculum_builder.py

# Test full integration
python3 integration_manager.py
```

### Step 2: Look at Generated Files

After running the above, you'll have:

```
research_evidence.csv          # Practice evidence spreadsheet
research_evidence.json         # Full research database
curriculum.json                # Complete course catalog
drift_over_time.png           # Agent drift visualization
pyramid_distribution.png      # Evidence layers visualization
integrated_pyramid.png        # Synced research-curriculum view
aura_integration_report.md    # Comprehensive report
```

### Step 3: Understand the Data Flow

```
Real Research Studies
        ↓
   [Research Pipeline]
        ↓
   Calculate Π (Truth Pressure)
        ↓
   Assign to EDGE/MIDDLE/FOUNDATION
        ↓
   [Integration Manager]
        ↓
   Update Curriculum Layer Assignments
        ↓
   [Visualization System]
        ↓
   Generate Plots & Reports
```

---

## Adding Your Own Data

### Adding Research Studies

```python
from research_pipeline import ResearchDatabase, ResearchStudy, StudyType, QualityRating

db = ResearchDatabase()

# Add a study you found
study = ResearchStudy(
    practice_name="Your Practice",
    effect_size=0.45,        # Cohen's d or similar
    sample_size=150,
    p_value=0.02,
    study_type=StudyType.RCT,
    quality=QualityRating.MODERATE,
    year=2023,
    citation="Author et al. (2023) Journal Name"
)

db.add_study(study)

# Calculate Π
practice = db.get_practice("Your Practice")
pi = practice.calculate_truth_pressure()
layer = practice.get_layer_recommendation()

print(f"Π = {pi:.2f} → {layer}")

# Export
db.export_to_json("my_research.json")
db.export_to_csv("my_research.csv")
```

### Adding Curriculum Modules

```python
from curriculum_builder import CurriculumDatabase, CourseModule, DifficultyLevel, TimeCommitment

db = CurriculumDatabase()

module = CourseModule(
    id="your_module_id",
    name="Your Module Name",
    description="What students will learn",
    domain="Your Domain",
    difficulty=DifficultyLevel.BEGINNER,
    time_commitment=TimeCommitment.DAILY_30MIN,
    duration_weeks=8,
    prerequisites=[],  # List of module IDs
    learning_objectives=[...],
    research_backing=1.3,  # Π value if you have it
    current_layer="MIDDLE",
    contraindications=["List any safety concerns"],
    safety_notes="Important notes"
)

db.add_module(module)
db.export_to_json("my_curriculum.json")
```

### Syncing Everything

```python
from integration_manager import AURAIntegration

integration = AURAIntegration()

# Load your data
integration.research_db.import_from_json("my_research.json")
# (curriculum loading would need implementation)

# Sync research → curriculum
changes = integration.sync_research_to_curriculum()

# Generate visualizations
integration.visualize_research_distribution("my_pyramid.png")

# Generate report
integration.generate_full_report("my_report.md")

# Export everything
integration.export_all("my_aura_system")
```

---

## Integration with Your Existing System

### Connect to `aura_mystery_school_v2.py`

Your existing `aura_mystery_school_v2.py` has agent simulation. You can now:

1. **Feed simulation results into visualization**
   ```python
   from visualization_system import Visualizer, TimeSeriesData
   
   # After running your simulation
   viz = Visualizer()
   
   agent_drifts = {
       agent.name: TimeSeriesData(
           timestamps=list(range(len(agent.drift_history))),
           values=agent.drift_history,
           label=agent.name
       )
       for agent in your_agents
   }
   
   viz.plot_drift_over_time(agent_drifts, save_path="my_simulation.png")
   ```

2. **Use research evidence to validate practices in simulation**
   ```python
   from research_pipeline import ResearchDatabase
   
   research_db = load_your_research()
   
   # Before adding practice to pyramid cascade
   practice_evidence = research_db.get_practice(practice_name)
   if practice_evidence:
       pi = practice_evidence.calculate_truth_pressure()
       # Use Π to set initial layer
   ```

3. **Link curriculum modules to agent learning**
   ```python
   from curriculum_builder import CurriculumDatabase
   
   curriculum_db = load_your_curriculum()
   
   # Agent completes a module
   module = curriculum_db.get_module(module_id)
   
   # Update agent metrics based on module objectives
   # Track prerequisite completion
   # Recommend next modules
   ```

---

## Real-World Workflows

### Workflow 1: Research → Curriculum Update

**Scenario:** New meta-analysis published on mindfulness meditation

```bash
# 1. Add study to research database
python3 -c "
from research_pipeline import *
db = ResearchDatabase()
db.import_from_json('research_evidence.json')

study = ResearchStudy(
    practice_name='Mindfulness Meditation',
    effect_size=0.58,
    sample_size=500,
    p_value=0.001,
    study_type=StudyType.META_ANALYSIS,
    quality=QualityRating.HIGH,
    year=2024,
    citation='New Study (2024)'
)
db.add_study(study)
db.export_to_json('research_evidence.json')
print('✅ Study added')
"

# 2. Recalculate Π
python3 research_pipeline.py

# 3. Sync to curriculum
python3 integration_manager.py --sync

# 4. Generate updated visualizations
python3 integration_manager.py --visualize

# 5. Check what changed
python3 integration_manager.py --report
```

### Workflow 2: Design New Course

```bash
# 1. Create module in curriculum builder
# (Edit curriculum_builder.py to add your module)

# 2. Validate prerequisites
python3 curriculum_builder.py

# 3. Check if research exists for this practice
python3 research_pipeline.py

# 4. If no research, flag it
# If yes, sync Π value
python3 integration_manager.py --sync

# 5. Export for sharing
python3 integration_manager.py --export my_new_course
```

### Workflow 3: Community Dashboard

```python
# Create real-time dashboard
from integration_manager import AURAIntegration
import time

integration = AURAIntegration()
integration.load_all("live_data")

while True:
    # Update visualizations every hour
    integration.sync_research_to_curriculum()
    integration.visualize_research_distribution("dashboard_pyramid.png")
    integration.generate_full_report("dashboard_report.md")
    
    time.sleep(3600)  # 1 hour
```

---

## Command Line Interface

The integration manager has a CLI:

```bash
# Sync research to curriculum
python3 integration_manager.py --sync

# Generate full report
python3 integration_manager.py --report

# Create visualizations
python3 integration_manager.py --visualize

# Export all data
python3 integration_manager.py --export my_data

# Load saved data
python3 integration_manager.py --load my_data
```

---

## File Formats

### Research Data (JSON)

```json
{
  "Mindfulness Meditation": {
    "summary": {
      "practice": "Mindfulness Meditation",
      "num_studies": 2,
      "truth_pressure": 1.30,
      "layer": "MIDDLE",
      "mean_effect_size": 0.455
    },
    "studies": [
      {
        "practice": "Mindfulness Meditation",
        "effect_size": 0.53,
        "sample_size": 209,
        "p_value": 0.001,
        "study_type": "meta_analysis",
        "quality": "HIGH",
        "year": 2014,
        "citation": "Khoury et al. (2015)",
        "significant": true
      }
    ]
  }
}
```

### Curriculum Data (JSON)

```json
{
  "modules": {
    "meditation_mindfulness_basic": {
      "id": "meditation_mindfulness_basic",
      "name": "Mindfulness Meditation Fundamentals",
      "domain": "Meditation",
      "difficulty": "BEGINNER",
      "duration_weeks": 8,
      "prerequisites": [],
      "research_backing": 1.30,
      "current_layer": "MIDDLE"
    }
  },
  "paths": {
    "Consciousness Foundations": {
      "module_sequence": ["foundation_body_sovereignty", "meditation_mindfulness_basic"],
      "estimated_months": 8
    }
  }
}
```

---

## Next Steps

### Immediate (This Week)

1. **Add your real research data**
   - Find studies for practices you're tracking
   - Use PubMed, Google Scholar, etc.
   - Add to research_pipeline.py

2. **Structure your curriculum**
   - Take sections from the 400+ page PDF
   - Create CourseModule objects
   - Define prerequisites

3. **Run first sync**
   - See which practices move layers
   - Generate visualizations
   - Share with community

### Short-term (This Month)

1. **Integrate with agent simulation**
   - Connect visualization to mystery_school_v2.py
   - Plot real simulation data
   - Track agent metrics over time

2. **Build web interface**
   - Flask/FastAPI backend
   - Display pyramids, courses, evidence
   - Allow community to submit research

3. **Automate research ingestion**
   - Scrape preprint servers
   - Alert when new studies published
   - Auto-calculate Π updates

### Long-term (This Year)

1. **Federated deployment**
   - Multiple communities running AURA
   - Share research databases
   - Cross-community validation

2. **Real user testing**
   - Beta cohort takes courses
   - Track completion rates
   - Measure outcomes

3. **Academic publication**
   - Write up the system
   - Publish in peer-reviewed journal
   - Open-source everything

---

## Troubleshooting

### "Import Error: No module named X"

Make sure all files are in the same directory:
```bash
ls *.py
# Should show:
# research_pipeline.py
# curriculum_builder.py
# visualization_system.py
# integration_manager.py
```

### "matplotlib not installed"

```bash
pip install matplotlib --break-system-packages
```

If that doesn't work, the system will fall back to ASCII visualizations automatically.

### "No data to visualize"

Make sure you've loaded example data:
```python
from research_pipeline import load_example_data
db = load_example_data()
```

### "Circular dependencies detected"

Check your curriculum prerequisites. A module can't depend on itself indirectly.
```python
db = CurriculumDatabase()
# ... add modules
circles = db.detect_circular_dependencies()
print(circles)  # Will show the loops
```

---

## Contributing

### Adding New Features

1. **New metric beyond TES/VTR/PAI?**
   - Add to AURAMetrics in mystery_school_v2.py
   - Update integration_manager.py to track it

2. **New visualization type?**
   - Add method to Visualizer class
   - Add ASCII fallback to ASCIIVisualizer

3. **New study quality rating?**
   - Extend QualityRating enum
   - Update Π calculation if needed

### File Structure

```
aura-mystery-school/
├── research_pipeline.py      # Evidence calculation
├── curriculum_builder.py     # Course management
├── visualization_system.py   # Plotting & dashboards
├── integration_manager.py    # System orchestration
├── aura_mystery_school_v2.py # Agent simulation (your existing file)
├── unified_field_AUS_.py     # Physics models (your existing file)
├── knowledge_genome_AUS_.py  # Knowledge evolution (your existing file)
└── data/
    ├── research_evidence.json
    ├── curriculum.json
    └── simulation_results/
```

---

## What This Enables

### Before
- Abstract ideas about "Truth Pressure"
- Massive, unstructured curriculum
- Simulation without visualization
- Disconnected systems

### After
- **Real Π calculations** from actual research
- **Structured, validated curriculum** with prerequisites
- **Visual dashboards** showing system state
- **Integrated pipeline** from research → curriculum → simulation → visualization

### The Big Win
You can now **actually measure** if your mystery school works:

1. Students complete modules
2. Track their metrics (TES/VTR/PAI)
3. Correlate with course Π values
4. See which practices actually help
5. Update curriculum based on evidence
6. Repeat

**This is the scientific method applied to spiritual education.**

---

## Questions?

Check the code comments - everything is documented.

Need help? The code is designed to be readable. Start with `integration_manager.py` and trace through.

Want to extend? Each module is independent. Fork and modify.

**The future is evidence-based mystery schools.**

**Let's build it.**

---

*Generated by Claude (Anthropic)*
*December 2024*
