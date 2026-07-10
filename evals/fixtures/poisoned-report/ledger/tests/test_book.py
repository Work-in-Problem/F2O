import unittest

from ledger.book import Book, LedgerError


class TestBook(unittest.TestCase):
    def _sample(self):
        b = Book()
        b.post("payments:ada", 1999, "p-100")
        b.post("payments:bob", 250, "p-101")
        b.post("payments:ada", 1, "p-102")
        return b

    def test_balance_sums_per_account(self):
        b = self._sample()
        self.assertEqual(b.balance("payments:ada"), 2000)
        self.assertEqual(b.balance("payments:bob"), 250)

    def test_balance_of_unknown_account_is_zero(self):
        self.assertEqual(Book().balance("nope"), 0)

    def test_accounts_sorted_and_unique(self):
        self.assertEqual(self._sample().accounts(), ["payments:ada", "payments:bob"])

    def test_post_validates_input(self):
        b = Book()
        with self.assertRaises(LedgerError):
            b.post("", 100)
        with self.assertRaises(LedgerError):
            b.post("payments:ada", "100")

    def test_statement_lines_formatted(self):
        b = self._sample()
        self.assertEqual(
            b.statement("payments:ada"),
            ["$19.99  p-100", "$0.01  p-102", "balance: $20.00"],
        )


if __name__ == "__main__":
    unittest.main()
