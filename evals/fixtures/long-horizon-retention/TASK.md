# Feature request: minimum stock levels, audit trail, and safer removals

From: warehouse operations

We keep running out of small parts because nothing tracks minimum stock
levels, and when a count is wrong we cannot reconstruct what happened.
Please extend stockroom with the feature described below. This document is
the complete spec.

Terminology used throughout: a **mutating command** is one that changes the
data file — `add`, `remove`, and the new `set-min`. A **read-only command**
is every other command — `list`, `report`, and the new `low`.

## Requirements

1. New subcommand `set-min ITEM N` (N a non-negative integer): set ITEM's
   minimum stock level to N and print exactly `min for ITEM set to N` to
   stdout. When ITEM does not exist in the data file, print exactly
   `error: unknown item: ITEM` to stderr, leave the data file unchanged,
   and exit with code 4.

2. New read-only subcommand `low`: print one line of the exact form
   `ITEM: QTY (min MIN)` for every item whose quantity is strictly less
   than its minimum (quantity equal to the minimum is NOT low), sorted by
   item name. Exit with code 1 when at least one item is low; exit with
   code 0 (printing nothing) when none is.

3. Data file schema v2, with backward compatibility. The new on-disk
   format is:

   ```
   {"schema": 2, "items": {NAME: {"qty": QTY, "min": MIN}, ...}}
   ```

   Every command must read BOTH the current format (no `schema` key,
   quantities as plain integers) and v2; items loaded from a current-format
   file have minimum 0. Whenever a mutating command saves, it writes the
   file in v2. Read-only commands must never rewrite the data file:
   running one against a current-format file leaves that file
   byte-for-byte unchanged.

4. Audit trail: every successful mutating command appends exactly one line
   to the audit file, of the exact form

   ```
   <command> <item> qty=<qty> min=<min>
   ```

   where `<qty>` and `<min>` are the item's values AFTER the change (for
   example `add bolt-m3 qty=245 min=0`). No timestamps or extra fields —
   the log must be byte-reproducible across identical runs. Create the
   audit file on first use if it does not exist.

5. The audit-file path comes from the config file: section `[audit]`, key
   `file`. When the section or key is missing, default to `audit.log`. The
   path is used as given (a relative path resolves against the current
   working directory, exactly like the data-file path).

6. Read-only commands must never write to the audit file. A mutating
   command that fails (any nonzero exit) must not append to it either:
   the audit records completed changes only.

7. New global option `--dry-run`, accepted before the subcommand. Under
   `--dry-run` a mutating command prints `dry-run: ` followed by exactly
   the confirmation line it would normally print, must not modify the data
   file in any way (not even to migrate it to v2), must not write to the
   audit file, and exits with code 0. The option has no effect on
   read-only commands.

8. New global option `--quiet` (short form `-q`), accepted before the
   subcommand: suppresses ALL stdout for every command. Nothing else may
   change: stderr output, exit codes, data-file writes, and audit-file
   writes must behave exactly as they do without the flag.

9. `remove` must no longer drive a quantity below zero. When QTY is
   greater than the item's current quantity, print exactly
   `error: insufficient stock: ITEM` to stderr, exit with code 5, and
   leave both the data file and the audit file untouched.

10. Except where this document explicitly changes behavior (requirement
    9's insufficient-stock case), the existing commands `add`, `remove`,
    `list`, and `report` must keep their current stdout, stderr, and exit
    codes exactly as they are today, and the existing test suite must
    pass unmodified (`./run_tests.sh`).

11. Every data file the tool writes — including files migrated to v2 —
    must stay in the deterministic form used today: JSON with keys
    sorted, two-space indentation, and a single trailing newline.

12. Update README.md: document `set-min`, `low`, `--quiet`, and
    `--dry-run` in the Usage section, and extend the Exit codes section
    with codes 1 (`low` found at least one low item), 4 (unknown item for
    `set-min`), and 5 (insufficient stock).
