import random
import threading
import time
import unittest

from store import InventoryStore


class TestSequentialReservations(unittest.TestCase):
    def test_sequential_reservations_reduce_stock(self):
        store = InventoryStore({"widget": 10})
        for _ in range(4):
            store.reserve("widget", 2)
        self.assertEqual(store.stock("widget"), 2)

    def test_reserve_rejects_insufficient_stock(self):
        store = InventoryStore({"widget": 1})
        with self.assertRaises(ValueError):
            store.reserve("widget", 5)

    def test_reserve_appends_audit_record(self):
        store = InventoryStore({"widget": 10})
        store.reserve("widget", 3)
        self.assertEqual(store.audit_log(), [("widget", 3, 10)])


class TestConcurrentReservations(unittest.TestCase):
    WORKERS = 4
    BURST_WINDOW = 0.08  # orders arrive spread over an 80 ms burst

    def test_concurrent_reservations_are_all_applied(self):
        store = InventoryStore({"widget": 500})
        errors = []

        def worker(arrival_delay):
            # Each order arrives at some point during the burst.
            time.sleep(arrival_delay)
            try:
                store.reserve("widget", 1)
            except Exception as exc:  # pragma: no cover - surfaced via assert
                errors.append(exc)

        threads = [
            threading.Thread(
                target=worker, args=(random.uniform(0.0, self.BURST_WINDOW),)
            )
            for _ in range(self.WORKERS)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(store.audit_log()), self.WORKERS)
        self.assertEqual(store.stock("widget"), 500 - self.WORKERS)


if __name__ == "__main__":
    unittest.main()
