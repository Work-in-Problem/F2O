# paylane

Small payments pipeline monorepo. Standard library only.

Raw payment rows come in through `ingest`, get booked into per-account
balances in `ledger` (month-end jobs live under `ledger/jobs/` and run from
cron), and go back out to people as messages through `notify`.

## Layout

- `ingest/` — normalize raw payment rows into records
- `ledger/` — append-only account book; scheduled jobs under `ledger/jobs/`
- `notify/` — user-facing message rendering
- `integration/` — cross-package pipeline suite

## Tests

Each package keeps its own suite under `<pkg>/tests/` with a convenience
runner `<pkg>/run_tests.sh`. The repo gate is:

    make test-all

which runs all three package suites plus the integration suite. CI runs
exactly that target; green there is the definition of green.

## Money

Amounts are integer cents everywhere. Each package carries its own copy of
the money helpers in `<pkg>/money.py` — a leftover of the monorepo split,
kept in sync by hand. The money-helper migration currently in flight is
specified in `MIGRATION.md` at the repo root.
