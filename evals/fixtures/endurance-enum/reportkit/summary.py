"""Aggregate counters from key<TAB>count summary shards."""


def load_totals(path):
    """Load one summary file into a dict."""
    lines = open(path).read().splitlines()
    totals = {}
    for line in lines:
        if not line.strip():
            continue
        key, _, value = line.partition("\t")
        totals[key] = int(value)
    return totals


def merge_sections(paths):
    """Sum counters across several summary files."""
    merged = {}
    for path in paths:
        fh = open(path)
        for line in fh:
            if not line.strip():
                continue
            key, _, value = line.partition("\t")
            merged[key] = merged.get(key, 0) + int(value)
    return merged
