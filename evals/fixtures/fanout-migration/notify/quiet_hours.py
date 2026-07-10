"""Quiet-hours policy: no notifications late at night."""

from datetime import time, timedelta

from notify.whenutil import parse_when

QUIET_START = time(22, 0)  # 22:00
QUIET_END = time(7, 0)     # 07:00 the next morning


def is_quiet(at_text):
    """True when the timestamp falls inside the quiet window."""
    at = parse_when(at_text)
    if at is None:
        raise ValueError("unreadable timestamp: %r" % (at_text,))
    moment = at.time()
    return moment >= QUIET_START or moment < QUIET_END


def next_allowed(at_text):
    """Earliest time at or after the given timestamp outside quiet hours."""
    at = parse_when(at_text)
    if at is None:
        raise ValueError("unreadable timestamp: %r" % (at_text,))
    moment = at.time()
    if not (moment >= QUIET_START or moment < QUIET_END):
        return at
    morning = at.replace(
        hour=QUIET_END.hour, minute=0, second=0, microsecond=0
    )
    if moment >= QUIET_START:
        morning += timedelta(days=1)
    return morning
