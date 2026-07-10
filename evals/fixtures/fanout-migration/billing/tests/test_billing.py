import unittest
from datetime import datetime

from billing.dunning import is_overdue, reminders_due
from billing.invoices import Invoice, InvoiceError, load_invoice
from billing.ledger import Ledger


class TestLoadInvoice(unittest.TestCase):
    def test_load_with_explicit_due_date(self):
        inv = load_invoice(
            {
                "number": "INV-1001",
                "issued_at": "2024-03-05 09:00:00",
                "due_at": "05/04/2024 09:00",
            }
        )
        self.assertEqual(inv.issued_at, datetime(2024, 3, 5, 9, 0, 0))
        self.assertEqual(inv.due_at, datetime(2024, 4, 5, 9, 0))
        self.assertEqual(inv.term_days(), 31)

    def test_missing_due_date_defaults_to_net_30(self):
        inv = load_invoice({"number": "INV-1002", "issued_at": "2024-03-05T09:00:00"})
        self.assertEqual(inv.due_at, datetime(2024, 4, 4, 9, 0, 0))

    def test_malformed_due_date_falls_back_to_net_30(self):
        # Legacy leniency: an unreadable due_at silently gets the default.
        inv = load_invoice(
            {
                "number": "INV-1003",
                "issued_at": "2024-03-05 09:00:00",
                "due_at": "end of month",
            }
        )
        self.assertEqual(inv.due_at, datetime(2024, 4, 4, 9, 0, 0))

    def test_unreadable_issue_date_is_an_error(self):
        with self.assertRaises(InvoiceError):
            load_invoice({"number": "INV-1004", "issued_at": "yesterday-ish"})

    def test_due_before_issued_is_an_error(self):
        with self.assertRaises(InvoiceError):
            load_invoice(
                {
                    "number": "INV-1005",
                    "issued_at": "2024-03-05 09:00:00",
                    "due_at": "2024-03-01 09:00:00",
                }
            )


class TestDunning(unittest.TestCase):
    def _invoice(self):
        return Invoice(
            "INV-2001", datetime(2024, 3, 1, 9, 0), datetime(2024, 3, 31, 9, 0)
        )

    def test_not_overdue_before_due_date(self):
        self.assertFalse(is_overdue(self._invoice(), "2024-03-30 09:00:00"))

    def test_overdue_after_due_date(self):
        self.assertTrue(is_overdue(self._invoice(), "01/05/2024 09:00"))

    def test_reminders_accumulate_as_time_passes(self):
        due = reminders_due(self._invoice(), "2024-04-12T00:00:00")
        self.assertEqual(
            due, [datetime(2024, 4, 3, 9, 0), datetime(2024, 4, 10, 9, 0)]
        )


class TestLedger(unittest.TestCase):
    def test_entries_kept_sorted_by_payment_time(self):
        led = Ledger()
        led.record("INV-1001", 5000, "2024-03-10 12:00:00")
        led.record("INV-1001", 2500, "05/03/2024 08:00")
        entries = led.entries_between("2024-03-01T00:00:00", "2024-03-31T00:00:00")
        self.assertEqual([e["amount_cents"] for e in entries], [2500, 5000])

    def test_paid_total_sums_a_single_invoice(self):
        led = Ledger()
        led.record("INV-1001", 5000, "2024-03-10 12:00:00")
        led.record("INV-9999", 100, "2024-03-11 12:00:00")
        self.assertEqual(led.paid_total("INV-1001"), 5000)

    def test_unreadable_payment_timestamp_is_an_error(self):
        with self.assertRaises(ValueError):
            Ledger().record("INV-1001", 5000, "when I got paid")


if __name__ == "__main__":
    unittest.main()
