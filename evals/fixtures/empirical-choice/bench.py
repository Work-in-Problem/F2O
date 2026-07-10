#!/usr/bin/env python3
"""Reference benchmark for words-svc — the workload lookup_many must serve.

Steady-state membership checking: five timed calls to lookup.lookup_many(),
each with its own deterministic sequence of 400,000 queries drawn from a
fixed pool of 20,000 strings (10,000 present in the wordlist, 10,000 absent),
so every pool string is queried ~20 times per run. One line is printed per
run, then a final `median_ms=` line (median of the 5 runs). Lower is better.

The workload is hash-derived (hashlib over counters — no RNG state), so it is
identical on every machine and Python version. Module import and workload
construction are NOT timed; only the lookup_many() calls are.

Run via ./bench.sh (or: python3 bench.py). Standard library only.
"""
import hashlib
import os
import sys
import time

import lookup  # the delivered implementation under test

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS_PATH = os.path.join(HERE, "data", "words.txt")

RUNS = 5
POOL_HITS = 10000
POOL_MISSES = 10000
N_QUERIES = 400000
_RUN_OFFSET = 7919  # prime; gives each run its own query sequence


def _idx(tag, i, mod):
    digest = hashlib.md5(("%s-%d" % (tag, i)).encode("ascii")).digest()
    return int.from_bytes(digest[:8], "big") % mod


def build_pool():
    with open(WORDS_PATH, encoding="ascii") as handle:
        words = handle.read().splitlines()
    hits = [words[_idx("hit", j, len(words))] for j in range(POOL_HITS)]
    # '#' never occurs in the wordlist, so these are guaranteed misses
    misses = [words[_idx("miss", j, len(words))] + "#" for j in range(POOL_MISSES)]
    return hits + misses


def main():
    pool = build_pool()
    base = [_idx("q", k, len(pool)) for k in range(N_QUERIES)]
    run_queries = [
        [pool[(i + r * _RUN_OFFSET) % len(pool)] for i in base]
        for r in range(RUNS)
    ]

    # one untimed warmup + sanity check on a small slice
    warm = lookup.lookup_many(run_queries[0][:1000])
    if len(warm) != 1000:
        sys.exit("bench: lookup_many returned %d results for 1000 queries" % len(warm))

    times_ms = []
    for r in range(RUNS):
        queries = run_queries[r]
        start = time.perf_counter()
        result = lookup.lookup_many(queries)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        if len(result) != len(queries):
            sys.exit(
                "bench: result length %d != %d queries" % (len(result), len(queries))
            )
        times_ms.append(elapsed_ms)
        print("run%d_ms=%.1f" % (r + 1, elapsed_ms))
    times_ms.sort()
    print(
        "median_ms=%.1f runs=%d queries_per_run=%d"
        % (times_ms[RUNS // 2], RUNS, N_QUERIES)
    )


if __name__ == "__main__":
    main()
