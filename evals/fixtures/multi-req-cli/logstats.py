#!/usr/bin/env python3
"""logstats — tiny command-line statistics for plain-text log files.

Log line format: ``TIMESTAMP LEVEL MESSAGE``, for example::

    2026-07-01T09:15:00 INFO Started worker pool
"""

import argparse
import sys
from datetime import datetime

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
LEVELS = ("INFO", "WARN", "ERROR")


def fail(message):
    """Print an error in the tool's standard format and exit with code 2."""
    print("error: {}".format(message), file=sys.stderr)
    sys.exit(2)


def parse_line(line):
    """Parse one log line into (timestamp, level, message).

    Returns None for malformed lines: wrong field count, unknown level, or a
    timestamp that does not match TIMESTAMP_FORMAT.
    """
    parts = line.strip().split(" ", 2)
    if len(parts) < 3:
        return None
    raw_ts, level, message = parts
    if level not in LEVELS:
        return None
    try:
        ts = datetime.strptime(raw_ts, TIMESTAMP_FORMAT)
    except ValueError:
        return None
    return ts, level, message


def load_entries(path):
    """Return (entries, skipped) from `path`; malformed lines are skipped."""
    entries = []
    skipped = 0
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                entry = parse_line(line)
                if entry is None:
                    skipped += 1
                else:
                    entries.append(entry)
    except OSError as exc:
        fail("cannot read {}: {}".format(path, exc.strerror))
    return entries, skipped


def cmd_count(args):
    entries, _ = load_entries(args.logfile)
    print("entries: {}".format(len(entries)))
    return 0


def cmd_errors(args):
    entries, _ = load_entries(args.logfile)
    for ts, level, message in entries:
        if level == "ERROR":
            print("{} {}".format(ts.strftime(TIMESTAMP_FORMAT), message))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="logstats",
        description="Tiny statistics for plain-text log files.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    p_count = subparsers.add_parser(
        "count", help="Count the valid log entries in a file."
    )
    p_count.add_argument("logfile")
    p_count.set_defaults(func=cmd_count)

    p_errors = subparsers.add_parser(
        "errors", help="Print every ERROR entry in a file."
    )
    p_errors.add_argument("logfile")
    p_errors.set_defaults(func=cmd_errors)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
