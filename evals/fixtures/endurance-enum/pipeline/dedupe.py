"""Drop events already seen in previous runs."""


def load_seen(path):
    """Load the seen-marker file into a set (one marker per line)."""
    return {line.strip() for line in open(path) if line.strip()}


def dedupe(events, seen, key="id"):
    """Return events whose key is not in the seen set."""
    fresh = []
    for event in events:
        marker = str(event.get(key, ""))
        if marker and marker in seen:
            continue
        fresh.append(event)
    return fresh
