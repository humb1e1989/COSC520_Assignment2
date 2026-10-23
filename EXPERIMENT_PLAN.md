# Experiment Plan

## Research question

How do Fenwick Tree, Segment Tree, and Square Root Decomposition compare in build time, dynamic range-sum workload time, and principal storage as the number of values grows?

## Controlled operations

- Point addition: `add(index, delta)`
- Inclusive range sum: `range_sum(left, right)`

All structures receive the same initial values and the same ordered operation list.

## Input sizes

- 10,000
- 100,000
- 1,000,000
- 5,000,000
- 10,000,000

Use smaller sizes for smoke tests before the full experiment.

## Workload

- 5,000 operations per measured run
- Three profiles: `mixed` (50% additions / 50% queries), `update` (100% additions), `query` (100% queries)
- Each structure is rebuilt from the same values before every profile
- Uniformly selected update positions
- Uniformly selected left endpoint, followed by a uniform right endpoint in `[left, n)`
- Dataset and workload seed: 520

## Repetition policy

Run five measured repetitions for each structure and size after the automatic unreported warm-up. Report the median and, if space permits, the interquartile range. The benchmark CSV preserves every repetition, and the plotting program uses the median at each input size.

## Measurements

- Build time in seconds
- Mixed workload time in seconds
- Operations per second
- Principal numeric-storage bytes
- Query checksum for cross-implementation validation

## Fairness controls

- Same machine and power mode
- Same CPython version
- No unrelated foreground applications
- Same input and operation seeds
- Same operation semantics
- Benchmark structures sequentially, not concurrently
- Run garbage collection before each build
- Keep plotting and file I/O outside measured regions

## Expected complexity

| Structure | Build | Point add | Range sum | Principal space |
|---|---:|---:|---:|---:|
| Fenwick Tree | O(n) | O(log n) | O(log n) | O(n) |
| Segment Tree | O(n) | O(log n) | O(log n) | O(n) |
| Square Root Decomposition | O(n) | O(1) | O(sqrt(n)) | O(n + sqrt(n)) |

## Required report interpretation

Explain both asymptotic behavior and constant-factor effects. In particular, an O(log n) Segment Tree may be slower than a Fenwick Tree because it stores more values and performs more memory accesses, while Square Root Decomposition may perform fast updates but slower large-range queries.

