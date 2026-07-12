#!/usr/bin/env python3
"""Print quick kind counts for an events CSV.

Usage: python3 scripts/stats.py EVENTS_CSV [OUT_TSV]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import ingest


def kind_counts(events):
    """Count events by kind."""
    kinds = {}
    for event in events:
        kind = event.get("kind", "unknown")
        kinds[kind] = kinds.get(kind, 0) + 1
    return kinds


def write_stats(kinds, path):
    """Write kind<TAB>count lines, sorted by kind."""
    with open(path, "w") as fh:
        for kind in sorted(kinds):
            fh.write("{}\t{}\n".format(kind, kinds[kind]))


def main(argv):
    if len(argv) not in (2, 3):
        print("usage: stats.py EVENTS_CSV [OUT_TSV]", file=sys.stderr)
        return 2
    events = ingest.load_events(argv[1])
    kinds = kind_counts(events)
    for kind in sorted(kinds):
        print("{}\t{}".format(kind, kinds[kind]))
    print("total\t{}".format(len(events)))
    if len(argv) == 3:
        write_stats(kinds, argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
