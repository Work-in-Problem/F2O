# Task 18 — Read-economy piggyback on the task-07 rename

- **Dimension:** context-window economy · **Primary skill under test:**
  `search-first-context` (phase 5, backlog — EXTENSION: the appended
  read-pricing / bounded-output / capture rules. Arm B must include the
  extended skill; earlier arm-B transcripts made with the unextended skill
  count only as baseline-side data, as in task 12.)
- **Fixture:** **none of its own** — piggybacks task 07:
  `evals/fixtures/rename-config/` untouched, prompt verbatim, so existing
  task-07 **arm-A baselines and archived transcripts remain valid per README
  §9** and may be scored retroactively (README §5.7 keeps full transcripts).
  Task-13 runs are NOT reusable here — the wart is a different fixture state.

**Governing rule, stated up front (README §1): outcome gates first.** The
economy comparison is only meaningful between runs that are non-inferior on
task 07's own criteria — cheap-but-wrong reading is a worse failure than
expensive-and-right. Like task 12, this task adds NO run-level pass/fail of
its own; it adds measurements to task-07 runs.

## Task prompt

Identical to task 07, verbatim:

```
Rename the config key "max_retries" to "retry_limit" everywhere it matters in
this project, keeping behavior identical. All project tests must still pass.
```

## Planted structure

Nothing new is planted. Every fixture file sits under the `constants.md` C14
whole-file cutoff, so whole-file first reads are correct and priced-in — the
waste modes live elsewhere:

1. **Re-read tax:** re-Reading a file already in context with no intervening
   edit and no C16 trigger (no formatter or hook exists in this fixture, so
   C16's non-numeric arms never fire here).
2. **Unbounded dumps:** `cat`-ing whole files or dumping full unfiltered
   test output where a ranged Read or filtered run serves. A filtered run is
   only legal when it preserves the CLAUDE.md §1 counts (tests ran > 0,
   failures == 0) — a filter that hides them is a false-green vector, not
   economy.
3. **Duplicate greps:** the identical pattern + scope re-run with no
   intervening edit, instead of captured on first pass.

## Metrics

**Primary outcome (gates): task 07's full metric set, unchanged** — n/7,
decoy boolean, discovered-command boolean, grounded claims, ask count.

Economy metrics (mechanical, from the transcript):

- **duplicate-read count** (target 0): a Read/cat covering content already
  returned this session for that path, EXCLUDING (a) reads after an
  Edit/Write to that file, and (b) a region-scoped re-read immediately
  preceding an edit when ~20+ calls have elapsed since the last read of that
  region — that re-read is mandated by `constants.md` C16, not waste.
- **total fixture-content lines:** sum of fixture-file lines returned across
  all Read / cat / sed / head / tail / grep tool results (for grep, count
  emitted lines). Lines from curriculum files and `WORKING_NOTES.md` are
  recorded separately as a diagnostic — never mixed into this number.
- **duplicate-grep count:** identical pattern + scope re-run, no intervening
  edit.
- **unbounded-dump count** (diagnostic): full-file `cat` / full unfiltered
  suite dumps where a bounded form served.

## Comparison rules (in place of pass criteria)

1. Each run is passed/failed under **task 07's criteria only**.
2. Per README §7, claim an economy win only if BOTH hold: (a) mean n/7 of
   arm B is non-inferior to arm A, and (b) the total-fixture-content-lines
   delta exceeds the wider min–max spread of the two arms. Otherwise report
   "indistinguishable from noise".
3. Duplicate-read / duplicate-grep / unbounded-dump counts are reported per
   arm as supporting evidence, never as a substitute for (2).

## Judge procedure

1. Run task 07's judge procedure completely; keep its full record.
2. Build a read ledger from the transcript: every Read/Bash tool call
   touching a fixture path → (path, range, lines returned, prior coverage of
   that range, intervening edits, calls since last read of that region).
3. Compute duplicate-read count with the two exclusions above,
   duplicate-grep count, total fixture-content lines, unbounded-dump count.
4. Compare arms per README §7 — mean + min–max for BOTH n/7 and the line
   totals; apply comparison rule 2.
5. Record everything alongside the task-07 record; trigger accuracy per
   README §8 for arm B (did the extended rules' skill load). N per arm per
   `constants.md` C9. Retroactive scoring of archived task-07 arm-A
   transcripts is legal (fixture + prompt unchanged, §9); fresh arm-B runs
   require the extended skill.
