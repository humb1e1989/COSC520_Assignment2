# Dataset Record

## File

`values_10000000.bin`

## Contents

- 10,000,000 pseudorandom integers
- signed 64-bit little-endian binary representation
- value range: -1,000 through 1,000 inclusive
- generation seed: 520
- uncompressed size: 80,000,000 bytes
- SHA-256: `5569c493c1262c42cd55f582e3d72d893cdfc76282f614155e8bb6fdbc1169d8`

## Reproduction

From the installed project directory, the same file can be reproduced with:

```bash
python -m advanced_structures.benchmark \
  --generate \
  --sizes 10000000 \
  --operations 0 \
  --repetitions 1 \
  --seed 520 \
  --dataset data/values_10000000.bin \
  --output results/dataset_generation_check.csv
```

The benchmark generator uses `random.Random(520)` and writes values in chunks, so it does not create a large intermediate Python list.

## Report citation information

The final online dataset record should include the filename, size, value range, seed, binary format, SHA-256 checksum, upload date, and a persistent public URL. Add that URL to the Assignment 2 PDF.

