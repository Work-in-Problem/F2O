"""Shipment manifest records."""

from shipping.timefmt import parse_when


class ManifestError(ValueError):
    """Raised when raw shipment fields cannot be turned into a Shipment."""


class Shipment(object):
    def __init__(self, tracking_id, shipped_at, delivered_at=None):
        self.tracking_id = tracking_id
        self.shipped_at = shipped_at
        self.delivered_at = delivered_at

    def in_transit(self):
        return self.delivered_at is None

    def transit_seconds(self):
        if self.delivered_at is None:
            raise ManifestError("shipment %s is still in transit" % self.tracking_id)
        return int((self.delivered_at - self.shipped_at).total_seconds())


def load_shipment(fields):
    """Build a Shipment from a raw field mapping (one manifest row).

    ``shipped_at`` is required. ``delivered_at`` is optional — an empty or
    missing value means the shipment is still on the road.
    """
    tracking_id = (fields.get("tracking_id") or "").strip()
    if not tracking_id:
        raise ManifestError("tracking_id is required")

    shipped_at = parse_when(fields.get("shipped_at"))
    if shipped_at is None:
        raise ManifestError("shipment %s: unreadable shipped_at" % tracking_id)

    delivered_at = parse_when(fields.get("delivered_at"))
    if delivered_at is not None and delivered_at < shipped_at:
        raise ManifestError("shipment %s: delivered before shipped" % tracking_id)

    return Shipment(tracking_id, shipped_at, delivered_at)
