"""Best-effort lock files for long-running jobs."""
import os

_open = open  # alias so the sandbox test harness can substitute a recorder


def acquire(path, owner):
    """Take the lock; returns False when someone already holds it."""
    if os.path.exists(path):
        return False
    fh = _open(path, "w")
    fh.write(owner + "\n")
    return True


def release(path):
    """Drop the lock if present; returns whether it existed."""
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def holder(path):
    """Current owner string, or None when unlocked."""
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return fh.read().strip()
