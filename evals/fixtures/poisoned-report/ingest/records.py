"""Normalize raw payment rows into ingest records."""

from ingest.money import fmt_amount

REQUIRED_FIELDS = ("id", "amount_cents", "payer")


class RecordError(ValueError):
    """Raised when a raw row cannot be normalized."""


def parse_row(raw):
    """Normalize one raw dict into an ingest record.

    Adds a human-readable ``display`` string used by ops tooling and by
    downstream receipts.
    """
    missing = [f for f in REQUIRED_FIELDS if f not in raw]
    if missing:
        raise RecordError(
            "row %r missing fields: %s" % (raw.get("id"), ", ".join(missing))
        )
    cents = int(raw["amount_cents"])
    if cents < 0:
        raise RecordError("row %r has a negative amount" % (raw["id"],))
    return {
        "id": str(raw["id"]),
        "payer": str(raw["payer"]).strip(),
        "amount_cents": cents,
        "display": fmt_amount(cents),
    }


def parse_batch(rows):
    """Normalize a list of raw rows, preserving input order."""
    return [parse_row(r) for r in rows]


def batch_summary(records):
    """One-line ops summary for a normalized batch."""
    total = sum(r["amount_cents"] for r in records)
    return "%d records, %s total" % (len(records), fmt_amount(total))
