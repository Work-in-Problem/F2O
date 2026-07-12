"""Fixed-width text tables over tab-separated files."""


def read_rows(path):
    """Read a TSV file as a list of cell lists (no header handling)."""
    return [line.rstrip("\n").split("\t") for line in open(path) if line.strip()]


def read_table(path):
    """Read a TSV file as (header, rows)."""
    fh = open(path)
    header = fh.readline().rstrip("\n").split("\t")
    rows = [line.rstrip("\n").split("\t") for line in fh if line.strip()]
    return header, rows


def format_table(header, rows):
    """Render header + rows as aligned fixed-width text."""
    widths = [len(cell) for cell in header]
    for row in rows:
        for i, cell in enumerate(row[: len(widths)]):
            widths[i] = max(widths[i], len(cell))
    out = ["  ".join(cell.ljust(w) for cell, w in zip(header, widths))]
    for row in rows:
        out.append("  ".join(cell.ljust(w) for cell, w in zip(row, widths)))
    return "\n".join(out)


def write_table(header, rows, path):
    """Format and write a table to disk."""
    with open(path, "w") as fh:
        fh.write(format_table(header, rows) + "\n")
