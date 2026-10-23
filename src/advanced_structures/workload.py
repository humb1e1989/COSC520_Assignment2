"""Deterministic mixed update/query workload generation."""

from dataclasses import dataclass
from random import Random


# Benchmarked workload profiles mapped to their point-update probability.
# ``mixed`` reflects a balanced application, while ``update`` and ``query``
# isolate the cost of each operation so that each bound can be checked alone.
WORKLOAD_RATIOS = {
    "mixed": 0.5,
    "update": 1.0,
    "query": 0.0,
}


@dataclass(frozen=True)
class Operation:
    """Represent one point addition or inclusive range-sum query.

    Attributes:
        kind: ``"add"`` for a point addition or ``"sum"`` for a range query.
        first: Update index for ``add``; left endpoint for ``sum``.
        second: Signed increment for ``add``; right endpoint for ``sum``.
    """

    kind: str
    first: int
    second: int


def generate_workload(
    size: int,
    operation_count: int,
    update_ratio: float = 0.5,
    seed: int = 520,
) -> list[Operation]:
    """Generate a reproducible mixture of updates and range queries.

    Input:
        size: Number of positions in the represented array.
        operation_count: Total operations to generate.
        update_ratio: Probability that an operation is a point addition.
        seed: Pseudorandom seed.
    Output:
        Ordered list of ``Operation`` records shared by all structures.
    Purpose:
        Guarantee that every implementation receives the same workload.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if operation_count < 0:
        raise ValueError("operation_count must be non-negative")
    if not 0.0 <= update_ratio <= 1.0:
        raise ValueError("update_ratio must be in [0, 1]")

    rng = Random(seed)
    operations: list[Operation] = []
    for _ in range(operation_count):
        if rng.random() < update_ratio:
            operations.append(
                Operation("add", rng.randrange(size), rng.randint(-100, 100))
            )
        else:
            left = rng.randrange(size)
            right = rng.randrange(left, size)
            operations.append(Operation("sum", left, right))
    return operations

