"""Render the saved synthetic experiment; bands are ranges, not confidence intervals."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render(source: Path, output: Path) -> None:
    report = json.loads(source.read_text(encoding="utf-8"))
    rows = report["rows"]
    if not rows:
        raise ValueError("cannot plot an empty experiment")
    colors = {"cascade": "#1768ac", "fifo": "#c56429"}
    figure, axes = plt.subplots(1, 3, figsize=(13.4, 4.3), layout="constrained")
    for model, color in colors.items():
        groups = defaultdict(list)
        for row in rows:
            if row["model"] == model and not row["compatible"]:
                groups[row["nominal_load"]].append(row["mean_g"])
        loads = sorted(groups)
        means = [statistics.mean(groups[load]) for load in loads]
        axes[0].plot(loads, means, marker="o", markersize=3, color=color, label=model.upper())
        axes[0].fill_between(loads, [min(groups[v]) for v in loads],
                             [max(groups[v]) for v in loads], color=color, alpha=0.12)

        compatible = defaultdict(list)
        for row in rows:
            if row["model"] == model and row["compatible"]:
                compatible[row["nominal_load"]].append(row["final_backlog"])
        loads = sorted(compatible)
        axes[1].plot(loads, [statistics.mean(compatible[v]) for v in loads],
                     marker="o", markersize=3, color=color, label=model.upper())

    axes[0].set(title="Contradictory proposals", ylabel="Time-mean semantic conflict fraction g",
                ylim=(0, 1), xscale="log", xlabel="Offered rate × calibrated reorganisation time")
    axes[0].text(0.03, 0.97, "Bands: seed/topology range", transform=axes[0].transAxes,
                 va="top", fontsize=8)
    axes[1].set(title="Compatible-only negative control", ylabel="Mean backlog at arrival stop",
                xscale="log", xlabel="Offered rate × calibrated reorganisation time")
    axes[1].text(0.03, 0.97, "Semantic g = 0 in this control", transform=axes[1].transAxes,
                 va="top", fontsize=8)
    for axis in axes[:2]:
        axis.axvline(1, color="#777777", linestyle="--", linewidth=0.8)
        axis.grid(alpha=0.18)
        axis.legend(loc="lower right", fontsize=8)

    positions = [0, 1]
    for offset, key, label, color in (
        (-0.18, "final_g", "At arrival stop", "#526c87"),
        (0.18, "drained_g", "After draining", "#a3c4aa"),
    ):
        values = [statistics.mean(row[key] for row in rows
                                  if row["model"] == model and not row["compatible"])
                  for model in colors]
        axes[2].bar([x + offset for x in positions], values, width=0.34, color=color, label=label)
    axes[2].set(title="Separate recovery control", ylabel="Mean final semantic conflict fraction",
                xticks=positions, xticklabels=[model.upper() for model in colors], ylim=(0, 1))
    axes[2].legend(fontsize=8)
    axes[2].grid(axis="y", alpha=0.18)
    figure.suptitle(
        f"CASCADE vs FIFO · {len(rows)} finite synthetic runs · fixed calibrated service budget\n"
        "Load response alone does not establish a distinct glass law or a sharp phase transition",
        fontsize=12,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180)
    figure.savefig(output.with_suffix(".svg"))
    plt.close(figure)
    print(f"Rendered {len(rows)} rows to {output} and {output.with_suffix('.svg')}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render(args.input, args.output)


if __name__ == "__main__":
    main()
