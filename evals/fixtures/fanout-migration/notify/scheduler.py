"""Outbound notification scheduling."""

from notify.whenutil import parse_when


class SchedulerError(ValueError):
    """Raised when a notification cannot be scheduled or drained."""


class Scheduler(object):
    def __init__(self):
        self._queue = []

    def schedule(self, recipient, body, send_at_text):
        """Queue a notification for delivery at the given time."""
        send_at = parse_when(send_at_text)
        if send_at is None:
            raise SchedulerError("unreadable send time: %r" % (send_at_text,))
        item = {"recipient": recipient, "body": body, "send_at": send_at}
        self._queue.append(item)
        self._queue.sort(key=lambda i: i["send_at"])
        return item

    def due(self, now_text):
        """Pop and return every queued item due at the given clock time."""
        now = parse_when(now_text)
        if now is None:
            raise SchedulerError("unreadable clock time: %r" % (now_text,))
        ready = [i for i in self._queue if i["send_at"] <= now]
        self._queue = [i for i in self._queue if i["send_at"] > now]
        return ready

    def pending_count(self):
        return len(self._queue)
