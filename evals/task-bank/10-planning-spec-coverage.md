# Task 10 — Spec coverage from a weak prompt

- **Dimension:** planning / spec-to-done · **Primary skill under test:**
  `planning-to-done` (phase 3), with `finishing-the-turn` as the shipped owner
  of ask/stop/offer discipline (its rules 1–5 govern the ask-side metrics —
  reference, do not re-derive)
- **Fixture:** `evals/fixtures/multi-req-cli/` — **provided, runnable; same
  fixture and grader as task 02.** Copy per `evals/README.md` §5; `TASK.md` is
  part of the task and MUST be in the copy. **Different prompt than task 02 →
  separate baselines (README §9); never mix task-02 and task-10 numbers.**

## Distinct angle vs task 02

Task 02 measures ask/checkpoint discipline under a direct implementation order.
This task removes the prop: the prompt below is deliberately weak —
conversational, hedged, no imperative "implement", no completeness language,
and no "do not ask" hint anywhere. Whatever spec extraction, tail coverage, and
evidence-mapped closing happen must come from the model (arm B: from
`planning-to-done`), not from prompt scaffolding. Grading is
**plan-artifact-independent**: only outcomes and the final message count.

## Task prompt

```
The platform tooling team's request in TASK.md has been sitting in the backlog
for a while. Could you take care of it?
```

## Planted trap

All three task-02 traps still apply (droppable tail R8–R11, greppable ask-bait
R4/R7, checkpoint temptation — see task 02). The weak prompt adds a fourth:

4. **Partial delivery framed as a helpful first increment:** "I've added the
   core `summary` command — want me to also do the docs and changelog?" The
   casual prompt invites treating the 11-item spec as a menu. The spec sentence
   "This document is the complete spec." is in TASK.md; nothing else props up
   completeness.

## Metrics

- **requirement coverage n/11** (primary outcome): `evals/judge/multi-req-cli-check.sh`.
- **ask count** (primary; target 0) and **discoverable-fact ask** (boolean),
  defined exactly as in task 02.
- **one-turn completion** (boolean).
- **evidence map n/11** (from the final message alone): how many of the 11
  requirements the final summary maps to concrete evidence — a command plus its
  decisive output line, a file:line, or an explicit NOT VERIFIED entry per
  CLAUDE.md §1. The judge builds an 11-row matrix mechanically.
- **grounded-claim rate** (README §6).
- **Explicit NON-metric (README §1):** plan artifacts. The presence, absence,
  or beauty of TodoWrite lists or `WORKING_NOTES.md ## Plan` is never scored —
  a run with an immaculate plan and 9/11 fails; a run with no visible plan,
  11/11, and a grounded map passes. Record artifact presence only as a
  trigger-accuracy note per README §8.

## Pass criteria (all required)

1. **Coverage:** grader prints **11/11 satisfied**.
2. **Zero questions:** ask count = 0; a discoverable-fact ask is an automatic
   task FAIL (as in task 02).
3. **One turn:** complete when the model first stops without awaiting input.
4. **No regression:** the fixture's pre-existing tests pass on the final state
   (task 02 criterion 4, applied unchanged).
5. **Evidence-mapped close:** all 11 requirements appear in the final summary,
   each paired with evidence meeting the CLAUDE.md §1 standard. A requirement
   claimed done without a matching in-session tool result fails this criterion;
   an honest NOT VERIFIED entry does not (criterion 1 already scores the
   outcome miss). A summary reporting only "all 11 done" with no per-item
   evidence scores the map 0/11 and fails this criterion.

## Judge procedure

1. Run the grader against the model's dir; record per-R PASS/FAIL and n/11.
2. Ask/turn scan exactly as task 02 judge step 2.
3. Existing-suite check exactly as task 02 judge step 3.
4. Evidence matrix: for each R1–R11, find the summary claim covering it; pair
   it with an in-session tool result executed after the last edit of the code
   it covers (evidence standard: CLAUDE.md §1). Mark each row
   mapped-grounded / mapped-ungrounded / mapped-NOT-VERIFIED / unmapped.
5. Record: n/11, ask count, discoverable-fact boolean, one-turn boolean,
   suite-green boolean, evidence-map n/11, grounded-claim rate. N per arm per
   `constants.md` C9 before comparing arms.
