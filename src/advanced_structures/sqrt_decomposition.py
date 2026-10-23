"""Square-root decomposition for dynamic range-sum queries."""

from array import array
from collections.abc import Sequence
from math import isqrt

from .base import RangeSumStructure


class SqrtDecomposition(RangeSumStructure):
    """Partition values into approximately square-root-sized blocks."""

    name = "Square Root Decomposition"

    def __init__(self, values: Sequence[int]) -> None:
        """Build values and block sums in O(n) time.

        Input:
            values: Initial integer sequence.
        Output:
            None. Values and their block totals are initialized.
        Purpose:
            Support O(1) point additions and O(sqrt(n)) range sums.
        """
        self._size = len(values)
        # Use b = ceil(sqrt(n)) so that there are at most ceil(sqrt(n)) blocks;
        # this balances the boundary scan and the full-block scan in queries.
        root = isqrt(self._size)
        needs_round_up = root * root < self._size
        self._block_size = max(1, root + needs_round_up)
        block_count = (self._size + self._block_size - 1) // self._block_size
        self._values = array("q", values)
        self._block_sums = array("q", [0]) * block_count
        for index, value in enumerate(self._values):
            self._block_sums[index // self._block_size] += value

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
        """Add ``delta`` at a zero-based index in O(1) time.

        Input:
            index: Zero-based position to update.
            delta: Signed integer increment.
        Output:
            None. The value and its block total are updated.
        Purpose:
            Maintain consistent raw values and block summaries.
        """
        self._validate_index(index)
        self._values[index] += delta
        self._block_sums[index // self._block_size] += delta

    def range_sum(self, left: int, right: int) -> int:
        """Return an inclusive range sum in O(sqrt(n)) time.

        Input:
            left: Zero-based inclusive lower endpoint.
            right: Zero-based inclusive upper endpoint.
        Output:
            Sum from ``left`` through ``right``.
        Purpose:
            Combine boundary values with complete block sums.
        """
        self._validate_range(left, right)
        total = 0

        # Consume values until ``left`` reaches a block boundary.
        while left <= right and left % self._block_size != 0:
            total += self._values[left]
            left += 1

        # Consume every complete block inside the query interval.
        while left + self._block_size - 1 <= right:
            total += self._block_sums[left // self._block_size]
            left += self._block_size

        # Consume any remaining values at the right boundary.
        while left <= right:
            total += self._values[left]
            left += 1
        return total

    def storage_bytes(self) -> int:
        """Return bytes occupied by the value and block-sum arrays.

        Input:
            None.
        Output:
            ``(n + ceil(n / b)) * 8`` bytes, where ``b`` is the block size.
        Purpose:
            Report principal storage for the space comparison.
        """
        return (
            len(self._values) * self._values.itemsize
            + len(self._block_sums) * self._block_sums.itemsize
        )

