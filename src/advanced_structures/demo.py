"""Small, human-readable demonstration of equivalent structure behavior."""

from .factory import STRUCTURE_TYPES


def main() -> None:
    """Run the same operations on all structures and print their answers.

    Input:
        None.
    Output:
        None. One line per structure is printed to standard output.
    Purpose:
        Show on a tiny example that all three structures return identical
        range sums before and after a point update.
    """
    values = [4, -2, 7, 3, 1, 8]
    print(f"Initial values: {values}")
    for structure_type in STRUCTURE_TYPES:
        structure = structure_type(values)
        before = structure.range_sum(1, 4)
        structure.add(2, 5)
        after = structure.range_sum(1, 4)
        print(
            f"{structure_type.name:28s} "
            f"sum[1,4]={before:2d}; after add(2,+5)={after:2d}"
        )


if __name__ == "__main__":
    main()

