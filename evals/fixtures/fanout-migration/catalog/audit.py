"""Catalog change audit log."""

from catalog.dates import parse_when


class AuditLog(object):
    def __init__(self):
        self._events = []

    def log_change(self, sku, field, at_text):
        """Record that a product field changed at the given time."""
        at = parse_when(at_text)
        if at is None:
            raise ValueError("unreadable audit timestamp: %r" % (at_text,))
        event = {"sku": sku, "field": field, "at": at}
        self._events.append(event)
        return event

    def changes_since(self, cutoff_text):
        """Every recorded change at or after the cutoff."""
        cutoff = parse_when(cutoff_text)
        if cutoff is None:
            raise ValueError("unreadable audit cutoff: %r" % (cutoff_text,))
        return [e for e in self._events if e["at"] >= cutoff]
