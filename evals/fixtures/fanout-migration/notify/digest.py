"""Daily-digest send-time computation."""

from datetime import timedelta

from notify.whenutil import parse_when

DIGEST_HOUR = 8  # daily digests go out at 08:00 local time


def next_digest_after(anchor_text):
    """First daily digest send time strictly after the anchor timestamp."""
    anchor = parse_when(anchor_text)
    if anchor is None:
        raise ValueError("unreadable anchor timestamp: %r" % (anchor_text,))
    candidate = anchor.replace(hour=DIGEST_HOUR, minute=0, second=0, microsecond=0)
    if candidate <= anchor:
        candidate += timedelta(days=1)
    return candidate


def digest_times_between(start_text, end_text):
    """Every digest send time in the inclusive window."""
    start = parse_when(start_text)
    end = parse_when(end_text)
    if start is None or end is None:
        raise ValueError("unreadable digest window bounds")
    sends = []
    candidate = start.replace(hour=DIGEST_HOUR, minute=0, second=0, microsecond=0)
    if candidate < start:
        candidate += timedelta(days=1)
    while candidate <= end:
        sends.append(candidate)
        candidate += timedelta(days=1)
    return sends
