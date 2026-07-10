import unittest

from ingest.money import format_amount
from ingest.records import RecordError, batch_summary, parse_batch, parse_row


class TestParseRow(unittest.TestCase):
    def test_happy_row_normalized_with_display(self):
        rec = parse_row({"id": 7, "amount_cents": "1234", "payer": " Ada "})
        self.assertEqual(
            rec,
            {"id": "7", "payer": "Ada", "amount_cents": 1234, "display": "$12.34"},
        )

    def test_missing_field_rejected(self):
        with self.assertRaises(RecordError):
            parse_row({"id": "x", "amount_cents": 100})

    def test_negative_amount_rejected(self):
        with self.assertRaises(RecordError):
            parse_row({"id": "x", "amount_cents": -1, "payer": "Ada"})


class TestBatch(unittest.TestCase):
    def test_batch_preserves_order_and_sums(self):
        recs = parse_batch(
            [
                {"id": "a", "amount_cents": 100, "payer": "Ada"},
                {"id": "b", "amount_cents": 250, "payer": "Bob"},
            ]
        )
        self.assertEqual([r["id"] for r in recs], ["a", "b"])
        self.assertEqual(batch_summary(recs), "2 records, $3.50 total")


class TestFormatAmount(unittest.TestCase):
    def test_usd_uses_symbol(self):
        self.assertEqual(format_amount(1999, "USD"), "$19.99")

    def test_other_currencies_use_iso_prefix(self):
        self.assertEqual(format_amount(1999, "EUR"), "EUR 19.99")
        self.assertEqual(format_amount(-501, "THB"), "-THB 5.01")


if __name__ == "__main__":
    unittest.main()
