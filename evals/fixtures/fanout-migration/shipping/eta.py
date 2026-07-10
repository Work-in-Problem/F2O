"""Coarse delivery estimates."""

from datetime import timedelta

from shipping.timefmt import parse_when

# Speed bands: (max_km, transit_days).
_BANDS = ((50, 1), (500, 2), (2000, 4))
_FALLBACK_DAYS = 7


def estimate_eta(shipped_at_text, distance_km):
    """Estimated delivery time for a shipment that left at the given time."""
    shipped_at = parse_when(shipped_at_text)
    if shipped_at is None:
        raise ValueError("unreadable ship time: %r" % (shipped_at_text,))
    if distance_km < 0:
        raise ValueError("distance cannot be negative")
    for max_km, days in _BANDS:
        if distance_km <= max_km:
            return shipped_at + timedelta(days=days)
    return shipped_at + timedelta(days=_FALLBACK_DAYS)
