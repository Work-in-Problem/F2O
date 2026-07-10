"""Scan-event tracking for shipments."""

from shipping.timefmt import parse_when


class TrackingLog(object):
    def __init__(self, tracking_id):
        self.tracking_id = tracking_id
        self._scans = []

    def add_scan(self, location, at_text):
        """Record a checkpoint scan; scans are kept sorted by time."""
        at = parse_when(at_text)
        if at is None:
            raise ValueError("unreadable scan timestamp: %r" % (at_text,))
        scan = {"location": location, "at": at}
        self._scans.append(scan)
        self._scans.sort(key=lambda s: s["at"])
        return scan

    def latest(self):
        """The most recent scan, or None when nothing has been scanned."""
        if not self._scans:
            return None
        return self._scans[-1]

    def scans_between(self, start_text, end_text):
        """Scans with start <= at <= end (both ends inclusive)."""
        start = parse_when(start_text)
        end = parse_when(end_text)
        if start is None or end is None:
            raise ValueError("unreadable scan window bounds")
        return [s for s in self._scans if start <= s["at"] <= end]
