"""Shared interface for the compared dynamic range-sum data structures."""

from abc import ABC, abstractmethod
from collections.abc import Sequence


class RangeSumStructure(ABC):
    """Abstract interface used by the benchmark and demonstration programs."""

    name = "RangeSumStructure"

    @abstractmethod
    def __init__(self, values: Sequence[int]) -> None:
        """Build the data structure from ``values``.

        Input:
            values: Initial integer sequence.
        Output:
            None. A new data structure is initialized.
        Purpose:
            Prepare the structure for point additions and inclusive range sums.
        """

    @abstractmethod
    def add(self, index: int, delta: int) -> None:
        """Add ``delta`` to one array element.

        Input:
            index: Zero-based position to update.
            delta: Signed amount added to the current value.
        Output:
            None. The structure is updated in place.
        Purpose:
            Apply the common point-update operation used in the comparison.
        """

    @abstractmethod
    def range_sum(self, left: int, right: int) -> int:
        """Return the inclusive sum from ``left`` through ``right``.

        Input:
            left: Zero-based inclusive lower endpoint.
            right: Zero-based inclusive upper endpoint.
        Output:
            Integer sum of the requested interval.
        Purpose:
            Execute the common range-query operation used in the comparison.
        """

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of represented values.

        Input:
            None.
        Output:
            Number of array positions ``n`` held by the structure.
        Purpose:
            Allow ``len(structure)`` and shared index validation.
        """

    @abstractmethod
    def storage_bytes(self) -> int:
        """Return the bytes used by the principal numeric storage arrays.

        Input:
            None.
        Output:
            Bytes occupied by the internal numeric arrays, excluding Python
            object headers.
        Purpose:
            Compare the space usage of the structures empirically.
        """

    def _validate_index(self, index: int) -> None:
        """Check that ``index`` addresses a stored value.

        Input:
            index: Zero-based position to check.
        Output:
            None.
        Purpose:
            Reject out-of-range positions before they corrupt internal arrays.
        Raises:
            IndexError: If ``index`` is outside ``[0, n)``.
        """
        if index < 0 or index >= len(self):
            raise IndexError(f"index {index} outside [0, {len(self)})")

    def _validate_range(self, left: int, right: int) -> None:
        """Check that ``[left, right]`` is a valid inclusive query range.

        Input:
            left: Zero-based inclusive lower endpoint.
            right: Zero-based inclusive upper endpoint.
        Output:
            None.
        Purpose:
            Give every implementation the same error behaviour.
        Raises:
            ValueError: If ``left > right``.
            IndexError: If either endpoint is outside ``[0, n)``.
        """
        if left > right:
            raise ValueError("left endpoint cannot exceed right endpoint")
        self._validate_index(left)
        self._validate_index(right)

