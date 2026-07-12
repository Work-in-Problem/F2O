# Task 25 — Hidden edges (spec-depth, raw capability)

- **Dimension:** RAW CAPABILITY — first-shot correctness depth: does the
  agent implement the whole spec, or only the part the visible tests
  exercise? · **Primary skill under test:** none in particular — this task
  is a capability baseline, not a process probe (`planning-to-done` spec
  extraction and `verifying-before-claiming` self-testing plausibly help,
  but the metric is outcome-only).
- **Fixture:** `evals/fixtures/hidden-edges/` — **provided, runnable,
  calibrated** (reference 30/30, naive visible-tests-only baseline 12/30,
  pristine 0/30; see `evals/judge/hidden-edges-NOTES.md`). Copy per
  `evals/README.md` §5 — the fixture dir contains no spoilers; `SPEC.md`,
  `README.md`, and `tests/` are part of the task and MUST be in the copy.
  The grader and the hidden test battery live in `evals/judge/` and must
  NEVER be copied into a run dir — the fixture must not mention or hint at
  their existence, and it doesn't.

## Task prompt

```
The project is in the current directory. Implement cardparse.py per SPEC.md
so it handles the format robustly and completely. Make sure the project's
tests pass when you are done.
```

## Design

`SPEC.md` is a precise, complete, ~2.5-page English spec for "VCF-lite":
BEGIN/END card blocks, `key:value` lines, line folding, escape sequences
(`\\`, `\n`, `\;`, `\:`), case-insensitive keys stored lowercase,
`;`-separated multi-value fields, an exact duplicate-key policy (append),
LF/CRLF (and lone-CR-as-content) handling, blank-line rules, verbatim
Unicode, a fully enumerated error model (`CardParseError`, message format
`line N: <reason>`), and ordering guarantees. The fixture ships 8 visible
happy-path tests (`./run_tests.sh`). The hidden battery is 30 cases probing
spec corners the visible tests never touch — folding+escaping interaction,
CRLF/lone-CR, duplicate keys, escaped separators, marker edge spellings,
boundary inputs (empty card, empty value, fold at EOF), and the exact error
messages/line numbers.

**Fairness rule (audited):** every hidden case's expected behavior is
unambiguously derivable from `SPEC.md` alone; the NOTES file cites the
deciding SPEC.md sentence per case. There are no gotchas the spec doesn't
settle, no misleading material, and no requirement conflict — depth of spec
reading and implementation is the only variable.

**Calibration:** the reference implementation scores 30/30; a deliberately
naive implementation that passes all 8 visible tests scores 12/30. Expected
spread for evaluated agents: a shallow "make the tests green" run lands
roughly 10–18/30; a spec-complete run approaches 30/30.

## Metrics

- **hiddenPass n/30** (PRIMARY): `bash evals/judge/hidden-edges-check.sh
  <run-dir>` — one PASS/FAIL line per hidden case, final `SCORE: n/30`
  (mechanical, exit 0 always; score line is the result). Ratio metric — no
  binary threshold; compare distributions across arms.
- **visibleTests** (secondary boolean): the fixture's own `./run_tests.sh`
  green on the final state (8 tests, 0 failures). A run that fails its own
  visible tests is broken regardless of hiddenPass.
- **fixtureIntact** (validity gate): `diff -ru` vs pristine fixture —
  `SPEC.md`, `README.md`, `run_tests.sh`, `tests/` unmodified. Weakening the
  visible tests or editing the spec voids the run. The agent adding its OWN
  new test files is fine and expected of a thorough run.
- **ask count** / **one-turn completion** per README §§5.6, 6 — the task is
  fully specified; expected ask count is 0.
- **grounded-claim rate** of the final message (README §6): the agent cannot
  see the battery, so any specific "verified" behavior claim must trace to
  its own visible evidence (its added tests / commands).

## Judge procedure

1. Copy the final state of the run dir to a scratch location.
2. `bash evals/judge/hidden-edges-check.sh <copy>` → record `SCORE: n/30`
   and the per-case PASS/FAIL lines verbatim.
3. `./run_tests.sh` in the copy → visibleTests boolean.
4. `diff -ru <pristine-fixture> <copy>` → fixtureIntact; list agent-added
   files (diagnostic: did it write its own edge-case tests?).
5. Ask scan and grounded-claim audit per README §§5.6, 6.
6. Record: hiddenPass n/30, visibleTests, fixtureIntact, ask count, one-turn
   boolean, grounded-claim rate, agent-added-tests count (diagnostic).
   hiddenPass is a 0–30 count, not binary — per `constants.md` C9 report
   mean + min–max spread per arm (C9's binary-exact-test note does not
   apply to this metric).
