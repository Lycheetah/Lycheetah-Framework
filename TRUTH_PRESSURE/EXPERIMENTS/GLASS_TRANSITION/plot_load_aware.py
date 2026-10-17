"""Compare preserved fixed-budget results with measured-work snapshot results."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def grouped(rows, model, key):
    values = defaultdict(list)
    for row in rows:
        if row["model"] == model and not row["compatible"]:
            values[row["nominal_load"]].append(row[key])
    return values


def render(fixed: Path, measured: Path, output: Path) -> None:
    before = json.loads(fixed.read_text(encoding="utf-8"))["rows"]
    after = json.loads(measured.read_text(encoding="utf-8"))["rows"]
    if not before or not after:
        raise ValueError("both experiments must contain actual rows")
    figure, axes = plt.subplots(1, 3, figsize=(13.6, 4.4), layout="constrained")
    colors = {"cascade":"#1768ac", "fifo":"#c56429"}
    for model, color in colors.items():
        old = grouped(before, model, "mean_g")
        new = grouped(after, model, "mean_g")
        if set(old) != set(new):
            raise ValueError("load grids differ; no direct plot comparison")
        loads = sorted(new)
        old_means = [statistics.mean(old[value]) for value in loads]
        new_means = [statistics.mean(new[value]) for value in loads]
        axes[0].plot(loads, old_means, linestyle="--", color=color, alpha=0.6,
                     label=f"Fixed {model.upper()}")
        axes[0].plot(loads, new_means, marker="o", markersize=3, color=color,
                     label=f"Measured {model.upper()}")
        axes[1].plot(loads, [right-left for left, right in zip(old_means, new_means)],
                     marker="o", markersize=3, color=color, label=model.upper())
        usage = defaultdict(list)
        for row in after:
            if row["model"] == model and not row["compatible"]:
                usage[row["nominal_load"]].append(
                    row["work_units_in_window"]/row["available_work_in_window"]
                )
        axes[2].plot(loads, [statistics.mean(usage[v]) for v in loads],
                     marker="o", markersize=3, color=color, label=model.upper())
    axes[0].set(title="Charge work and freeze service inputs", ylabel="Time-mean conflict fraction g",
                ylim=(0,1), xlabel="Offered rate × isolated calibration time", xscale="log")
    axes[1].set(title="Change from the preserved control", ylabel="Measured minus fixed mean g",
                xlabel="Offered rate × isolated calibration time", xscale="log")
    axes[1].axhline(0, color="#777777", linewidth=0.8)
    axes[2].set(title="Measured service obeys its budget", ylabel="Fraction of available work consumed",
                ylim=(0,1.05), xlabel="Offered rate × isolated calibration time", xscale="log")
    axes[2].axhline(1, color="#777777", linestyle="--", linewidth=0.8)
    for axis in axes:
        axis.grid(alpha=0.18)
        axis.legend(fontsize=7, loc="best")
    figure.suptitle(
        f"Snapshot/commit sensitivity · {len(after)} measured-work runs vs {len(before)} fixed-budget runs\n"
        "Finite synthetic experiment; declared work units are not CPU seconds or a validated glass law",
        fontsize=12,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180)
    figure.savefig(output.with_suffix(".svg"))
    plt.close(figure)
    print(f"Rendered {len(after)} measured-work rows and {len(before)} control rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixed", type=Path, required=True)
    parser.add_argument("--measured", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render(args.fixed, args.measured, args.output)
