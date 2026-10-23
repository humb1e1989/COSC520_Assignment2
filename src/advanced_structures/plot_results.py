"""Create report-ready benchmark plots from the CSV output."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt

from .workload import WORKLOAD_RATIOS

# Human-readable panel titles for each workload profile.
WORKLOAD_TITLES = {
    "mixed": "Mixed (50% add / 50% sum)",
    "update": "Update-only (100% add)",
    "query": "Query-only (100% sum)",
}


def read_results(path: Path) -> dict[str, dict[str, list[dict[str, float]]]]:
    """Read CSV rows and aggregate repeated measurements by median.

    Input:
        path: Raw CSV written by ``advanced_structures.benchmark``.
    Output:
        Nested mapping ``workload -> structure -> rows`` where each row holds
        the median ``n``, build time, operation time, microseconds per
        operation, and storage bytes; rows are sorted by ``n``.
    Purpose:
        Convert raw repetitions into one point per plotted input size.
        Rows from older CSVs without a ``workload`` column count as ``mixed``.
    """
    raw: dict[tuple[str, str, int], list[dict[str, float]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            key = (row.get("workload", "mixed"), row["structure"], int(row["n"]))
            raw[key].append(
                {
                    "build_seconds": float(row["build_seconds"]),
                    "operation_seconds": float(row["operation_seconds"]),
                    "operations": float(row["operations"]),
                    "storage_bytes": float(row["storage_bytes"]),
                }
            )

    grouped: dict[str, dict[str, list[dict[str, float]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for (workload, structure, size), measurements in raw.items():
        operation_seconds = median(row["operation_seconds"] for row in measurements)
        operations = measurements[0]["operations"]
        grouped[workload][structure].append(
            {
                "n": float(size),
                "build_seconds": median(row["build_seconds"] for row in measurements),
                "operation_seconds": operation_seconds,
                "microseconds_per_operation": (
                    operation_seconds / operations * 1_000_000 if operations else 0.0
                ),
                "storage_bytes": median(row["storage_bytes"] for row in measurements),
            }
        )
    for structures in grouped.values():
        for rows in structures.values():
            rows.sort(key=lambda item: item["n"])
    return grouped


def merge_workloads(grouped) -> dict[str, list[dict[str, float]]]:
    """Pool build time and storage across workloads for each structure.

    Input:
        grouped: Output of ``read_results``.
    Output:
        Mapping ``structure -> rows`` with the median build time and storage
        over every workload at each ``n``.
    Purpose:
        Build time and storage do not depend on the workload, so pooling the
        separate builds gives more samples per plotted point.
    """
    pooled: dict[tuple[str, float], list[dict[str, float]]] = defaultdict(list)
    for structures in grouped.values():
        for structure, rows in structures.items():
            for row in rows:
                pooled[(structure, row["n"])].append(row)

    merged: dict[str, list[dict[str, float]]] = defaultdict(list)
    for (structure, size), rows in pooled.items():
        merged[structure].append(
            {
                "n": size,
                "build_seconds": median(row["build_seconds"] for row in rows),
                "storage_bytes": median(row["storage_bytes"] for row in rows),
            }
        )
    for rows in merged.values():
        rows.sort(key=lambda item: item["n"])
    return merged


def draw_series(ax, series, metric: str, scale: float = 1.0) -> None:
    """Draw one line per structure on an existing matplotlib axis.

    Input:
        ax: Target matplotlib ``Axes``.
        series: Mapping ``structure -> rows`` sorted by ``n``.
        metric: Row key plotted on the y-axis.
        scale: Divisor applied to every y value (e.g. bytes to MB).
    Output:
        None. Lines are added to ``ax``.
    Purpose:
        Keep marker and line styling identical across every figure.
    """
    for structure, rows in sorted(series.items()):
        ax.plot(
            [row["n"] for row in rows],
            [row[metric] / scale for row in rows],
            marker="o",
            linewidth=1.8,
            label=structure,
        )


def plot_metric(
    series,
    metric: str,
    ylabel: str,
    output: Path,
    scale: float = 1.0,
    logarithmic_y: bool = False,
) -> None:
    """Plot one measurement against input size using logarithmic x scaling.

    Input:
        series: Mapping ``structure -> rows`` sorted by ``n``.
        metric: Row key plotted on the y-axis.
        ylabel: Y-axis label.
        output: Destination PNG path.
        scale: Divisor applied to every y value.
        logarithmic_y: Use a log y-axis too, giving a log-log plot in which
            a power law ``n^k`` appears as a straight line of slope ``k``.
    Output:
        None. The figure is saved to ``output``.
    Purpose:
        Produce one report figure for a single metric.
    """
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    draw_series(ax, series, metric, scale)
    ax.set_xscale("log")
    if logarithmic_y:
        ax.set_yscale("log")
    ax.set_xlabel("Number of data points n")
    ax.set_ylabel(ylabel)
    ax.margins(y=0.08)
    ax.grid(True, which="both", linestyle="--", alpha=0.35)
    ax.legend(frameon=False)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def plot_operation_comparison(grouped, output: Path) -> None:
    """Plot time per operation for every workload side by side (log-log).

    Input:
        grouped: Output of ``read_results``.
        output: Destination PNG path.
    Output:
        None. A one-row, multi-panel figure is saved to ``output``.
    Purpose:
        Show in one figure that Square Root Decomposition wins on updates
        but loses on queries, while both trees stay logarithmic.
    """
    workloads = [name for name in WORKLOAD_RATIOS if name in grouped]
    fig, axes = plt.subplots(
        1, len(workloads), figsize=(4.2 * len(workloads), 3.8), squeeze=False
    )
    for ax, workload in zip(axes[0], workloads):
        draw_series(ax, grouped[workload], "microseconds_per_operation")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(WORKLOAD_TITLES.get(workload, workload), fontsize=10)
        ax.set_xlabel("Number of data points n")
        ax.grid(True, which="both", linestyle="--", alpha=0.35)
    axes[0][0].set_ylabel("Time per operation (µs, log scale)")
    axes[0][0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def main() -> None:
    """Generate build-time, per-workload time, and storage plots.

    Input:
        Command-line arguments ``--input`` and ``--output-dir``.
    Output:
        None. PNG files are written to ``--output-dir``.
    Purpose:
        Create every figure used in the report from one raw CSV.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/benchmark.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/plots"))
    args = parser.parse_args()
    grouped = read_results(args.input)
    merged = merge_workloads(grouped)
    out = args.output_dir

    plot_metric(merged, "build_seconds", "Build time (seconds)", out / "build_time.png")
    plot_metric(
        merged,
        "build_seconds",
        "Build time (seconds, log scale)",
        out / "build_time_log.png",
        logarithmic_y=True,
    )
    plot_metric(
        merged,
        "storage_bytes",
        "Principal numeric storage (MB)",
        out / "storage.png",
        scale=1_000_000.0,
    )
    for workload, series in grouped.items():
        title = WORKLOAD_TITLES.get(workload, workload)
        plot_metric(
            series,
            "operation_seconds",
            f"{title} time (seconds)",
            out / f"{workload}_time.png",
        )
        plot_metric(
            series,
            "operation_seconds",
            f"{title} time (s, log scale)",
            out / f"{workload}_time_log.png",
            logarithmic_y=True,
        )
    plot_operation_comparison(grouped, out / "operation_comparison.png")
    print(f"Plots written to {out}")


if __name__ == "__main__":
    main()
