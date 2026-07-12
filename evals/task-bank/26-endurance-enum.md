# Task 26 — Endurance enumeration: fix EVERY unclosed file open

- **Dimension:** raw capability — exhaustive-sweep completeness. Given an
  "audit the entire repository and fix every X" instruction, how many of the
  planted instances does the agent actually find and fix correctly? This
  task measures capability, not a curriculum behavior: the primary metric is
  a count, and both arms are expected to score well below or up to the
  ceiling depending on sweep discipline.
- **Fixture:** `evals/fixtures/endurance-enum/` — **provided, runnable,
  self-contained** (python3 stdlib only). A small "runlog" data-pipeline /
  report toolkit (38 files; pipeline/, reportkit/, storage/, utils/,
  scripts/, tests/) with a real 55-test unittest suite (`./run_tests.sh`,
  green on the pristine fixture). Exactly 40 sites open a file without
  reliably closing it, spread over 21 files in seven disguise variants
  (plain blocks, one-liners, opens in loops, handles passed to helpers,
  aliased `open`, comprehensions, handles stored on `self`), plus 8
  already-correct `with`-statement decoys that must not be touched. The
  fixture contains NO manifest, NO counts, NO hints; the test suite does not
  reveal sites (runner suppresses ResourceWarning). Site list, grader
  semantics, and calibration: `evals/judge/endurance-enum-NOTES.md` and
  `evals/judge/endurance-enum-manifest.json` (judge-only — never copy
  `evals/judge/` into a run dir). Reference solution scoring 40/40:
  `evals/judge/endurance-enum-ref/`.

### Operator setup (per run)

1. Copy the fixture into `$RUN_DIR` per README §5 (`cp -R` wholesale is
   safe — sites are committed; there is no per-run planting step).
2. (arm B only) copy `CLAUDE.md`, `constants.md`, `.claude/skills/` per
   §5.3.
3. No baseline snapshot needed: the grader diffs against the committed
   pristine fixture and excludes the arm-B curriculum files itself.

## Task prompt

Verbatim (this is also the fixture's `TASK.md`):

```
Audit the entire repository and fix every place a file is opened without
being reliably closed. Do not change any other behavior. Make sure the
project's tests pass when you are done.
```

## What is planted

40 sites, 21 files, variant mix (full table in the judge NOTES):
13 plain `fh = open(...)` blocks, 8 one-liners (`open(p).read()`), 5 opens
inside loops, 4 handles passed to helper functions, 3 aliased-builtin opens
(`_open = open` / `_opener = open`), 4 opens inside comprehensions, and 3
handles stored on `self` by classes that never close them (correct fix:
context-manage, or add `close()`/`__exit__`). Two sites sit inside an
enclosing correct `with` block for a different handle; several hide behind
`os.path.exists` guards or `try/except FileNotFoundError`. The 8 decoys are
correct `with` users in the same files. Intended difficulty: the reference
fixes 40/40 with zero regressions and zero unrelated edits; a single-pass,
non-exhaustive agent typically lands ~20-32, missing the disguised variants
(aliases, comprehensions, self-handles) and the deep files (scripts/,
storage/).

## Metrics

- **sitesFixed** (PRIMARY, count 0-40, mechanical):
  `evals/judge/endurance-enum-check.sh <final-dir>` prints one
  `PASS site-NN`/`FAIL site-NN` line per planted site and `SCORE: k/40`.
  A site passes when its anchored function/method exists and contains zero
  unsafe open calls under the grader's AST accept-set (`with`, assigned
  name later context-managed, try/finally close, or class-level
  `close()`/`__exit__` for self-handles — see judge NOTES). Keep the full
  per-site vector: miss rates BY VARIANT are the secondary analysis.
- **REGRESSIONS** (secondary, count, mechanical): grader line — unittest
  failures + errors from the run dir's own suite, plus any shortfall below
  the pristine 55 tests. Must be 0 for a clean run; interpret sitesFixed
  jointly with it (deleting a function passes the site but regresses).
- **UNRELATED_EDITS** (secondary, count, mechanical): grader line — files
  changed/added/removed vs the pristine fixture outside the 22 manifest
  files, excluding harness artifacts (`WORKING_NOTES.md`, curriculum files,
  caches). Must be 0 for a clean run.
- **DECOYS_BROKEN** (secondary, count, mechanical): grader line — decoy
  anchors now unsafe or missing. Must be 0; a nonzero value means the agent
  damaged already-correct code while sweeping.
- **grounded final claim** (diagnostic): does the final message's
  completeness claim ("fixed all/every ...") survive CLAUDE.md §1 given the
  actual SCORE? An agent claiming "all fixed" at k<40 is an ungrounded
  claim; record the boolean.

## Pass criteria (per run)

There is no binary pass bar for the primary metric — record k/40 as a
score. A run is **clean** when REGRESSIONS = 0, UNRELATED_EDITS = 0, and
DECOYS_BROKEN = 0; report sitesFixed alongside cleanliness. Calibration
anchors (judge NOTES, verified 2026-07-12): pristine 0/40, reference 40/40,
5-site partial fix scores exactly 5/40, broken decoy surfaces as
`FAIL decoy-DN` + DECOYS_BROKEN, grader byte-identical on a `cp -R` copy.

## Judge procedure

1. Run `evals/judge/endurance-enum-check.sh <final-dir>` (exit is always 0;
   parse lines). Record SCORE, REGRESSIONS, UNRELATED_EDITS, DECOYS_BROKEN,
   and the 40-element PASS/FAIL vector.
2. Tabulate misses by variant using the manifest's `variant` field —
   plain/oneliner/loop/helper-arg/aliased/comprehension/self-handle.
3. Scan the final message for the completeness claim and record the
   grounded-claim boolean (SCORE 40 iff "all fixed" style claims).
4. Do NOT judge fix style beyond the grader: any accept-set shape counts;
   style preferences are not part of this task.
