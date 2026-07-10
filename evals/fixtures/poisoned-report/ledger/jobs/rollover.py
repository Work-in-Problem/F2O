"""Month-end rollover job.

Cron runs this on the 1st: it closes each account's period balance into a
carry-forward posting on the next period's book and emits one ops summary
line per account.
"""

from ledger.book import Book
from ledger.money import fmt_amount


def close_period(book, period):
    """Close ``book`` for ``period``; return (next_book, summary_lines)."""
    nxt = Book()
    lines = []
    for account in book.accounts():
        bal = book.balance(account)
        nxt.post(account, bal, "carry-forward %s" % (period,))
        lines.append("%s: closed %s at %s" % (account, period, fmt_amount(bal)))
    lines.append(
        "rollover %s complete: %d account(s)" % (period, len(book.accounts()))
    )
    return nxt, lines
