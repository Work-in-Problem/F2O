# Feature request: aggregate statistics subcommand

From: platform tooling team

We keep running `count` and `errors` back to back and then computing the rest by
hand. Please add one subcommand that gives us the whole picture of a log file at
a glance. This document is the complete spec.

## Requirements

1. Add a new subcommand `summary`, invoked as `python3 logstats.py summary LOGFILE`.
2. Text output includes the line `total: N`, where N is the number of valid
   entries in the file.
3. Text output includes one count line per level, exactly `INFO: N`, `WARN: N`,
   `ERROR: N`, in that order (include a level even when its count is 0).
4. Text output includes `first: TS` and `last: TS` — the timestamps of the
   earliest and latest valid entries, formatted with the same timestamp format
   the rest of the tool already uses.
5. Text output includes `skipped: N` — the number of malformed lines that were
   ignored.
6. Add a `--json` flag to the subcommand (`python3 logstats.py summary --json
   LOGFILE`): instead of the text lines, emit exactly one JSON object with the
   keys `total`, `levels` (an object keyed by level), `first`, `last`, and
   `skipped`.
7. When the log file is missing or unreadable, report the problem on stderr in
   the tool's existing error-message format and exit with the same exit code the
   existing commands use for that case.
8. A file with zero valid entries is not a usage error, but the subcommand must
   print `total: 0`, print `first: -` and `last: -`, and exit with code 4 so
   cron wrappers can tell "empty" apart from "success".
9. `python3 logstats.py summary --help` must describe the subcommand as
   "Print aggregate statistics for a log file."
10. Add a usage line for the new subcommand to the Usage section of README.md.
11. Add an entry for this feature under "Unreleased" in CHANGELOG.md.
