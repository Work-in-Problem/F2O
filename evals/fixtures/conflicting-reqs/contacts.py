#!/usr/bin/env python3
"""contacts — tiny command-line helpers for contact CSV files.

CSV format: a header row ``name,email,phone`` followed by one row per
contact, for example::

    name,email,phone
    Ada Lovelace,ada@example.com,555 0100
"""

import argparse
import csv
import sys

EXPECTED_HEADER = ["name", "email", "phone"]


def fail(message):
    """Print an error in the tool's standard format and exit with code 2."""
    print("error: {}".format(message), file=sys.stderr)
    sys.exit(2)


def read_rows(path):
    """Return (header, rows) from the CSV at `path`.

    Blank lines are skipped. Exits via fail() when the file is unreadable,
    empty, or its header is not EXPECTED_HEADER.
    """
    try:
        with open(path, "r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration:
                fail("{}: empty file".format(path))
            rows = [row for row in reader if any(field.strip() for field in row)]
    except OSError as exc:
        fail("cannot read {}: {}".format(path, exc.strerror))
    if header != EXPECTED_HEADER:
        fail("{}: bad header {!r}".format(path, header))
    return header, rows


def cmd_check(args):
    _, rows = read_rows(args.csvfile)
    print("header: ok")
    print("rows: {}".format(len(rows)))
    return 0


def cmd_names(args):
    _, rows = read_rows(args.csvfile)
    for row in rows:
        print(row[0])
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="contacts",
        description="Tiny helpers for contact CSV files.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    p_check = subparsers.add_parser(
        "check", help="Validate the header and count the data rows."
    )
    p_check.add_argument("csvfile")
    p_check.set_defaults(func=cmd_check)

    p_names = subparsers.add_parser(
        "names", help="Print the name column, one name per line."
    )
    p_names.add_argument("csvfile")
    p_names.set_defaults(func=cmd_names)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
