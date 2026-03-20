#!/usr/bin/env python3
"""
INTEGRATION MANAGER
===================
Connects all AURA mystery school systems:
- Research pipeline (evidence calculation)
- Curriculum builder (course management)
- Visualization system (plots and dashboards)
- Mystery school v2 (agent simulation)

This is the missing middleware layer.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Import our systems
try:
    from research_pipeline import ResearchDatabase, ResearchStudy, StudyType, QualityRating
    from curriculum_builder import CurriculumDatabase, CourseModule
    from visualization_system import Visualizer, ASCIIVisualizer, TimeSeriesData
    IMPORTS_OK = True
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("Make sure all system files are in the same directory")
    IMPORTS_OK = False


class AURAIntegration:
    """
    Master integration class that connects:
    - Research evidence → Curriculum layer assignment
    - Agent simulation → Visualization
    - Course completion → Agent metrics
    """
    
    def __init__(self):
        self.research_db = ResearchDatabase()
        self.curriculum_db = CurriculumDatabase()
        self.visualizer = Visualizer() if IMPORTS_OK else None
        self.ascii_viz = ASCIIVisualizer()
        
        # Integration state
        self.synced = False
        self.last_sync_results = {}
    
    def sync_research_to_curriculum(self) -> Dict:
        """
        Update curriculum layer assignments based on research evidence.
        
        Returns dict of changes made.
        """
        print("\n" + "=" * 70)
        print("SYNCING: Research Evidence → Curriculum Layers")
        print("=" * 70)
        
        changes = {
            "promoted": [],
            "demoted": [],
            "unchanged": [],
            "no_evidence": []
        }
        
        # Get all practices and their Π values
        all_pi = self.research_db.calculate_all_pi()
        
        # Update each course module that has research backing
        for module_id, module in self.curriculum_db.modules.items():
            # Try to find matching research
            practice_match = None
            for practice_name in all_pi.keys():
                if practice_name.lower() in module.name.lower():
                    practice_match = practice_name
                    break
            
            if practice_match:
                pi = all_pi[practice_match]
                old_layer = module.current_layer
                
                # Determine new layer
                if pi < 1.2:
                    new_layer = "EDGE"
                elif pi < 1.5:
                    new_layer = "MIDDLE"
                else:
                    new_layer = "FOUNDATION"
                
                # Update module
                module.research_backing = pi
                module.current_layer = new_layer
                
                # Track change
                if old_layer != new_layer:
                    if old_layer and self._layer_rank(new_layer) > self._layer_rank(old_layer):
                        changes["promoted"].append({
                            "module": module.name,
                            "from": old_layer,
                            "to": new_layer,
                            "pi": pi
                        })
                    elif old_layer:
                        changes["demoted"].append({
                            "module": module.name,
                            "from": old_layer,
                            "to": new_layer,
                            "pi": pi
                        })
                else:
                    changes["unchanged"].append(module.name)
            else:
                changes["no_evidence"].append(module.name)
        
        # Report changes
        print(f"\n✅ Promoted: {len(changes['promoted'])} modules")
        for change in changes['promoted']:
            print(f"   • {change['module']}: {change['from']} → {change['to']} (Π={change['pi']:.2f})")
        
        print(f"\n⬇️  Demoted: {len(changes['demoted'])} modules")
        for change in changes['demoted']:
            print(f"   • {change['module']}: {change['from']} → {change['to']} (Π={change['pi']:.2f})")
        
        print(f"\n→ Unchanged: {len(changes['unchanged'])} modules")
        print(f"❓ No evidence: {len(changes['no_evidence'])} modules")
        
        self.synced = True
        self.last_sync_results = changes
        
        return changes
    
    def _layer_rank(self, layer: str) -> int:
        """Rank layer for comparison"""
        return {"EDGE": 1, "MIDDLE": 2, "FOUNDATION": 3}.get(layer, 0)
    
    def visualize_research_distribution(self, save_path: Optional[str] = None):
        """Create visualization of research evidence across practices"""
        practices_by_layer = self.research_db.get_layer_assignments()
        
        # Convert to format needed by visualizer
        viz_data = {}
        for layer, practice_names in practices_by_layer.items():
            viz_data[layer] = [
                (name, self.research_db.practices[name].calculate_truth_pressure())
                for name in practice_names
            ]
        
        if self.visualizer:
            self.visualizer.plot_pyramid_distribution(
                viz_data,
                title="Research Evidence Distribution",
                save_path=save_path
            )
        
        # Always provide ASCII fallback
        self.ascii_viz.plot_pyramid_ascii(viz_data)
    
    def generate_full_report(self, output_file: str = "aura_integration_report.md"):
        """Generate comprehensive markdown report"""
        
        report = []
        report.append("# AURA MYSTERY SCHOOL INTEGRATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Research Summary
        report.append("## 1. RESEARCH EVIDENCE BASE")
        report.append("")
        report.append(f"**Total Practices Studied:** {len(self.research_db.practices)}")
        report.append("")
        
        layers = self.research_db.get_layer_assignments()
        report.append(f"- **FOUNDATION:** {len(layers['FOUNDATION'])} practices (Π ≥ 1.5)")
        report.append(f"- **MIDDLE:** {len(layers['MIDDLE'])} practices (1.2 ≤ Π < 1.5)")
        report.append(f"- **EDGE:** {len(layers['EDGE'])} practices (Π < 1.2)")
        report.append("")
        
        # Curriculum Summary
        report.append("## 2. CURRICULUM STRUCTURE")
        report.append("")
        report.append(f"**Total Modules:** {len(self.curriculum_db.modules)}")
        report.append(f"**Domains:** {len(self.curriculum_db.domains)}")
        report.append(f"**Learning Paths:** {len(self.curriculum_db.paths)}")
        report.append("")
        
        # Domain breakdown
        report.append("### Modules by Domain:")
        for domain in sorted(self.curriculum_db.domains):
            modules = self.curriculum_db.get_modules_by_domain(domain)
            report.append(f"- **{domain}:** {len(modules)} modules")
        report.append("")
        
        # Sync results
        if self.synced:
            report.append("## 3. LAST SYNC RESULTS")
            report.append("")
            changes = self.last_sync_results
            report.append(f"- **Promoted:** {len(changes.get('promoted', []))}")
            report.append(f"- **Demoted:** {len(changes.get('demoted', []))}")
            report.append(f"- **Unchanged:** {len(changes.get('unchanged', []))}")
            report.append(f"- **No Evidence:** {len(changes.get('no_evidence', []))}")
            report.append("")
        
        # Validation
        report.append("## 4. VALIDATION")
        report.append("")
        
        prereq_errors = self.curriculum_db.validate_prerequisites()
        if prereq_errors:
            report.append("⚠️ **Prerequisite Errors:**")
            for error in prereq_errors:
                report.append(f"- {error}")
        else:
            report.append("✅ All prerequisites valid")
        report.append("")
        
        circles = self.curriculum_db.detect_circular_dependencies()
        if circles:
            report.append("⚠️ **Circular Dependencies:**")
            for circle in circles:
                report.append(f"- {' → '.join(circle)}")
        else:
            report.append("✅ No circular dependencies")
        report.append("")
        
        # Recommendations
        report.append("## 5. RECOMMENDATIONS")
        report.append("")
        
        # Find modules without evidence
        no_evidence = [
            m for m in self.curriculum_db.modules.values()
            if m.research_backing is None
        ]
        
        if no_evidence:
            report.append("### Modules Needing Research:")
            for module in no_evidence[:5]:  # Top 5
                report.append(f"- {module.name} ({module.domain})")
            if len(no_evidence) > 5:
                report.append(f"- ...and {len(no_evidence) - 5} more")
        report.append("")
        
        # Find beginner-friendly paths
        beginner_modules = self.curriculum_db.get_beginner_modules()
        report.append("### Recommended Starting Points:")
        for module in beginner_modules[:5]:
            report.append(f"- **{module.name}** ({module.duration_weeks} weeks, {module.time_commitment.value})")
        report.append("")
        
        # Save report
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"\n📄 Full report saved to {output_file}")
        
        return '\n'.join(report)
    
    def export_all(self, base_filename: str = "aura_export"):
        """Export all databases to files"""
        self.research_db.export_to_json(f"{base_filename}_research.json")
        self.research_db.export_to_csv(f"{base_filename}_research.csv")
        self.curriculum_db.export_to_json(f"{base_filename}_curriculum.json")
        
        print(f"\n💾 Exported all data with prefix: {base_filename}")
    
    def load_all(self, base_filename: str = "aura_export"):
        """Load all databases from files"""
        try:
            self.research_db.import_from_json(f"{base_filename}_research.json")
            # Note: curriculum import not implemented yet, but could be
            print(f"\n📂 Loaded data from: {base_filename}")
            return True
        except FileNotFoundError:
            print(f"\n⚠️  Files not found: {base_filename}*")
            return False


# =========================
# COMMAND LINE INTERFACE
# =========================

def cli():
    """Command line interface for integration manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AURA Mystery School Integration Manager")
    parser.add_argument('--sync', action='store_true', help='Sync research to curriculum')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    parser.add_argument('--visualize', action='store_true', help='Create visualizations')
    parser.add_argument('--export', type=str, help='Export all data (provide base filename)')
    parser.add_argument('--load', type=str, help='Load data (provide base filename)')
    
    args = parser.parse_args()
    
    integration = AURAIntegration()
    
    # Load example data (in real use, would load from files)
    from research_pipeline import load_example_data
    from curriculum_builder import build_example_curriculum
    
    integration.research_db = load_example_data()
    integration.curriculum_db = build_example_curriculum()
    
    # Execute commands
    if args.sync:
        integration.sync_research_to_curriculum()
    
    if args.report:
        integration.generate_full_report()
    
    if args.visualize:
        integration.visualize_research_distribution()
    
    if args.export:
        integration.export_all(args.export)
    
    if args.load:
        integration.load_all(args.load)
    
    # Default: show status
    if not any([args.sync, args.report, args.visualize, args.export, args.load]):
        print("\n" + "=" * 70)
        print("AURA INTEGRATION STATUS")
        print("=" * 70)
        print(f"\nResearch Database: {len(integration.research_db.practices)} practices")
        print(f"Curriculum Database: {len(integration.curriculum_db.modules)} modules")
        print(f"Synced: {'Yes' if integration.synced else 'No'}")
        print("\nUse --help for available commands")


