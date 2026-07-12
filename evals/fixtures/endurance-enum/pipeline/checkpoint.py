"""Persist pipeline progress between runs."""
import json

_open = open  # module-level alias so test stubs stay local to this module


def load_checkpoint(path):
    """Return the saved state, or a fresh state when none exists."""
    try:
        fh = open(path)
    except FileNotFoundError:
        return {"offset": 0}
    return json.loads(fh.read())


def save_checkpoint(state, path):
    """Serialize the state dict with stable key order."""
    fh = _open(path, "w")
    fh.write(json.dumps(state, sort_keys=True))
