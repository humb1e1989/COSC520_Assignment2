"""Iterative segment tree implementation for dynamic range sums."""

from array import array
from collections.abc import Sequence

from .base import RangeSumStructure


class SegmentTree(RangeSumStructure):
    """Represent interval sums in a compact iterative binary tree."""

    name = "Segment Tree"

    def __init__(self, values: Sequence[int]) -> None:
        """Build an iterative segment tree in O(n) time.

        Input:
            values: Initial integer sequence.
        Output:
            None. Leaves and internal interval sums are initialized.
        Purpose:
            Support O(log n) point additions and O(log n) range sums.
        """
        self._size = len(values)
        # Leaves live in tree[n:2n]; node p has children 2p and 2p + 1, so
        # each internal node tree[1:n] stores the sum of its two children.
        self._tree = array("q", [0]) * (2 * self._size)
        for index, value in enumerate(values):
            self._tree[self._size + index] = value
        for position in range(self._size - 1, 0, -1):
            self._tree[position] = (
                self._tree[2 * position] + self._tree[2 * position + 1]
            )

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
            None. The leaf and all ancestors are updated.
        Purpose:
            Maintain correct interval sums after a point addition.
        """
        self._validate_index(index)
        position = self._size + index
        self._tree[position] += delta
        position //= 2
        while position >= 1:
            self._tree[position] = (
                self._tree[2 * position] + self._tree[2 * position + 1]
            )
            position //= 2

    def range_sum(self, left: int, right: int) -> int:
        """Return an inclusive range sum in O(log n) time.

        Input:
            left: Zero-based inclusive lower endpoint.
            right: Zero-based inclusive upper endpoint.
        Output:
            Sum from ``left`` through ``right``.
        Purpose:
            Combine the minimum set of disjoint segment-tree nodes.
        """
        self._validate_range(left, right)
        left += self._size
        right += self._size + 1  # Convert to a half-open interval.
        total = 0
        while left < right:
            if left & 1:
                total += self._tree[left]
                left += 1
            if right & 1:
                right -= 1
                total += self._tree[right]
            left //= 2
            right //= 2
        return total

    def storage_bytes(self) -> int:
        """Return bytes occupied by the internal signed-64-bit array.

        Input:
            None.
        Output:
            ``2n * 8`` bytes: ``n`` leaves plus ``n - 1`` internal nodes and
            one unused slot at index 0.
        Purpose:
            Report principal storage for the space comparison.
        """
        return len(self._tree) * self._tree.itemsize

