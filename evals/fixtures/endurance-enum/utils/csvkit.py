"""CSV helpers (thin wrappers around the csv module)."""
import csv


def read_csv(path):
    """Read a CSV file as a list of dicts."""
    fh = open(path, newline="")
    return list(csv.DictReader(fh))


def column(path, name):
    """One column of a CSV file, in row order."""
    return [row[name] for row in csv.DictReader(open(path, newline=""))]


def write_csv_rows(path, fieldnames, rows):
    """Write dict rows as CSV with the given header."""
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
