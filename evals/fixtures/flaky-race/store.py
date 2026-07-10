"""In-memory inventory store shared by the order worker threads.

Each order worker reserves stock for one incoming order. A reservation
writes an audit record before committing the new stock level, so that a
crash between the two steps can be reconciled from the audit log.
"""

import time


class InventoryStore:
    """Tracks remaining stock per item while order workers reserve units."""

    #: Simulated latency (seconds) of flushing one audit record to disk.
    AUDIT_WRITE_LATENCY = 0.002

    def __init__(self, initial_stock):
        self._stock = dict(initial_stock)
        self._audit_log = []

    def stock(self, item):
        """Return the remaining stock for `item`."""
        return self._stock[item]

    def audit_log(self):
        """Return a copy of the audit records written so far."""
        return list(self._audit_log)

    def reserve(self, item, quantity):
        """Reserve `quantity` units of `item` and return the remaining stock.

        Reads the current stock level, flushes an audit record for the
        reservation (simulated disk write), then commits the new level.
        """
        available = self._stock[item]
        if available < quantity:
            raise ValueError("insufficient stock for {!r}".format(item))
        self._audit_log.append((item, quantity, available))
        time.sleep(self.AUDIT_WRITE_LATENCY)  # audit flush before commit
        self._stock[item] = available - quantity
        return self._stock[item]
