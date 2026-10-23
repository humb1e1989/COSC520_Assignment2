"""Correctness and interface tests for all compared data structures."""

import random
import unittest

from advanced_structures.factory import STRUCTURE_TYPES, create_structure


class SharedStructureTests(unittest.TestCase):
    """Apply the same required behavior to every implementation."""

    def test_known_range_sums_and_updates(self) -> None:
        """Hand-computed sums match before and after one point update."""
        values = [4, -2, 7, 3, 1, 8]
        for structure_type in STRUCTURE_TYPES:
            with self.subTest(structure=structure_type.name):
                structure = structure_type(values)
                self.assertEqual(structure.range_sum(0, 5), 21)
                self.assertEqual(structure.range_sum(1, 4), 9)
                self.assertEqual(structure.range_sum(2, 2), 7)
                structure.add(2, 5)
                self.assertEqual(structure.range_sum(1, 4), 14)

    def test_randomized_equivalence_to_plain_list(self) -> None:
        """Random adds and queries agree with a plain Python list.

        Sizes include 1, powers of two, their neighbours, and perfect squares
        so that tree shapes and square-root block boundaries are all covered.
        """
        rng = random.Random(520)
        for size in (1, 2, 3, 15, 16, 17, 99, 100, 101, 257):
            baseline = [rng.randint(-100, 100) for _ in range(size)]
            structures = [structure_type(baseline) for structure_type in STRUCTURE_TYPES]

            for _ in range(300):
                if rng.random() < 0.45:
                    index = rng.randrange(size)
                    delta = rng.randint(-50, 50)
                    baseline[index] += delta
                    for structure in structures:
                        structure.add(index, delta)
                else:
                    left = rng.randrange(size)
                    right = rng.randrange(left, size)
                    expected = sum(baseline[left : right + 1])
                    for structure in structures:
                        with self.subTest(structure=structure.name, size=size):
                            self.assertEqual(
                                structure.range_sum(left, right), expected
                            )

    def test_invalid_inputs_raise_clear_errors(self) -> None:
        """Out-of-range indices and reversed ranges raise exceptions."""
        for structure_type in STRUCTURE_TYPES:
            structure = structure_type([1, 2, 3])
            with self.subTest(structure=structure_type.name):
                with self.assertRaises(IndexError):
                    structure.add(-1, 2)
                with self.assertRaises(IndexError):
                    structure.add(3, 2)
                with self.assertRaises(IndexError):
                    structure.range_sum(0, 3)
                with self.assertRaises(IndexError):
                    structure.range_sum(-1, 1)
                with self.assertRaises(ValueError):
                    structure.range_sum(2, 1)

    def test_single_element(self) -> None:
        """A one-value array supports update and query."""
        for structure_type in STRUCTURE_TYPES:
            with self.subTest(structure=structure_type.name):
                structure = structure_type([9])
                structure.add(0, -4)
                self.assertEqual(structure.range_sum(0, 0), 5)

    def test_empty_input(self) -> None:
        """An empty array builds, has length 0, and rejects every index."""
        for structure_type in STRUCTURE_TYPES:
            with self.subTest(structure=structure_type.name):
                structure = structure_type([])
                self.assertEqual(len(structure), 0)
                with self.assertRaises(IndexError):
                    structure.add(0, 1)

    def test_storage_matches_analysis(self) -> None:
        """Reported storage equals the space formula from the report."""
        size = 100
        values = list(range(size))
        expected = {
            "Fenwick Tree": (size + 1) * 8,
            "Segment Tree": 2 * size * 8,
            "Square Root Decomposition": (size + 10) * 8,  # b = 10 blocks
        }
        for structure_type in STRUCTURE_TYPES:
            with self.subTest(structure=structure_type.name):
                structure = structure_type(values)
                self.assertEqual(structure.storage_bytes(), expected[structure.name])

    def test_factory(self) -> None:
        """Short names map to the right classes; unknown names fail."""
        self.assertEqual(create_structure("fenwick", [1]).name, "Fenwick Tree")
        self.assertEqual(create_structure("segment", [1]).name, "Segment Tree")
        self.assertEqual(create_structure(" SQRT ", [1]).name, "Square Root Decomposition")
        with self.assertRaises(ValueError):
            create_structure("unknown", [1])


if __name__ == "__main__":
    unittest.main()
