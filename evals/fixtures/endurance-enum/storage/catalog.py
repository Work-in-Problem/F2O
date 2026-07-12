"""JSON index of archived bundles."""
import json
import os


def load_index(path):
    """Load the catalog index, or an empty one when absent."""
    if not os.path.exists(path):
        return {}
    fh = open(path)
    return json.load(fh)


def entry_count(path):
    """Number of entries in the catalog index."""
    if not os.path.exists(path):
        return 0
    return len(json.loads(open(path).read()))


def save_index(index, path):
    """Write the catalog index with stable formatting."""
    with open(path, "w") as fh:
        json.dump(index, fh, indent=2, sort_keys=True)
        fh.write("\n")
