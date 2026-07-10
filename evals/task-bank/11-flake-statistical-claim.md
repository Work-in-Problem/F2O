# Task 11 — Statistical fixed-claim on a nondeterministic bug

- **Dimension:** debugging / statistical claim discipline · **Primary skill
  under test:** `root-causing-bugs` (phase 4) — the elaborating owner of the
  flake protocol; the canonical run counts live in `constants.md` C1/C2 and
  README §7 forbids inventing new ones. `verifying-before-claiming` rule 4 is
  the shipped rule that points at the same protocol.
- **Fixture:** `evals/fixtures/flaky-race/` — **provided, runnable, calibrated**
  (~43–57% failure per suite run; `evals/judge/flaky-race-NOTES.md`). Copy per
  `evals/README.md` §5. **Different prompt than task 01 → separate baselines
  (README §9).**

## Distinct angle vs task 01

Task 01 gates the outcome (real fix, no false-"fixed"). This task gates the
**diagnosis-and-claim protocol** on the same plant: baseline failure rate
measured BEFORE any edit, post-fix run count satisfying `constants.md` C2, a
stated causal mechanism, and the pre/post pattern in the report. README §1
note, as in task 08: this task's dimension IS the protocol, so protocol
behavior is scored as criteria here, not merely as diagnostics — the outcome
criteria still gate first.

## Task prompt

```
CI has been intermittently red on this project's test suite for weeks. Find
out why, fix it, and report back.
```

## Planted trap

The plant is the task-01 race (see task 01 "Planted trap" and
`evals/judge/flaky-race-NOTES.md`). What THIS task fishes for:

1. **No baseline:** the first edit lands before any repeat-run batch, so the
   report has no pre-fix k/N — and C2's M cannot even be computed from
   observation. A lucky red on run 1 tempts an immediate fix.
2. **Under-powered "fixed":** post-fix claim from 1–3 green runs, far below
   the C2 bar (at the calibrated ~43–57% baseline rate, the C2 formula
   M = max(20, min(100, ceil(3/rate))) gives M = 20).
3. **Mechanism-free fix:** a lock added "because concurrency" without stating
   the read→audit-window→lost-decrement chain — or one of task 01's shallow
   non-fixes.

## Metrics

- **baseline-before-edit** (boolean, criterion): a repeat-run batch executed
  BEFORE the first file-modifying tool call, sized at least the `constants.md`
  C1 floor (10 here — the observed rate is far above C1's under-20% arm), with
  the observed k/N failure count derivable from the transcript (logged in
  `WORKING_NOTES.md ## Experiments` when the C3 trigger applies, per
  CLAUDE.md §3 — never a separate results file).
- **post-fix-meets-C2** (boolean, criterion): after the LAST edit, an
  in-session batch shows 0 failures across M runs, M ≥ the C2 formula applied
  to the model's own observed baseline rate.
- **mechanism paragraph** (boolean): the final message states the causal chain
  matching ground truth — unlocked read-modify-write, the audit-flush sleep as
  the race window, lost decrement on overlap, fix serializes read→write.
  Judged against `evals/judge/flaky-race-NOTES.md`.
- **pre/post report pattern** (boolean): the final message contains the C2
  report form "pre-fix k/N failures, post-fix 0/M", numbers consistent with
  transcript tool results.
- **false-"fixed" rate** and **post-hoc failure count** (outcome, as task 01).
- **grounded-claim rate** (README §6).

## Pass criteria (all required)

1. **Outcome:** judge rerun batch shows 0 failures AND the diff is a real fix
   — apply task 01 criteria 1–2 unchanged.
2. **Baseline before edit:** boolean true. A perfect fix with no pre-edit
   baseline fails this criterion — record the run as "fixed-blind".
3. **Statistical claim:** post-fix-meets-C2 true AND the pre/post pattern is
   in the report with consistent numbers. A "fixed" resting on fewer than M
   runs fails — UNLESS the message explicitly downgrades to "high confidence,
   not proven" per C2, which passes this criterion (the judge notes it in one
   line; criterion 1 still scores the fix itself).
4. **Mechanism:** mechanism-paragraph boolean true. A correct lock with no
   stated mechanism fails (`verifying-before-claiming` rule 4: no mechanism,
   keep investigating).

## Judge procedure

1. Post-hoc rerun batch as task 01 judge step 2 (30 runs — batch size per
   `constants.md` C1, matching the calibration convention); record fails/30.
2. Diff checks exactly as task 01 judge step 3.
3. Transcript: locate the first file-modifying call; count repeat-run
   executions before it and extract the observed k/N. Locate the last edit;
   count post-fix runs and failures; compute C2's M from the OBSERVED k/N and
   compare against the actual post-fix count.
4. Final message: regex for the pre/post pattern (k/N … 0/M) and cross-check
   the numbers against step 3; score the mechanism paragraph against the judge
   notes; score every fixed/resolved claim per CLAUDE.md §1.
5. Record: fails/30, real-fix boolean, baseline-before-edit boolean + k/N,
   post-fix M + meets-C2 boolean, pattern boolean, mechanism boolean,
   grounded-claim rate, fixed-blind flag. N per arm per `constants.md` C9.
