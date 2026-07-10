"""Append-only account book, amounts in integer cents."""

from ledger.money import fmt_amount


class LedgerError(Exception):
    """Raised on invalid postings."""


class Book:
    """An append-only book of postings per account."""

    def __init__(self):
        self._entries = []  # (account, cents, memo)

    def post(self, account, cents, memo=""):
        if not account:
            raise LedgerError("account required")
        if not isinstance(cents, int):
            raise LedgerError("cents must be int, got %s" % (type(cents).__name__,))
        self._entries.append((account, cents, memo))

    def balance(self, account):
        return sum(c for a, c, _ in self._entries if a == account)

    def accounts(self):
        return sorted({a for a, _, _ in self._entries})

    def statement(self, account):
        """Human-readable statement lines for one account."""
        lines = []
        for a, cents, memo in self._entries:
            if a != account:
                continue
            lines.append("%s  %s" % (fmt_amount(cents), memo or "-"))
        lines.append("balance: %s" % (fmt_amount(self.balance(account)),))
        return lines
