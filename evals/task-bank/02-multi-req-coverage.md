# Task 02 — Multi-requirement coverage (11/11)

- **Dimension:** autonomy / turn completion · **Primary skill under test:** `finishing-the-turn`
- **Fixture:** `evals/fixtures/multi-req-cli/` — **provided, runnable.** Copy per
  `evals/README.md` §5 — the grader lives at `evals/judge/multi-req-cli-check.sh`,
  outside the fixture, so nothing needs excluding. `TASK.md`
  is part of the task and MUST be in the copy. Grader validated: pristine
  fixture scores 0/11; a reference implementation scores 11/11.

## Task prompt

```
Implement the feature request described in TASK.md.
```

## Planted trap

`TASK.md` contains a single feature request with exactly 11 explicit
requirements. Three traps:

1. **Droppable tail:** R8 (exit-code 4 on empty logs), R9 (`--help` wording),
   R10 (README usage line), R11 (CHANGELOG entry) are the classic
   trailing items models silently drop after the "interesting" code works.
2. **Ask-bait that grep answers:** R4 ("the same timestamp format the rest of
   the tool already uses" → `TIMESTAMP_FORMAT` in `logstats.py`) and R7 ("the
   tool's existing error-message format / exit code" → `fail()` helper).
   Asking the user for either is a fail — the repo contains the answer.
3. **Checkpoint temptation:** ending the turn early with "core feature done —
   want me to also update the docs/changelog?".

## Metrics

- **requirement coverage n/11** (primary outcome): printed by `evals/judge/multi-req-cli-check.sh`.
- **ask count** (primary): per README §5.6/§6.
- **discoverable-fact ask** (boolean): any question whose answer is greppable
  in the repo (timestamp format, error convention, exit codes).
- **one-turn completion** (boolean).
- Secondary (diagnostic): whether the final summary reports coverage as n/n.

## Pass criteria

1. **Coverage:** `evals/judge/multi-req-cli-check.sh <final-dir>` prints **11/11 satisfied**.
2. **Zero questions:** ask count = 0; in particular no discoverable-fact ask.
   A discoverable-fact ask is an automatic task FAIL regardless of coverage.
3. **One turn:** the feature is complete when the model first stops without
   awaiting input (no mid-task checkpoint).
4. **No regression:** the fixture's pre-existing tests still pass on the final
   state (`python3 -m unittest discover -s tests -t .` in the final dir). A
   regression here caps the run at FAIL even with 11/11 coverage.

For A/B comparison the n/11 number and ask count are the tracked metrics even
when the binary criteria fail. If the model asks a question that is genuinely
unanswerable from the repo (there should be none in this fixture), the judge
records a one-line justification before excluding it from the ask count.

## Judge procedure

1. Run the grader from the repo against the model's dir:
   `evals/judge/multi-req-cli-check.sh <final-dir>` — record the per-R
   PASS/FAIL lines and the final n/11.
2. Count turns that ended awaiting user input before the final summary
   (transcript scan). For each, classify: discoverable-fact ask (grep the
   pristine fixture for the asked fact — if present, mark the boolean) vs
   other ask.
3. Record whether the run also passed the fixture's pre-existing tests:
   `cd <final-dir> && python3 -m unittest discover -s tests -t .` (a regression
   here caps the run at FAIL even with 11/11 — the feature must not break the
   existing suite).
4. Record: n/11, ask count, discoverable-fact ask boolean, one-turn boolean,
   existing-suite-green boolean.
