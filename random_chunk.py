"""Print a random sample of chunks for manual inspection.

For each chunk, ask: does this make sense on its own? Could someone answer a
question from this chunk alone, without reading what comes before or after?

Usage:
  python random_chunk.py            # 5 random chunks
  python random_chunk.py 8          # 8 random chunks
  python random_chunk.py 5 --seed 42  # reproducible sample (same 5 each run)
"""

import argparse
import random

import chunk


def main():
    parser = argparse.ArgumentParser(description="Print random chunks for inspection.")
    parser.add_argument("n", nargs="?", type=int, default=5, help="how many chunks (default 5)")
    parser.add_argument("--seed", type=int, default=None, help="fix the sample for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    chunks = chunk.chunk_corpus()
    sample_size = min(args.n, len(chunks))
    sample = random.sample(chunks, sample_size)

    print(f"Showing {sample_size} of {len(chunks)} chunks "
          f"(size={chunk.CHUNK_SIZE}, overlap={chunk.CHUNK_OVERLAP})\n")
    for i, c in enumerate(sample, 1):
        print(f"########## RANDOM CHUNK {i}  [{c['source']}]  len={len(c['text'])} ##########")
        print(c["text"])
        print()


if __name__ == "__main__":
    main()
