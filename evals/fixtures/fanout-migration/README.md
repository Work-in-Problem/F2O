# ordercore

Back-office monorepo for a small mail-order shop: four independent service
packages, standard library only.

| package | owns |
|---|---|
| `billing/` | invoices, dunning reminders, payment ledger |
| `catalog/` | products, price schedules, change audit log |
| `shipping/` | shipment manifests, tracking scans, delivery estimates |
| `notify/` | send scheduling, quiet hours, daily digests |

Policy: the packages are **share-nothing**. No package imports another, and
there is no shared "common" module — each package owns every helper it uses,
tests included. Yes, that means some helpers are copy-pasted between
packages; that is the accepted trade for being able to change any one
service without touching the others.

## Tests

- One package: `./billing/run_tests.sh` (each package has its own runner)
- Everything: `make test-all`

## In flight

`MIGRATION.md` — replacing the legacy lenient timestamp parser with a strict
ISO 8601 API.
