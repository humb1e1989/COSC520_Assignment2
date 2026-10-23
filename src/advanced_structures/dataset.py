"""Deterministic binary-dataset generation and loading utilities."""

from array import array
from pathlib import Path
from random import Random
import sys


def generate_dataset(
    path: str | Path,
    count: int,
    seed: int = 520,
    minimum: int = -1_000,
    maximum: int = 1_000,
) -> Path:
    """Generate a reproducible signed-64-bit integer dataset.

    Input:
        path: Destination binary-file path.
        count: Number of integers to generate.
        seed: Pseudorandom seed recorded for reproducibility.
        minimum: Smallest possible generated value.
        maximum: Largest possible generated value.
    Output:
        Resolved ``Path`` of the written dataset.
    Purpose:
        Create up to ten million data points without a large text file.
    Raises:
        ValueError: If ``count`` is negative or ``minimum > maximum``.
    """
    if count < 0:
        raise ValueError("count must be non-negative")
    if minimum > maximum:
        raise ValueError("minimum cannot exceed maximum")

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rng = Random(seed)
    chunk_size = 100_000
    remaining = count
    with output.open("wb") as stream:
        while remaining:
            current_size = min(chunk_size, remaining)
            chunk = array(
                "q", (rng.randint(minimum, maximum) for _ in range(current_size))
            )
            if sys.byteorder != "little":
                chunk.byteswap()
            chunk.tofile(stream)
            remaining -= current_size
    return output


def load_dataset(path: str | Path, count: int | None = None) -> array:
    """Load all or a prefix of a little-endian signed-64-bit dataset.

    Input:
        path: Existing binary dataset.
        count: Optional maximum number of integers to load.
    Output:
        ``array('q')`` containing the requested values.
    Purpose:
        Provide memory-efficient input to each benchmark implementation.
    Raises:
        ValueError: If ``count`` is negative or exceeds the stored values.
    """
    if count is not None and count < 0:
        raise ValueError("count must be non-negative")
    source = Path(path)
    values = array("q")
    with source.open("rb") as stream:
        if count is None:
            values.fromfile(stream, source.stat().st_size // values.itemsize)
        else:
            available = source.stat().st_size // values.itemsize
            values.fromfile(stream, min(count, available))
    if sys.byteorder != "little":
        values.byteswap()
    if count is not None and len(values) < count:
        raise ValueError(f"dataset has {len(values)} values, but {count} were requested")
    return values

