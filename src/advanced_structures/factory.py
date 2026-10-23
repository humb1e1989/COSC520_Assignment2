"""Factory helpers shared by the benchmark and command-line demonstration."""

from collections.abc import Sequence

from .base import RangeSumStructure
from .fenwick_tree import FenwickTree
from .segment_tree import SegmentTree
from .sqrt_decomposition import SqrtDecomposition


# Every compared implementation, in the order they are benchmarked and plotted.
STRUCTURE_TYPES = (FenwickTree, SegmentTree, SqrtDecomposition)


def create_structure(name: str, values: Sequence[int]) -> RangeSumStructure:
    """Create a selected structure from a case-insensitive short name.

    Input:
        name: One of ``fenwick``, ``segment``, or ``sqrt``.
        values: Initial integer sequence.
    Output:
        A newly built ``RangeSumStructure`` implementation.
    Purpose:
        Keep command-line programs independent from concrete constructors.
    Raises:
        ValueError: If ``name`` is not a known structure.
    """
    normalized = name.strip().lower()
    choices = {
        "fenwick": FenwickTree,
        "segment": SegmentTree,
        "sqrt": SqrtDecomposition,
    }
    if normalized not in choices:
        raise ValueError(f"unknown structure: {name}")
    return choices[normalized](values)

