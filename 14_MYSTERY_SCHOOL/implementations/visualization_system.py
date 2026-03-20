#!/usr/bin/env python3
"""
VISUALIZATION SYSTEM
====================
Generate visualizations for:
- Agent consensus networks
- Drift over time
- Pyramid cascade reorganizations
- Practice evidence distributions

Uses matplotlib for plotting (install: pip install matplotlib)
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import statistics

# Check if matplotlib available
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib not installed. Install with: pip install matplotlib")


@dataclass
class TimeSeriesData:
    """Time series data for visualization"""
    timestamps: List[int]
    values: List[float]
    label: str
    
    def to_dict(self) -> Dict:
        return {
            "timestamps": self.timestamps,
            "values": self.values,
            "label": self.label
        }


class Visualizer:
    """Generate visualizations for AURA system"""
    
    def __init__(self):
        self.figures = []
    
    def plot_drift_over_time(
        self, 
        agent_drifts: Dict[str, TimeSeriesData],
        title: str = "Agent Drift Over Time",
        threshold: float = 0.25,
        save_path: Optional[str] = None
    ):
        """
        Plot drift for multiple agents over time
        
        Args:
            agent_drifts: Dict of agent_name -> TimeSeriesData
            title: Plot title
            threshold: Critical drift threshold line
            save_path: If provided, save figure to this path
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Cannot plot: matplotlib not installed")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot each agent
        for agent_name, data in agent_drifts.items():
            ax.plot(
                data.timestamps, 
                data.values, 
                label=agent_name,
                linewidth=2
            )
        
        # Add threshold line
        if threshold:
            ax.axhline(
                y=threshold, 
                color='r', 
                linestyle='--', 
                label=f'Critical Threshold ({threshold})',
                linewidth=2
            )
        
        ax.set_xlabel('Time Step', fontsize=12)
        ax.set_ylabel('Drift from Anchor', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Saved: {save_path}")
        else:
            plt.show()
        
        self.figures.append(fig)
    
    def plot_consensus_evolution(
        self,
        consensus_history: List[List[float]],
        title: str = "Consensus Vector Evolution",
        save_path: Optional[str] = None
    ):
        """
        Plot how consensus vector changes over time
        
        Args:
            consensus_history: List of consensus vectors at each timestep
            title: Plot title
            save_path: If provided, save figure to this path
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Cannot plot: matplotlib not installed")
            return
        
        if not consensus_history:
            print("No consensus history to plot")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot each dimension of consensus vector
        num_dims = len(consensus_history[0])
        timestamps = list(range(len(consensus_history)))
        
        for dim in range(num_dims):
            values = [vec[dim] for vec in consensus_history]
            ax.plot(timestamps, values, label=f'Dimension {dim+1}', linewidth=2)
        
        ax.set_xlabel('Time Step', fontsize=12)
        ax.set_ylabel('Consensus Value', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Saved: {save_path}")
        else:
            plt.show()
        
        self.figures.append(fig)
    
    def plot_metrics_dashboard(
        self,
        agents_metrics: Dict[str, Dict[str, List[float]]],
        title: str = "AURA Metrics Dashboard",
        save_path: Optional[str] = None
    ):
        """
        Plot TES/VTR/PAI for all agents over time
        
        Args:
            agents_metrics: Dict[agent_name -> Dict[metric_name -> values]]
            title: Dashboard title
            save_path: If provided, save figure to this path
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Cannot plot: matplotlib not installed")
            return
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        metrics = ['TES', 'VTR', 'PAI']
        thresholds = [0.70, 1.0, 0.75]
        
        for idx, (metric, threshold) in enumerate(zip(metrics, thresholds)):
            ax = axes[idx]
            
            # Plot each agent's metric
            for agent_name, agent_data in agents_metrics.items():
                if metric in agent_data:
                    timestamps = list(range(len(agent_data[metric])))
                    ax.plot(
                        timestamps, 
                        agent_data[metric], 
                        label=agent_name,
                        linewidth=2
                    )
            
            # Add threshold line
            ax.axhline(
                y=threshold,
                color='r',
                linestyle='--',
                label=f'Threshold ({threshold})',
                linewidth=2
            )
            
            ax.set_ylabel(metric, fontsize=12, fontweight='bold')
            ax.set_xlabel('Time Step', fontsize=10)
            ax.legend(loc='upper right', fontsize=8)
            ax.grid(True, alpha=0.3)
        
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Saved: {save_path}")
        else:
            plt.show()
        
        self.figures.append(fig)
    
    def plot_pyramid_distribution(
        self,
        practices_by_layer: Dict[str, List[Tuple[str, float]]],
        title: str = "Knowledge Pyramid Distribution",
        save_path: Optional[str] = None
    ):
        """
        Plot practices distributed across pyramid layers
        
        Args:
            practices_by_layer: Dict[layer_name -> List[(practice_name, pi_value)]]
            title: Plot title
            save_path: If provided, save figure to this path
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Cannot plot: matplotlib not installed")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        layers = ['FOUNDATION', 'MIDDLE', 'EDGE']
        colors = {'FOUNDATION': '#2ecc71', 'MIDDLE': '#f39c12', 'EDGE': '#e74c3c'}
        y_positions = {'FOUNDATION': 0, 'MIDDLE': 1, 'EDGE': 2}
        
        # Plot practices
        for layer in layers:
            if layer in practices_by_layer:
                practices = practices_by_layer[layer]
                for i, (practice, pi) in enumerate(practices):
                    x = pi
                    y = y_positions[layer] + (i * 0.05 - 0.1)  # Spread vertically
                    
                    ax.scatter(
                        x, y, 
                        s=200, 
                        c=colors[layer], 
                        alpha=0.7,
                        edgecolors='black',
                        linewidth=1
                    )
                    
                    # Add label
                    ax.text(
                        x, y, 
                        practice[:15] + '...' if len(practice) > 15 else practice,
                        fontsize=8,
                        ha='left',
                        va='center'
                    )
        
        # Add threshold lines
        ax.axvline(x=1.2, color='orange', linestyle='--', label='EDGE→MIDDLE (Π=1.2)', linewidth=2)
        ax.axvline(x=1.5, color='green', linestyle='--', label='MIDDLE→FOUNDATION (Π=1.5)', linewidth=2)
        
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(layers, fontsize=12, fontweight='bold')
        ax.set_xlabel('Truth Pressure (Π)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Saved: {save_path}")
        else:
            plt.show()
        
        self.figures.append(fig)
    
    def plot_energy_audit(
        self,
        energy_logs: Dict[str, List[Tuple[str, float]]],
        title: str = "Energy Audit by Agent",
        save_path: Optional[str] = None
    ):
        """
        Plot cumulative energy costs for each agent
        
        Args:
            energy_logs: Dict[agent_name -> List[(operation, cost)]]
            title: Plot title
            save_path: If provided, save figure to this path
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Cannot plot: matplotlib not installed")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Calculate cumulative energy
        for agent_name, operations in energy_logs.items():
            timestamps = list(range(len(operations)))
            cumulative = []
            total = 0
            for _, cost in operations:
                total += cost
                cumulative.append(total)
            
            ax.plot(timestamps, cumulative, label=agent_name, linewidth=2)
        
        ax.set_xlabel('Operation Number', fontsize=12)
        ax.set_ylabel('Cumulative Energy Cost', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 Saved: {save_path}")
        else:
            plt.show()
        
        self.figures.append(fig)
    
    def close_all(self):
        """Close all figures"""
        plt.close('all')
        self.figures = []
    
    def export_all_data(self, filename: str):
        """Export all plot data to JSON"""
        # This would store plot data for later regeneration
        # Implementation depends on what data you want to preserve
        pass


# =========================
# ASCII FALLBACK VISUALIZATIONS
# =========================

class ASCIIVisualizer:
    """Fallback visualizations using ASCII art (no matplotlib needed)"""
    
    @staticmethod
    def plot_drift_ascii(agent_drifts: Dict[str, List[float]], width: int = 60):
        """ASCII plot of drift over time"""
        print("\n" + "=" * width)
        print("AGENT DRIFT OVER TIME (ASCII)")
        print("=" * width)
        
        if not agent_drifts:
            print("No data to plot")
            return
        
        # Find max timesteps
        max_steps = max(len(values) for values in agent_drifts.values())
        
        # Plot each agent
        for agent_name, drifts in agent_drifts.items():
            print(f"\n{agent_name}:")
            
            # Create bar chart
            for i, drift in enumerate(drifts):
                bar_len = int(drift * width)
                bar = '█' * min(bar_len, width)
                print(f"  {i:3d} | {bar} {drift:.3f}")
        
        print("=" * width)
    
    @staticmethod
    def plot_pyramid_ascii(practices_by_layer: Dict[str, List[Tuple[str, float]]]):
        """ASCII pyramid visualization"""
        print("\n" + "=" * 70)
        print("KNOWLEDGE PYRAMID")
        print("=" * 70)
        
        layers = ['FOUNDATION', 'MIDDLE', 'EDGE']
        
        for layer in layers:
            print(f"\n{layer}:")
            print("-" * 70)
            
            if layer in practices_by_layer:
                for practice, pi in practices_by_layer[layer]:
                    bar_len = int(pi * 30)
                    bar = '█' * bar_len
                    print(f"  {practice[:40]:40s} Π={pi:.2f} {bar}")
            else:
                print("  (no practices)")
        
        print("=" * 70)


# =========================
# DEMONSTRATION
# =========================

def demo():
    """Demonstrate visualization capabilities"""
    
    # Generate sample data
    timesteps = list(range(50))
    
    agent_drifts = {
        'A1': TimeSeriesData(
            timesteps,
            [0.05 + 0.01 * i + 0.02 * (i % 10) for i in timesteps],
            'A1'
        ),
        'A2': TimeSeriesData(
            timesteps,
            [0.03 + 0.005 * i + 0.015 * (i % 8) for i in timesteps],
            'A2'
        ),
        'ADVERSARY': TimeSeriesData(
            timesteps,
            [0.1 + 0.02 * i + 0.05 * (i % 5) for i in timesteps],
            'ADVERSARY'
        ),
    }
    
    # Try matplotlib version
    if MATPLOTLIB_AVAILABLE:
        print("📊 Generating matplotlib visualizations...")
        viz = Visualizer()
        
        # Drift over time
        drift_dict = {name: data for name, data in agent_drifts.items()}
        viz.plot_drift_over_time(
            drift_dict,
            title="Agent Drift Simulation",
            save_path="/home/claude/drift_over_time.png"
        )
        
        # Pyramid distribution
        practices = {
            'FOUNDATION': [
                ('Cognitive Behavioral Therapy', 6.54),
                ('Exercise', 2.1)
            ],
            'MIDDLE': [
                ('Mindfulness Meditation', 1.30),
                ('Yoga', 1.25)
            ],
            'EDGE': [
                ('Breathwork', 0.33),
                ('Reiki', 0.01),
                ('Crystal Healing', 0.00)
            ]
        }
        
        viz.plot_pyramid_distribution(
            practices,
            title="Practice Evidence Distribution",
            save_path="/home/claude/pyramid_distribution.png"
        )
        
        print("✅ Visualizations generated!")
    
    # Always show ASCII fallback
    print("\n📊 ASCII Fallback Visualizations:")
    ascii_viz = ASCIIVisualizer()
    
    # Convert to simple dict for ASCII
    simple_drifts = {name: data.values for name, data in agent_drifts.items()}
    ascii_viz.plot_drift_ascii(simple_drifts)
    
    practices_ascii = {
        'FOUNDATION': [('CBT', 6.54), ('Exercise', 2.1)],
        'MIDDLE': [('Mindfulness', 1.30), ('Yoga', 1.25)],
        'EDGE': [('Breathwork', 0.33), ('Reiki', 0.01), ('Crystals', 0.00)]
    }
    ascii_viz.plot_pyramid_ascii(practices_ascii)


if __name__ == "__main__":
    demo()
