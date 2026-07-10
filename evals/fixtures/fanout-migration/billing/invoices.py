"""Invoice loading and validation."""

from datetime import timedelta

from billing.timeparse import parse_when

NET_TERMS_DAYS = 30


class InvoiceError(ValueError):
    """Raised when raw invoice fields cannot be turned into an Invoice."""


class Invoice(object):
    def __init__(self, number, issued_at, due_at):
        self.number = number
        self.issued_at = issued_at
        self.due_at = due_at

    def term_days(self):
        return (self.due_at - self.issued_at).days


def load_invoice(fields):
    """Build an Invoice from a raw field mapping (one imported CSV row).

    ``issued_at`` is required. ``due_at`` is optional and defaults to
    net-30 from the issue date.
    """
    number = (fields.get("number") or "").strip()
    if not number:
        raise InvoiceError("invoice number is required")

    issued_at = parse_when(fields.get("issued_at"))
    if issued_at is None:
        raise InvoiceError("invoice %s: unreadable issued_at" % number)

    due_at = parse_when(fields.get("due_at"))
    if due_at is None:
        due_at = issued_at + timedelta(days=NET_TERMS_DAYS)
    if due_at < issued_at:
        raise InvoiceError("invoice %s: due before issued" % number)

    return Invoice(number, issued_at, due_at)
