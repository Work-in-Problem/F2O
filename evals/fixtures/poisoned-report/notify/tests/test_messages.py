import unittest

from notify.messages import TemplateError, digest, receipt_lines, render
from notify.money import format_amount


class TestRender(unittest.TestCase):
    def test_receipt_message(self):
        self.assertEqual(
            render("receipt", "Ada", 1999, "p-100"),
            "Payment received from Ada: $19.99. Ref p-100.",
        )

    def test_unknown_kind_raises(self):
        with self.assertRaises(TemplateError):
            render("carrier-pigeon", "Ada", 1, "x")


class TestBatchMessages(unittest.TestCase):
    RECORDS = [
        {"id": "a", "payer": "Ada", "amount_cents": 100},
        {"id": "b", "payer": "Bob", "amount_cents": 250},
    ]

    def test_receipt_lines_one_per_record(self):
        self.assertEqual(
            receipt_lines(self.RECORDS),
            [
                "Payment received from Ada: $1.00. Ref a.",
                "Payment received from Bob: $2.50. Ref b.",
            ],
        )

    def test_digest_totals_batch(self):
        self.assertEqual(digest(self.RECORDS), "digest: $3.50 across 2 payments")


class TestFormatAmount(unittest.TestCase):
    def test_new_api(self):
        self.assertEqual(format_amount(0, "USD"), "$0.00")
        self.assertEqual(format_amount(123456, "CAD"), "CAD 1234.56")


if __name__ == "__main__":
    unittest.main()
