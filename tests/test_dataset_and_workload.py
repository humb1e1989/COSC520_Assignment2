"""Tests for reproducible input, workload generation, and benchmark helpers."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from advanced_structures.benchmark import (
    benchmark_size,
    execute_workload,
    parse_sizes,
    parse_workloads,
)
from advanced_structures.dataset import generate_dataset, load_dataset
from advanced_structures.fenwick_tree import FenwickTree
from advanced_structures.workload import Operation, generate_workload


class DatasetTests(unittest.TestCase):
    """Check the binary dataset generator and loader."""

    def test_dataset_round_trip_is_reproducible(self) -> None:
        """The same seed produces byte-identical files that load back intact."""
        with TemporaryDirectory() as directory:
            first = Path(directory) / "first.bin"
            second = Path(directory) / "second.bin"
            generate_dataset(first, 1000, seed=7)
            generate_dataset(second, 1000, seed=7)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(len(load_dataset(first)), 1000)
            self.assertEqual(load_dataset(first, 50), load_dataset(second, 50))

    def test_values_stay_in_range(self) -> None:
        """Generated values respect the requested minimum and maximum."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "range.bin"
            generate_dataset(path, 2000, seed=1, minimum=-5, maximum=5)
            values = load_dataset(path)
            self.assertTrue(all(-5 <= value <= 5 for value in values))

    def test_loading_too_many_values_fails(self) -> None:
        """Requesting more values than stored raises ``ValueError``."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "small.bin"
            generate_dataset(path, 10)
            with self.assertRaises(ValueError):
                load_dataset(path, 11)


class WorkloadTests(unittest.TestCase):
    """Check workload generation for each benchmark profile."""

    def test_workload_is_reproducible(self) -> None:
        """The same seed produces the same operation list."""
        first = generate_workload(100, 200, seed=17)
        second = generate_workload(100, 200, seed=17)
        self.assertEqual(first, second)

    def test_update_only_and_query_only_profiles(self) -> None:
        """Ratios 1.0 and 0.0 yield only additions and only queries."""
        updates = generate_workload(50, 300, update_ratio=1.0)
        queries = generate_workload(50, 300, update_ratio=0.0)
        self.assertTrue(all(op.kind == "add" for op in updates))
        self.assertTrue(all(op.kind == "sum" for op in queries))
        self.assertTrue(all(0 <= op.first <= op.second < 50 for op in queries))

    def test_invalid_arguments_raise(self) -> None:
        """Non-positive size and out-of-range ratio are rejected."""
        with self.assertRaises(ValueError):
            generate_workload(0, 10)
        with self.assertRaises(ValueError):
            generate_workload(10, 10, update_ratio=1.5)


class BenchmarkHelperTests(unittest.TestCase):
    """Check the benchmark helpers without running a full experiment."""

    def test_execute_workload_checksum(self) -> None:
        """The checksum is the XOR of all query answers after the updates."""
        structure = FenwickTree([1, 2, 3])
        operations = [
            Operation("sum", 0, 2),  # 6
            Operation("add", 1, 4),
            Operation("sum", 1, 1),  # 6
            Operation("sum", 0, 0),  # 1
        ]
        self.assertEqual(execute_workload(structure, operations), 6 ^ 6 ^ 1)

    def test_benchmark_size_rows_for_each_workload(self) -> None:
        """Each workload yields one row per structure with matching checksums."""
        values = list(range(200))
        for workload in ("mixed", "update", "query"):
            with self.subTest(workload=workload):
                rows = benchmark_size(values, 100, seed=3, repetition=0, workload=workload)
                self.assertEqual(len(rows), 3)
                self.assertEqual({row["workload"] for row in rows}, {workload})
                self.assertEqual(len({row["checksum"] for row in rows}), 1)

    def test_argument_parsers(self) -> None:
        """Size and workload lists are parsed and validated."""
        self.assertEqual(parse_sizes("10, 20"), [10, 20])
        self.assertEqual(parse_workloads("Query,update"), ["query", "update"])
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_sizes("10,0")
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_workloads("mixed,delete")


if __name__ == "__main__":
    unittest.main()
