"""Fenwick tree implementation for point additions and range-sum queries."""

from array import array
from collections.abc import Sequence

from .base import RangeSumStructure


class FenwickTree(RangeSumStructure):
    """Store prefix sums in a one-based Binary Indexed Tree."""

    name = "Fenwick Tree"

    def __init__(self, values: Sequence[int]) -> None:
        """Build a Fenwick tree in linear time.

        Input:
            values: Initial integer sequence.
        Output:
            None. Internal one-based partial sums are created.
        Purpose:
            Support O(log n) point additions and O(log n) range sums.
        """
        self._size = len(values)
        self._tree = array("q", [0]) * (self._size + 1)

        # First copy each value into its one-based leaf position.
        for position, value in enumerate(values, start=1):
            self._tree[position] = value

        # Propagate each partial sum once to obtain an O(n) construction.
        for position in range(1, self._size + 1):
            parent = position + (position & -position)
            if parent <= self._size:
                self._tree[parent] += self._tree[position]

    def __len__(self) -> int:
        """Return the number of represented values.

        Input:
            None.
        Output:
            Number of array positions ``n``.
        Purpose:
            Support ``len()`` and the shared index validation.
        """
        return self._size

    def add(self, index: int, delta: int) -> None:
        """Add ``delta`` at a zero-based index in O(log n) time.

        Input:
            index: Zero-based position to update.
            delta: Signed integer increment.
        Output:
            None. All affected partial sums are updated.
        Purpose:
            Perform a point addition without rebuilding the tree.
        """
        self._validate_index(index)
        position = index + 1
        while position <= self._size:
            self._tree[position] += delta
            position += position & -position

    def prefix_sum(self, right: int) -> int:
        """Return the inclusive prefix sum ending at ``right``.

        Input:
            right: Zero-based inclusive upper endpoint; -1 represents an empty prefix.
        Output:
            Sum of values from index 0 through ``right``.
        Purpose:
            Supply the primitive operation used to answer range sums.
        """
        if right == -1:
            return 0
        self._validate_index(right)
        total = 0
        position = right + 1
        while position > 0:
            total += self._tree[position]
            position -= position & -position
        return total

    def range_sum(self, left: int, right: int) -> int:
        """Return an inclusive range sum in O(log n) time.

        Input:
            left: Zero-based inclusive lower endpoint.
            right: Zero-based inclusive upper endpoint.
        Output:
            Sum from ``left`` through ``right``.
        Purpose:
            Answer a range query by subtracting two prefix sums.
        """
        self._validate_range(left, right)
        return self.prefix_sum(right) - self.prefix_sum(left - 1)

    def storage_bytes(self) -> int:
        """Return bytes occupied by the internal signed-64-bit array.

        Input:
            None.
        Output:
            ``(n + 1) * 8`` bytes for the one-based tree array.
        Purpose:
            Report principal storage for the space comparison.
        """
        return len(self._tree) * self._tree.itemsize

