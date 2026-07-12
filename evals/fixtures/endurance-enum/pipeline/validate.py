"""Schema checks for JSONL event files."""
import json


def load_schema(path):
    """Load a schema description ({"required": [field, ...]})."""
    return json.loads(open(path).read())


def _scan(fh, required):
    """Collect one problem string per missing required field."""
    problems = []
    for lineno, line in enumerate(fh, 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        for field in required:
            if field not in obj:
                problems.append("line {}: missing {}".format(lineno, field))
    return problems


def validate_file(path, schema):
    """Validate a JSONL file against a schema; return problem strings."""
    fh = open(path)
    return _scan(fh, schema.get("required", []))
