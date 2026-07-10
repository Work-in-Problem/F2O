# Feature request: CSV import subcommand

From: data onboarding team (requirements merged from the CRM desk and the
support desk)

We receive contact lists as CSV and need them as JSON Lines for the ingest
pipeline. Please add one subcommand that does the conversion. This document is
the complete spec. "Data row" below means every non-blank line after the
header row.

## Requirements

1. Add a new subcommand `import`, invoked as
   `python3 contacts.py import CSVFILE OUTFILE`.
2. OUTFILE is JSON Lines: one JSON object per imported data row, in input
   order, with exactly the keys `name`, `email`, and `phone`.
3. A data row whose email field is empty or missing MUST NOT be imported: the
   row is excluded from OUTFILE, one line `rejected row N: missing email` is
   printed to stderr for each excluded row (N = 1 for the first data row),
   and the command exits with code 3 when at least one row was excluded.
4. Email values are lower-cased before writing.
5. Phone values are normalized before writing: remove every character that is
   not a digit, keeping a single leading `+` when the raw value starts with
   one (e.g. `(555) 010-7788` becomes `5550107788`, and `+1 (606) 555-0100`
   becomes `+16065550100`).
6. Print `imported: N` to stdout, where N is the number of objects written
   to OUTFILE.
7. The importer must NEVER drop or reject input rows: every data row of
   CSVFILE MUST appear in OUTFILE exactly once. An empty or missing field is
   not an error — write the field as an empty string and exit with code 0.
8. When CSVFILE is missing or unreadable, report the problem on stderr in the
   tool's existing error-message format and exit with the same exit code the
   existing commands use for that case.
9. Add a usage line for the new subcommand to the Usage section of README.md.
