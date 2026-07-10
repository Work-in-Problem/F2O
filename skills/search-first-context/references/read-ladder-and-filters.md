# Read ladder traces and output-bound recipes

Worked material for SKILL.md rules 13 (purpose-priced reads) and 14 (bounded output).
Every numeric flag below (`tail -n 30`, `-m 5`, `limit=30`) is an illustrative recipe
value sized to keep the decisive block visible — not a threshold; thresholds live in
`constants.md`.

## Part 1 — ladder rung traces (rule 13)

### Rung (c): known-region lookup in a 3,000-line file

Question: "What is the default of `RETRY_LIMIT`?" — one symbol, no edit planned.

BAD trace:
```
Read src/config.py                      # 3,000 lines into context
```
Thousands of tokens; everything except one line is never referenced again this session.

GOOD trace:
```
Grep -n "RETRY_LIMIT" src/config.py     # hit: line 1842
Read src/config.py offset=1835 limit=20
```
Then capture per rule 15 so the question never costs a second read:
`## Findings: src/config.py:1842 RETRY_LIMIT = 5 (overridable via env RETRY_LIMIT)`.

### Rung (b): head-triage of a discovery batch, one deep read at the end

Task: find which of 12 candidate services owns rate limiting, then change it.

BAD trace: full Read of all 12 files (600–1,500 lines each) "to be thorough" —
depth-everywhere during what should be the cheap breadth window (rule 3, C15).

GOOD trace:
```
rg -n -m 3 "rate.?limit" services/*/handler.py   # 4 files hit
Read services/quota/handler.py limit=40           # imports + first declarations
Read services/gateway/handler.py limit=40         # same triage price
```
Two candidates survive triage; one line states why `gateway` is authoritative
(rule 4). ONLY the confirmed edit target then gets the rule 2 pre-edit read at C14's
above-cutoff depth (enclosing class + imports and exports). One deep read, not twelve.
Guard: any file the change will touch is an edit target under rule 13(a) — triage
pricing never applies to it.

### Re-read temptation resolved from captured anchors (rule 15)

Twenty-five calls after reading `src/handlers.py`, you need `dispatch()`'s signature
again. The notes already hold:
`## Findings: src/handlers.py:210 def dispatch(event: Event, *, retry: bool = False) -> Result`
No staleness trigger fired (rule 12, C16) → use the captured anchor, zero re-read.
If a trigger HAS fired (a formatter ran, another agent touched the repo), re-read only
the affected region: `Read src/handlers.py offset=200 limit=30` — never the whole file.

## Part 2 — output-bound recipes (rule 14)

Each recipe keeps the decisive verdict line plus the counts the CLAUDE.md §1 audit
needs (tests run, failures, skips). Verdict lines print LAST for most runners — bound
with `tail`, never `head`.

| Situation | Bounded invocation | Decisive line preserved |
|---|---|---|
| pytest suite | `pytest -q 2>&1 \| tail -n 30` | `N passed, M failed, K skipped in Xs` (also shows `no tests ran`) |
| pytest, one failure found | `pytest path/test_x.py::test_name -x -vv` | full verbose for the single unit only |
| jest suite | `npx jest --silent 2>&1 \| tail -n 30` | `Tests: X failed, Y passed, Z total` |
| go test | `go test ./... 2>&1 \| tail -n 40`; failure → `go test ./pkg -run 'TestName' -v` | per-package `ok`/`FAIL` lines cluster at end |
| cargo test | `cargo test --quiet 2>&1 \| tail -n 40` | `test result: ok. N passed; M failed` |
| build | `npm run build 2>&1 \| tail -n 30` / `make 2>&1 \| tail -n 40` | error block + exit summary print last |
| install | `npm install --no-audit --no-fund 2>&1 \| tail -n 15`; `pip install -q -r requirements.txt 2>&1 \| tail -n 15` | resolution errors and the final summary |
| git history | `git log -n 20 --oneline -- <path>`; `git log --follow -p -- <file>` only for the rule 8 fence check on named lines | bounded by -n and path |
| git diff | `git diff --stat` first; then `git diff -- <one-path>` per file of interest | per-file churn counts, then one file's hunks |
| search | `rg -l <pat>` to list files; `rg -n -m 5 <pat> <file>` to cap per-file hits; `rg -n -C 3` instead of opening the file | hit lines with anchors |
| find / ls -R | `find src -name '*.test.ts' -maxdepth 3 \| head -n 50` AND `... \| wc -l` | first page PLUS the true count — never a silently truncated list |

The single-failing-unit rows are rule 14's escalation path: bounded full run first;
on unexpected failure, verbose on the one failing unit — never the whole suite verbose.

## Part 3 — invalid bounds (filters that hide trap signals)

A bound is valid iff the filtered output ALONE still lets you fill the §1 buckets
truthfully. These do not:

- `pytest 2>&1 | grep -c PASSED` — hides `no tests ran` / "0 collected" (§1: a
  failure) and the failure count entirely.
- `npm test 2>/dev/null | tail -n 5` — discards stderr, where runners print the
  failure summary and stack traces.
- `pytest | head -n 20` — pytest's verdict prints last; head keeps warm-up noise and
  cuts the verdict.
- Any quiet flag that suppresses the skip count when the claim depends on "no skips"
  (§1: partial-green with skips is not green).

Each of these can blind you to a passing-looking failure from
`verifying-before-claiming` rule 6's trap catalog (its `references/output-traps.md`) —
that catalog owns the trap list; when it grows, the preserved-signal set here grows
with it.
