# MIGRATION — fmt_amount(cents) → format_amount(cents, currency)

Status: the new helper has shipped in every package's `money.py`; call
sites are not migrated yet. The deprecation window closes this quarter.

## Why

`fmt_amount(cents)` hardcodes USD. Multi-currency onboarding needs the
currency explicit at every call site, so the new API is
`format_amount(cents, currency)` with an ISO 4217 code (`"USD"`, `"EUR"`,
...). For `"USD"` the output string is identical to what `fmt_amount`
produces today.

## The change, per package

Every package carries its own copy of the helpers (`ingest/money.py`,
`ledger/money.py`, `notify/money.py`). For each package:

1. Replace every call `fmt_amount(X)` with `format_amount(X, "USD")`.
   All amounts in the system today are USD, so the migration is
   behavior-preserving — output strings do not change, and the existing
   tests must stay green unmodified.
2. Once the package has no `fmt_amount` callers left, DELETE the
   `fmt_amount` definition from that package's `money.py` in the same
   change. Do not leave the dead shim behind: the point of the window is
   that any lingering caller fails loudly at import time instead of
   silently formatting USD forever.
3. Done, for a package, means zero `fmt_amount` references left in it.
   Done, for the repo, means the repo gate `make test-all` is green.

Note: no test edits are expected anywhere — tests never call `fmt_amount`
directly, they assert on strings produced through the public functions,
and those strings are unchanged for USD.
