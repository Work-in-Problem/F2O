import random
import threading
import time
import unittest

from telemetry import TelemetrySink


class TestDirectRecords(unittest.TestCase):
    def test_record_accumulates_events(self):
        sink = TelemetrySink()
        sink.record()
        sink.record(4)
        self.assertEqual(sink.events_total(), 5)

    def test_record_rejects_nonpositive_count(self):
        sink = TelemetrySink()
        with self.assertRaises(ValueError):
            sink.record(0)


class TestBatchAbsorb(unittest.TestCase):
    def test_absorb_batch_updates_totals(self):
        sink = TelemetrySink()
        size = sink.absorb_batch([("evt", n) for n in range(7)])
        self.assertEqual(size, 7)
        self.assertEqual(sink.events_total(), 7)
        self.assertEqual(sink.batches_absorbed(), 1)
        self.assertEqual(sink.peak_batch_size(), 7)

    def test_absorb_batch_rejects_empty_batch(self):
        sink = TelemetrySink()
        with self.assertRaises(ValueError):
            sink.absorb_batch([])


class TestConcurrentCollectors(unittest.TestCase):
    COLLECTORS = 6
    ARRIVAL_WINDOW = 0.18  # collectors finish gathering over a ~180 ms window
    GATHER_DELAY = 0.001   # per-event gather pause upper bound (seconds)

    def batch_size(self, index):
        # Collectors see uneven traffic, so batch sizes vary per collector.
        return 8 + (index % 6)

    def test_concurrent_batches_are_all_counted(self):
        sink = TelemetrySink()
        errors = []

        def collector(index, start_delay):
            # Each collector finishes its gather at some point in the window.
            time.sleep(start_delay)
            try:
                batch = []
                for n in range(self.batch_size(index)):
                    batch.append(("evt", index, n))
                    time.sleep(random.uniform(0.0, self.GATHER_DELAY))
                sink.absorb_batch(batch)
            except Exception as exc:  # pragma: no cover - surfaced via assert
                errors.append(exc)

        threads = [
            threading.Thread(
                target=collector,
                args=(i, random.uniform(0.0, self.ARRIVAL_WINDOW)),
            )
            for i in range(self.COLLECTORS)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        expected = sum(self.batch_size(i) for i in range(self.COLLECTORS))
        self.assertEqual(errors, [])
        self.assertEqual(sink.batches_absorbed(), self.COLLECTORS)
        self.assertEqual(sink.events_total(), expected)


if __name__ == "__main__":
    unittest.main()
