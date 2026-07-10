"""Render user-facing notification messages."""

from notify.money import fmt_amount

TEMPLATES = {
    "receipt": "Payment received from {payer}: {amount}. Ref {ref}.",
    "reminder": "Reminder: {payer} owes {amount}. Ref {ref}.",
}


class TemplateError(KeyError):
    """Raised for an unknown message kind."""


def render(kind, payer, amount_cents, ref):
    """Render one message of ``kind`` for a payer/amount/reference."""
    try:
        tpl = TEMPLATES[kind]
    except KeyError:
        raise TemplateError("unknown message kind: %r" % (kind,))
    return tpl.format(payer=payer, amount=fmt_amount(amount_cents), ref=ref)


def receipt_lines(records):
    """One receipt message per ingest-shaped record, in input order."""
    return [
        render("receipt", r["payer"], r["amount_cents"], r["id"]) for r in records
    ]


def digest(records):
    """One-line ops digest for a batch of ingest-shaped records."""
    total = sum(r["amount_cents"] for r in records)
    return "digest: %s across %d payments" % (fmt_amount(total), len(records))
