"""JSON helpers with stable formatting."""
import json


def load_json(path):
    """Load one JSON document."""
    return json.loads(open(path).read())


def _write(obj, fh):
    json.dump(obj, fh, indent=2, sort_keys=True)
    fh.write("\n")


def dump_json(obj, path):
    """Write one JSON document with stable formatting."""
    fh = open(path, "w")
    _write(obj, fh)


def load_jsonl(path):
    """Load a JSON-lines file, skipping blank lines."""
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]
