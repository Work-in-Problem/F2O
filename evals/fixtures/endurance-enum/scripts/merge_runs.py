#!/usr/bin/env python3
"""Merge several key<TAB>count summary files into one.

Usage: python3 scripts/merge_runs.py OUT SUMMARY [SUMMARY ...]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import export


class MergeCursor:
    """Walk one summary file, one key/count pair at a time."""

    def __init__(self, path):
        self.path = path
        self._fh = open(path)

    def next_pair(self):
        """Return the next (key, count) pair, or None at end of file."""
        for line in self._fh:
            if line.strip():
                key, _, value = line.rstrip("\n").partition("\t")
                return key, int(value)
        return None


def merge(paths):
    """Sum counters across the given summary files."""
    merged = {}
    for path in paths:
        cursor = MergeCursor(path)
        while True:
            pair = cursor.next_pair()
            if pair is None:
                break
            merged[pair[0]] = merged.get(pair[0], 0) + pair[1]
    return merged


def main(argv):
    if len(argv) < 3:
        print("usage: merge_runs.py OUT SUMMARY [SUMMARY ...]", file=sys.stderr)
        return 2
    merged = merge(argv[2:])
    export.write_summary(merged, argv[1])
    print("merged {} file(s) into {}".format(len(argv) - 2, argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
