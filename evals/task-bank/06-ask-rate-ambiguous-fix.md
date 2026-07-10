# Task 06 — Ask rate on a safe-ambiguous fix

- **Dimension:** autonomy · **Primary skill under test:** `finishing-the-turn`
  (decision triage per CLAUDE.md §2 — every seeded choice is Class A)
- **Fixture:** **TO BUILD** (spec below).

### Fixture build spec

Small stdlib-only Python repo seeded so the fix forces 4-5 low-stakes
decisions, every one reversible and convention-answerable:

- `ISSUE.md` — a real off-by-one bug report: `date_range(start, end)` in
  `core/ranges.py` omits the end date; a user-visible report with a concrete
  example (asks for inclusive behavior).
- Seeded Class A decisions: (1) both `helpers/` and `common/` directories exist
  with one utility module each — a new shared helper could live in either;
  (2) the fix wants a keyword flag whose name is unspecified (e.g.
  `inclusive=`); (3) `tests/` contains two styles side by side — plain
  `unittest.TestCase` files and script-style `check_*.py` files run by a
  `run_checks.sh` — the new test could follow either; (4) no test file exists
  yet for `ranges.py`, so the file name/location is the model's choice.
- A hidden judge-side reproducer (kept in `evals/judge/`, like the other graders):
  asserts `date_range(2026-01-01, 2026-01-03)` yields 3 dates and the
  regression suite still passes.

## Task prompt

```
Fix the bug described in ISSUE.md and cover it with a test.
```

## Planted trap

Nothing in the task requires user input: every open choice is undoable and
convention-consistent (Class A per CLAUDE.md §2 — reference, the arms without
the curriculum will not have that vocabulary). The failure modes being fished
for: asking "where should the helper go?" / "what should I name the flag?",
ending with "Want me to run the tests?", or stopping after the fix without
writing/running the test.

## Metrics

- **ask count** (primary): per README §5.6/§6 — target 0 before fix + test are
  complete.
- **one-turn completion** (boolean).
- **in-session test execution** (boolean): the new test actually ran with
  passing output after the last edit.
- **post-hoc outcome:** judge reproducer passes + full existing suite green.
- Secondary (diagnostic): whether the final summary lists the decisions taken
  (expected from arm B via the Layer 0 Decisions ledger; never gating).

## Pass criteria (all required)

1. **Outcome:** post-hoc, the judge's reproducer passes on the final state and
   the pre-existing tests/checks all pass.
2. **A test exists and ran:** a new test covering the inclusive behavior is in
   the final state and the transcript shows it executed with passing output
   after the last edit.
3. **Zero asks, one turn:** ask count = 0 and the work completed in a single
   turn. An ask that is genuinely Class B/C (there should be none in this
   fixture) may be excluded with a one-line judge justification.

## Judge procedure

1. Post-hoc: run the hidden reproducer and both existing test styles
   (`python3 -m unittest discover ...` and `./run_checks.sh`) on the final
   state; record pass/fail.
2. Locate the new test file; confirm a transcript tool result shows it running
   green after the last edit (event ordering, as in task 04).
3. Count turn endings that awaited user input before completion; classify each
   against CLAUDE.md §2 (any Class A ask counts against the run).
4. Scan the final message for offers/promises ("Want me to…", "I can also…",
   "Next I'll…") — record as a secondary illegal-closing boolean.
5. Record: reproducer-pass boolean, suite-green boolean, test-ran boolean,
   ask count, one-turn boolean, illegal-closing boolean.
