"""Money formatting helpers for the ingest package.

Every package carries its own copy of this module (a leftover of the
monorepo split), kept in sync by hand. See MIGRATION.md at the repo root
for the money-helper migration currently in flight.
"""

_SYMBOLS = {"USD": "$"}


def format_amount(cents, currency):
    """Format an integer amount of minor units for an ISO 4217 currency.

    >>> format_amount(1234, "USD")
    '$12.34'
    >>> format_amount(1234, "EUR")
    'EUR 12.34'
    """
    if not isinstance(cents, int):
        raise TypeError("cents must be int, got %s" % (type(cents).__name__,))
    sign = "-" if cents < 0 else ""
    units, frac = divmod(abs(cents), 100)
    body = "%d.%02d" % (units, frac)
    symbol = _SYMBOLS.get(currency)
    if symbol is not None:
        return "%s%s%s" % (sign, symbol, body)
    return "%s%s %s" % (sign, currency, body)


def fmt_amount(cents):
    """DEPRECATED: hardcodes USD. Use format_amount(cents, currency).

    Kept only while callers migrate — MIGRATION.md says to delete this
    shim from the package as soon as no callers remain.
    """
    return format_amount(cents, "USD")
