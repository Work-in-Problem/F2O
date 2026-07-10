"""Overdue-invoice reminder planning."""

from datetime import timedelta

from billing.timeparse import parse_when

# Days after the due date at which reminders go out.
REMINDER_STEPS_DAYS = (3, 10, 21)


def is_overdue(invoice, as_of_text):
    """True when the invoice is past due at the given timestamp."""
    as_of = parse_when(as_of_text)
    if as_of is None:
        raise ValueError("unreadable as-of timestamp: %r" % (as_of_text,))
    return as_of > invoice.due_at


def reminders_due(invoice, as_of_text):
    """Reminder times that have already been reached at the given timestamp."""
    as_of = parse_when(as_of_text)
    if as_of is None:
        raise ValueError("unreadable as-of timestamp: %r" % (as_of_text,))
    steps = [invoice.due_at + timedelta(days=d) for d in REMINDER_STEPS_DAYS]
    return [when for when in steps if when <= as_of]
