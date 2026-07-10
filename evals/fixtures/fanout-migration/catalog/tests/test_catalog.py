import unittest
from datetime import datetime

from catalog.audit import AuditLog
from catalog.pricing import PriceSchedule
from catalog.products import ProductError, load_product


class TestLoadProduct(unittest.TestCase):
    def test_load_active_product(self):
        prod = load_product(
            {"sku": "SKU-1", "title": "Enamel mug", "added_at": "2024-01-15 10:00:00"}
        )
        self.assertEqual(prod.added_at, datetime(2024, 1, 15, 10, 0, 0))
        self.assertIsNone(prod.discontinued_at)
        self.assertTrue(prod.is_active(datetime(2024, 2, 1)))

    def test_discontinued_product_window(self):
        prod = load_product(
            {
                "sku": "SKU-2",
                "title": "Wax jacket",
                "added_at": "15/01/2024 10:00",
                "discontinued_at": "2024-03-01T00:00:00",
            }
        )
        self.assertTrue(prod.is_active(datetime(2024, 2, 1)))
        self.assertFalse(prod.is_active(datetime(2024, 3, 1)))

    def test_malformed_discontinued_is_ignored(self):
        # Legacy leniency: an unreadable discontinued_at silently means "active".
        prod = load_product(
            {
                "sku": "SKU-3",
                "title": "Tin whistle",
                "added_at": "2024-01-15 10:00:00",
                "discontinued_at": "someday",
            }
        )
        self.assertIsNone(prod.discontinued_at)

    def test_unreadable_added_at_is_an_error(self):
        with self.assertRaises(ProductError):
            load_product({"sku": "SKU-4", "added_at": "early spring"})


class TestPriceSchedule(unittest.TestCase):
    def test_base_price_before_any_change(self):
        sched = PriceSchedule(1200)
        sched.add_change(1500, "2024-05-01 00:00:00")
        self.assertEqual(sched.price_at("2024-04-30T23:59:59"), 1200)

    def test_latest_change_in_effect_wins(self):
        sched = PriceSchedule(1200)
        sched.add_change(1500, "2024-05-01 00:00:00")
        sched.add_change(1400, "01/06/2024 00:00")
        self.assertEqual(sched.price_at("2024-05-15 12:00:00"), 1500)
        self.assertEqual(sched.price_at("2024-06-02 12:00:00"), 1400)

    def test_unreadable_lookup_time_is_an_error(self):
        with self.assertRaises(ValueError):
            PriceSchedule(1200).price_at("mid-may")


class TestAuditLog(unittest.TestCase):
    def test_changes_since_filters_by_cutoff(self):
        log = AuditLog()
        log.log_change("SKU-1", "title", "2024-06-01 08:00:00")
        log.log_change("SKU-1", "price", "2024-06-03T09:30:00")
        recent = log.changes_since("02/06/2024 00:00")
        self.assertEqual([e["field"] for e in recent], ["price"])

    def test_unreadable_audit_timestamp_is_an_error(self):
        with self.assertRaises(ValueError):
            AuditLog().log_change("SKU-1", "title", "whenever")


if __name__ == "__main__":
    unittest.main()
