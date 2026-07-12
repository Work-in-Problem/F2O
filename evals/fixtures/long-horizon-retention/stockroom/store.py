"""Load and save the JSON inventory data file."""

import json
import sys


def fail(message):
    """Print an error in the tool's standard format and exit with code 2."""
    print("error: {}".format(message), file=sys.stderr)
    sys.exit(2)


def load(path):
    """Return the items mapping from the data file at `path`.

    Exits via fail() when the file is unreadable, not JSON, or not in the
    expected shape.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        fail("cannot read {}: {}".format(path, exc.strerror))
    except ValueError:
        fail("{}: not valid JSON".format(path))
    if not isinstance(data, dict) or not isinstance(data.get("items"), dict):
        fail("{}: unrecognized data-file format".format(path))
    return data["items"]


def save(path, items):
    """Write `items` to `path` deterministically (sorted keys, indent 2)."""
    payload = {"items": items}
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
