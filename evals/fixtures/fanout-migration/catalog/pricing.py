"""Scheduled price changes for catalog products."""

from catalog.dates import parse_when


class PriceSchedule(object):
    """Price changes over time for one SKU; the latest change in effect wins."""

    def __init__(self, base_price_cents):
        self.base_price_cents = base_price_cents
        self._changes = []  # (starts_at, price_cents), kept sorted

    def add_change(self, price_cents, starts_at_text):
        starts_at = parse_when(starts_at_text)
        if starts_at is None:
            raise ValueError("unreadable price-change start: %r" % (starts_at_text,))
        self._changes.append((starts_at, price_cents))
        self._changes.sort(key=lambda change: change[0])

    def price_at(self, at_text):
        at = parse_when(at_text)
        if at is None:
            raise ValueError("unreadable price lookup time: %r" % (at_text,))
        price = self.base_price_cents
        for starts_at, price_cents in self._changes:
            if starts_at <= at:
                price = price_cents
        return price
