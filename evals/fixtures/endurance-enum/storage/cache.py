"""File-backed string cache keyed by name."""
import os


def _key_path(root, key):
    return os.path.join(root, key + ".cache")


def get(root, key, default=None):
    """Return the cached value, or default when absent."""
    path = _key_path(root, key)
    if not os.path.exists(path):
        return default
    fh = open(path)
    return fh.read()


def peek(root, key):
    """Return only the first line of a cached value, or None."""
    path = _key_path(root, key)
    if not os.path.exists(path):
        return None
    return open(path).readline().rstrip("\n")


def set(root, key, value):
    """Store a value under the key, replacing any previous value."""
    with open(_key_path(root, key), "w") as fh:
        fh.write(value)
