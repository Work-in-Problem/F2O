"""Append-only payment ledger for a billing account."""

from billing.timeparse import parse_when


class Ledger(object):
    def __init__(self):
        self._entries = []

    def record(self, invoice_number, amount_cents, paid_at_text):
        """Record a payment; entries are kept sorted by payment time."""
        paid_at = parse_when(paid_at_text)
        if paid_at is None:
            raise ValueError("unreadable payment timestamp: %r" % (paid_at_text,))
        if amount_cents <= 0:
            raise ValueError("payments must be positive")
        entry = {
            "invoice": invoice_number,
            "amount_cents": amount_cents,
            "paid_at": paid_at,
        }
        self._entries.append(entry)
        self._entries.sort(key=lambda e: e["paid_at"])
        return entry

    def paid_total(self, invoice_number):
        """Total cents recorded against one invoice."""
        return sum(
            e["amount_cents"] for e in self._entries if e["invoice"] == invoice_number
        )

    def entries_between(self, start_text, end_text):
        """Entries with start <= paid_at <= end (both ends inclusive)."""
        start = parse_when(start_text)
        end = parse_when(end_text)
        if start is None or end is None:
            raise ValueError("unreadable ledger window bounds")
        return [e for e in self._entries if start <= e["paid_at"] <= end]
