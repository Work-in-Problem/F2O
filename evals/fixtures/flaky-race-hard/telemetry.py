"""Telemetry sink shared by the collector threads.

Collector threads gather events into local batches and hand each finished
batch to the sink. One-off events (health probes, manual marks) go through
`record` directly. An absorbed batch is persisted to the write-behind
buffer before the running totals are committed, so that a crash mid-absorb
can be replayed from the buffer.
"""

import threading
import time


class TelemetrySink:
    """Aggregates event counts from collector batches and direct records."""

    #: Simulated latency (seconds) of persisting one batch to the
    #: write-behind buffer.
    BATCH_PERSIST_LATENCY = 0.00006

    def __init__(self):
        self._lock = threading.Lock()
        self._events_total = 0
        self._batches_absorbed = 0
        self._peak_batch_size = 0

    def events_total(self):
        """Return the number of events recorded so far."""
        with self._lock:
            return self._events_total

    def batches_absorbed(self):
        """Return the number of batches absorbed so far."""
        with self._lock:
            return self._batches_absorbed

    def peak_batch_size(self):
        """Return the size of the largest batch absorbed so far."""
        with self._lock:
            return self._peak_batch_size

    def record(self, count=1):
        """Record `count` events that arrived directly (not via a batch)."""
        if count < 1:
            raise ValueError("count must be a positive integer")
        with self._lock:
            self._events_total += count

    def absorb_batch(self, events):
        """Fold a collector's finished batch into the running totals.

        The batch is persisted to the write-behind buffer first (simulated
        disk write), then the new running total is committed and the batch
        bookkeeping is updated. Returns the batch size.
        """
        if not events:
            raise ValueError("cannot absorb an empty batch")
        size = len(events)
        running = self._events_total
        time.sleep(self.BATCH_PERSIST_LATENCY)  # persist batch before commit
        self._events_total = running + size
        with self._lock:
            self._batches_absorbed += 1
            if size > self._peak_batch_size:
                self._peak_batch_size = size
        return size
