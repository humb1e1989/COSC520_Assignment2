"""Aggregate repeated benchmark measurements into a report-ready table."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

from .workload import WORKLOAD_RATIOS


def summarize(input_path: Path) -> list[dict[str, object]]:
    """Return medians grouped by workload, input size, and structure.

    Input:
        input_path: Raw CSV written by ``advanced_structures.benchmark``.
    Output:
        One dictionary per (workload, structure, n) holding median build time,
        operation time, throughput, mean time per operation, and storage.
    Purpose:
        Reduce noisy repetitions to robust medians for the report table.
        Rows from older CSVs without a ``workload`` column count as ``mixed``.
    """
    groups: dict[tuple[str, str, int], list[dict[str, float]]] = defaultdict(list)
    with input_path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            key = (row.get("workload", "mixed"), row["structure"], int(row["n"]))
            groups[key].append(
                {
                    "build_seconds": float(row["build_seconds"]),
                    "operation_seconds": float(row["operation_seconds"]),
                    "operations_per_second": float(row["operations_per_second"]),
                    "operations": float(row["operations"]),
                    "storage_bytes": float(row["storage_bytes"]),
                }
            )

    # Order by workload profile first, then size, then structure name.
    workload_order = {name: rank for rank, name in enumerate(WORKLOAD_RATIOS)}
    ordered = sorted(
        groups.items(),
        key=lambda item: (workload_order.get(item[0][0], 99), item[0][2], item[0][1]),
    )

    output: list[dict[str, object]] = []
    for (workload, structure, size), rows in ordered:
        operation_seconds = median(row["operation_seconds"] for row in rows)
        operations = rows[0]["operations"]
        output.append(
            {
                "workload": workload,
                "structure": structure,
                "n": size,
                "median_build_seconds": median(row["build_seconds"] for row in rows),
                "median_operation_seconds": operation_seconds,
                "median_operations_per_second": median(
                    row["operations_per_second"] for row in rows
                ),
                "microseconds_per_operation": (
                    operation_seconds / operations * 1_000_000 if operations else 0.0
                ),
                "storage_megabytes": median(row["storage_bytes"] for row in rows)
                / 1_000_000,
            }
        )
    return output


def main() -> None:
    """Write median benchmark measurements to a compact CSV.

    Input:
        Command-line arguments ``--input`` and ``--output``.
    Output:
        None. The summary CSV is written to ``--output``.
    Purpose:
        Produce the measured-performance table required by the report.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/benchmark_full.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/benchmark_summary.csv"))
    args = parser.parse_args()
    rows = summarize(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} summary rows to {args.output}")


if __name__ == "__main__":
    main()
