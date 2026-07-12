"""Read raw event exports into memory."""
import csv
import json


def load_events(path):
    """Parse a CSV export into a list of event dicts."""
    fh = open(path, newline="")
    reader = csv.DictReader(fh)
    events = []
    for row in reader:
        events.append({key: value.strip() for key, value in row.items()})
    return events


def read_header(path):
    """Return the column names of a CSV export."""
    line = open(path).readline()
    return [col.strip() for col in line.rstrip("\n").split(",")]


def load_batches(paths):
    """Load several JSONL batch files, oldest path first."""
    batches = []
    for path in sorted(paths):
        fh = open(path)
        batches.append([json.loads(line) for line in fh if line.strip()])
    return batches


def count_lines(path):
    """Number of non-blank lines in a file."""
    with open(path) as fh:
        return sum(1 for line in fh if line.strip())
