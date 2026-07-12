#!/usr/bin/env python3
"""Build the full text report for a finished run.

Usage: python3 scripts/build_report.py CONFIG OUT
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import ingest
from reportkit import render


def load_config(path):
    """Load the report configuration document."""
    fh = open(path)
    return json.loads(fh.read())


def read_notes(path):
    """Optional free-form notes appended to the report."""
    if not os.path.exists(path):
        return ""
    with open(path) as fh:
        return fh.read()


def main(argv):
    if len(argv) != 3:
        print("usage: build_report.py CONFIG OUT", file=sys.stderr)
        return 2
    config = load_config(argv[1])
    events = ingest.load_events(config["events_csv"])
    totals = {}
    for event in events:
        kind = event.get("kind", "unknown")
        totals[kind] = totals.get(kind, 0) + 1
    body = "\n".join("{}: {}".format(k, totals[k]) for k in sorted(totals))
    sections = [("Totals", body)]
    if "notes_file" in config:
        notes = read_notes(config["notes_file"])
        if notes:
            sections.append(("Notes", notes))
    render.render_page(sections, argv[2])
    print("wrote {}".format(argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
