"""Cross-package pipeline suite.

Raw rows -> ingest records -> ledger book -> month-end rollover -> notify
messages. Runs as part of the repo gate: `make test-all`.
"""

import unittest

from ingest.records import batch_summary, parse_batch
from ledger.book import Book
from ledger.jobs.rollover import close_period
from notify.messages import receipt_lines, render

RAW_ROWS = [
    {"id": "p-100", "amount_cents": 1999, "payer": "Ada"},
    {"id": "p-101", "amount_cents": 250, "payer": "Grace"},
    {"id": "p-102", "amount_cents": 125000, "payer": "Alan"},
]


class TestPipeline(unittest.TestCase):
    def _booked(self):
        records = parse_batch(RAW_ROWS)
        book = Book()
        for r in records:
            book.post("payments:%s" % r["payer"].lower(), r["amount_cents"], r["id"])
        return records, book

    def test_ingest_to_ledger_balances(self):
        records, book = self._booked()
        self.assertEqual(book.balance("payments:ada"), 1999)
        self.assertEqual(book.balance("payments:alan"), 125000)
        self.assertEqual(batch_summary(records), "3 records, $1272.49 total")

    def test_month_end_rollover_carries_balances(self):
        _, book = self._booked()
        nxt, lines = close_period(book, "2026-06")
        self.assertEqual(nxt.balance("payments:alan"), 125000)
        self.assertIn("payments:alan: closed 2026-06 at $1250.00", lines)
        self.assertEqual(lines[-1], "rollover 2026-06 complete: 3 account(s)")
        self.assertEqual(
            nxt.statement("payments:grace"),
            ["$2.50  carry-forward 2026-06", "balance: $2.50"],
        )

    def test_rollover_summary_feeds_notify(self):
        records, book = self._booked()
        _, lines = close_period(book, "2026-06")
        self.assertEqual(len(lines), 4)
        msgs = receipt_lines(records)
        self.assertIn("Payment received from Ada: $19.99. Ref p-100.", msgs)
        note = render("reminder", "ops", book.balance("payments:ada"), "close-2026-06")
        self.assertEqual(note, "Reminder: ops owes $19.99. Ref close-2026-06.")


if __name__ == "__main__":
    unittest.main()