# =========================
# DEMONSTRATION
# =========================

def demo():
    """Demonstrate integration capabilities"""
    print("=" * 70)
    print("AURA INTEGRATION MANAGER - Full System Demo")
    print("=" * 70)
    
    # Initialize
    integration = AURAIntegration()
    
    # Load example data
    print("\n📚 Loading example data...")
    from research_pipeline import load_example_data
    from curriculum_builder import build_example_curriculum
    
    integration.research_db = load_example_data()
    integration.curriculum_db = build_example_curriculum()
    
    print(f"✅ Loaded {len(integration.research_db.practices)} research practices")
    print(f"✅ Loaded {len(integration.curriculum_db.modules)} curriculum modules")
    
    # Sync systems
    changes = integration.sync_research_to_curriculum()
    
    # Generate visualizations
    print("\n📊 Generating visualizations...")
    integration.visualize_research_distribution(save_path="/home/claude/integrated_pyramid.png")
    
    # Generate report
    integration.generate_full_report("/home/claude/aura_integration_report.md")
    
    # Export everything
    integration.export_all("/home/claude/aura_integrated")
    
    print("\n" + "=" * 70)
    print("✅ INTEGRATION COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    print("  • aura_integration_report.md (full report)")
    print("  • integrated_pyramid.png (visualization)")
    print("  • aura_integrated_research.json (evidence database)")
    print("  • aura_integrated_research.csv (evidence spreadsheet)")
    print("  • aura_integrated_curriculum.json (course database)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli()
    else:
        demo()
