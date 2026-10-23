"""Command-line benchmark for the three range-sum data structures."""

import argparse
import csv
import gc
from pathlib import Path
from time import perf_counter

from .dataset import generate_dataset, load_dataset
from .factory import STRUCTURE_TYPES
from .workload import WORKLOAD_RATIOS, Operation, generate_workload


def execute_workload(structure, operations: list[Operation]) -> int:
    """Execute operations and return a checksum of all query answers.

    Input:
        structure: Initialized range-sum implementation.
        operations: Shared ordered benchmark operations.
    Output:
        Integer checksum across all range-query results.
    Purpose:
        Prevent dead-code assumptions and verify equivalent observable results.
    """
    checksum = 0
    for operation in operations:
        if operation.kind == "add":
            structure.add(operation.first, operation.second)
        else:
            checksum ^= structure.range_sum(operation.first, operation.second)
    return checksum


def benchmark_size(
    values,
    operation_count: int,
    seed: int,
    repetition: int,
    workload: str = "mixed",
) -> list[dict[str, object]]:
    """Benchmark every structure on one input size and one workload profile.

    Input:
        values: Initial integer sequence.
        operation_count: Number of operations in the workload.
        seed: Seed for the shared workload.
        repetition: Zero-based measured repetition number.
        workload: Key of ``WORKLOAD_RATIOS`` (``mixed``, ``update``, ``query``).
    Output:
        One result dictionary per data structure.
    Purpose:
        Measure build and operation time under identical conditions. Every
        structure is rebuilt from ``values``, so each workload starts from the
        same initial state.
    """
    operations = generate_workload(
        len(values), operation_count, WORKLOAD_RATIOS[workload], seed
    )
    results: list[dict[str, object]] = []
    expected_checksum: int | None = None

    for structure_type in STRUCTURE_TYPES:
        gc.collect()
        build_start = perf_counter()
        structure = structure_type(values)
        build_seconds = perf_counter() - build_start

        operation_start = perf_counter()
        checksum = execute_workload(structure, operations)
        operation_seconds = perf_counter() - operation_start

        if expected_checksum is None:
            expected_checksum = checksum
        elif checksum != expected_checksum:
            raise RuntimeError(
                f"checksum mismatch for {structure_type.name}: "
                f"{checksum} != {expected_checksum}"
            )

        results.append(
            {
                "structure": structure_type.name,
                "workload": workload,
                "n": len(values),
                "repetition": repetition,
                "operations": operation_count,
                "build_seconds": build_seconds,
                "operation_seconds": operation_seconds,
                "total_seconds": build_seconds + operation_seconds,
                "operations_per_second": (
                    operation_count / operation_seconds if operation_seconds else 0.0
                ),
                "storage_bytes": structure.storage_bytes(),
                "checksum": checksum,
            }
        )
        del structure
    return results


def write_results(path: Path, rows: list[dict[str, object]]) -> None:
    """Write benchmark rows to a CSV file with a stable schema.

    Input:
        path: Destination CSV path; missing parent folders are created.
        rows: Non-empty list of result dictionaries sharing the same keys.
    Output:
        None. The CSV file is created or overwritten.
    Purpose:
        Persist every raw measurement for later summarizing and plotting.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_sizes(raw: str) -> list[int]:
    """Parse a comma-separated list of positive input sizes.

    Input:
        raw: Text such as ``"1000,10000,100000"``.
    Output:
        List of the parsed sizes in the given order.
    Purpose:
        Validate the ``--sizes`` command-line argument.
    Raises:
        argparse.ArgumentTypeError: If the list is empty or has a size <= 0.
    """
    sizes = [int(value.strip()) for value in raw.split(",") if value.strip()]
    if not sizes or any(size <= 0 for size in sizes):
        raise argparse.ArgumentTypeError("sizes must be positive integers")
    return sizes


def parse_workloads(raw: str) -> list[str]:
    """Parse a comma-separated list of workload profile names.

    Input:
        raw: Text such as ``"mixed,update,query"``.
    Output:
        List of the validated workload names in the given order.
    Purpose:
        Validate the ``--workloads`` command-line argument.
    Raises:
        argparse.ArgumentTypeError: If the list is empty or has an unknown name.
    """
    workloads = [name.strip().lower() for name in raw.split(",") if name.strip()]
    unknown = [name for name in workloads if name not in WORKLOAD_RATIOS]
    if not workloads or unknown:
        raise argparse.ArgumentTypeError(
            f"workloads must be chosen from {', '.join(WORKLOAD_RATIOS)}"
        )
    return workloads


def main() -> None:
    """Generate/load data, run the comparison, and save a CSV result table.

    Input:
        Command-line arguments (see ``--help``).
    Output:
        None. Raw measurements are written to ``--output``.
    Purpose:
        Drive the complete experiment for every size, workload, and repetition.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("data/values.bin"))
    parser.add_argument(
        "--sizes",
        type=parse_sizes,
        default=parse_sizes("1000,10000,100000,1000000"),
        help="comma-separated input sizes",
    )
    parser.add_argument(
        "--workloads",
        type=parse_workloads,
        default=parse_workloads(",".join(WORKLOAD_RATIOS)),
        help="comma-separated workload profiles: mixed, update, query",
    )
    parser.add_argument("--operations", type=int, default=2000)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--seed", type=int, default=520)
    parser.add_argument("--output", type=Path, default=Path("results/benchmark.csv"))
    parser.add_argument(
        "--generate",
        action="store_true",
        help="generate/replace the binary dataset before benchmarking",
    )
    args = parser.parse_args()
    if args.operations < 0:
        parser.error("--operations must be non-negative")
    if args.repetitions <= 0:
        parser.error("--repetitions must be positive")

    largest_size = max(args.sizes)
    if args.generate or not args.dataset.exists():
        generate_dataset(args.dataset, largest_size, seed=args.seed)

    all_results: list[dict[str, object]] = []
    for size in args.sizes:
        values = load_dataset(args.dataset, size)
        # An unreported small workload warms imported code paths without paying
        # for a second full-size build at n = 10,000,000.
        warmup_values = values[: min(size, 10_000)]
        benchmark_size(
            warmup_values,
            min(args.operations, 200),
            args.seed + 10_000,
            repetition=-1,
        )
        del warmup_values

        for workload in args.workloads:
            for repetition in range(args.repetitions):
                all_results.extend(
                    benchmark_size(
                        values,
                        args.operations,
                        args.seed + repetition,
                        repetition,
                        workload,
                    )
                )
        del values
        gc.collect()
    write_results(args.output, all_results)
    print(f"Wrote {len(all_results)} rows to {args.output}")


if __name__ == "__main__":
    main()

