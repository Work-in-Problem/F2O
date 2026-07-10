# Task 14 — Cold resume from working notes (two real sessions)

- **Dimension:** working memory / session resume · **Primary skill under
  test:** `managing-working-memory` (phase 3) — elaborating owner of the notes
  surface; the single file and its sections are CLAUDE.md §3, the creation
  trigger is `constants.md` C3.
- **Fixture:** `evals/fixtures/multi-req-cli/` — **provided, runnable; same
  grader as task 02.** Session-1 prompt is task 02's on purpose (see below),
  but this is its own task with its own protocol — never mix task-14 numbers
  with task 02's.

> **⚠️ OPERATOR-RUN ONLY — TWO REAL Claude Code sessions required.** This task
> cannot run under a harness where the model under test is itself a sub-agent:
> such runs complete atomically and cannot be interrupted mid-turn, and a
> "second session" spawned by the same parent inherits or reconstructs context
> instead of starting cold. The interrupt plus the cold start ARE the
> measurement. Same spirit as tasks 08–09 / README §10: confirm before every
> run that the operator can hard-stop session 1 mid-turn.

### Operator protocol (documented midpoint — follow exactly)

1. Copy the fixture per README §5 (`TASK.md` must be in the copy); arm B adds
   curriculum files per §5.3; then `git init && git add -A && git commit -m
   pristine` in `$RUN_DIR` (as in tasks 08–09) so session 2 can read real
   state via git and the judge can diff mechanically.
2. **Session 1:** paste the session-1 prompt. Let it run.
3. **Midpoint poll:** every ~2 minutes run
   `rm -rf "$POLL" && cp -R "$RUN_DIR" "$POLL" && evals/judge/multi-req-cli-check.sh "$POLL"`
   — always poll a copy, never run the grader inside the run dir (a poll that
   catches a file mid-write may error; treat that as not-yet and poll again).
   **Interrupt session 1 at the FIRST poll scoring in the 4–8 band out of 11**
   (~half the requirements): hard stop mid-turn — Esc, then close the session.
   Do NOT let it finish the turn or write a sign-off. If a poll jumps past 8,
   interrupt immediately anyway and keep the run while the score is < 11;
   discard and rerun only when the first nonzero poll is already 11/11
   (nothing left to resume — judge notes it in one line per README §7).
4. **Snapshot:** `cp -R "$RUN_DIR" <outside>/task14-midpoint`; record
   k1 = grader score of that snapshot. Then touch NOTHING in `$RUN_DIR`:
   no commit, no cleanup. Session 2 must find the tree exactly as session 1
   left it — dirty working tree over the pristine commit, plus
   `WORKING_NOTES.md` only if session 1 actually wrote one (add nothing,
   delete nothing).
5. **Session 2:** a FRESH Claude Code session in the same `$RUN_DIR`, same arm
   and model. Paste the session-2 prompt. The model's entire context is the
   working copy (including whatever notes exist) plus that prompt — no
   transcript carryover, no summary paste, replies per README §5.6 only.

## Task prompt

Session 1 (identical to task 02 — session 1 is not the thing measured, and
reusing the calibrated prompt keeps session-1 trajectories comparable):

```
Implement the feature request described in TASK.md.
```

Session 2:

```
A previous session started implementing the feature request described in
TASK.md in this directory and was interrupted partway through. Finish the job.
```

## Planted trap

Nothing in the fixture is new — the trap is the cold start over a half-done
tree.

1. **Memory-based continuation:** session 2 "continues" from what TASK.md
   implies rather than what disk shows — re-implementing requirements already
   done (a duplicate CHANGELOG entry, a duplicate README usage line, a second
   `summary` sub-parser that crashes argparse) or assuming the tail was done
   and dropping it.
2. **Write-side failure (session 1, arm B):** notes that cannot be resumed
   from — no `WORKING_NOTES.md` despite a trajectory that plausibly meets the
   C3 trigger, or a stale `## State` section. The interrupt is unannounced,
   so only continuously maintained state survives (`managing-working-memory`
   owns that discipline).
3. **Trust-without-audit:** reading the notes and believing them without a
   reality check before editing. Notes claims are claims — the evidence
   standard of CLAUDE.md §1 applies to them like anything else.

## Metrics

README §1 note, as in task 08: this task's dimension IS resume behavior, so
the session-2 opening is scored as a criterion here — the outcome criteria
still gate first.

- **final coverage n/11** (primary outcome): grader on the final state.
- **no-double-implementation** (boolean, mechanical): (a) every requirement
  green at midpoint (grader on the snapshot) is still green at final;
  (b) no duplicated CHANGELOG line: the Unreleased block piped through
  `sort | uniq -d` is empty; (c) no duplicated README usage line, same check;
  (d) a duplicated argparse registration crashes the CLI and is already
  caught by (a).
- **opening audit** (boolean, criterion): in session 2, BEFORE the first
  Edit/Write tool call: (i) `WORKING_NOTES.md` is Read IF it exists in the
  tree (any arm), AND (ii) at least one reality-audit command runs —
  `git status`, `git diff`, a test-suite run, or executing the CLI. Editing
  first = memory-based continuation = false.
- **session-2 ask count** (README §5.6; target 0): the prior state is fully
  discoverable on disk; "what was already done?" is a discoverable-fact ask
  (task 02's rule; `search-first-context` rule 11).
- Secondary (diagnostic, never gating): k1; whether session 1 left
  `WORKING_NOTES.md` with a current `## State` (write-side, arm-B expectation
  per C3 / CLAUDE.md §3); session-2 tool calls to completion; session-1 ask
  count.

## Pass criteria (all required)

1. **Outcome:** grader prints **11/11 satisfied** on the final state AND the
   fixture's pre-existing tests pass (task 02 criterion 4) — nothing dropped.
2. **Nothing doubled:** no-double-implementation boolean true.
3. **Opening audit:** boolean true. A perfect outcome that opened with blind
   edits is recorded "lucky-resume" and fails this criterion.
4. **Zero session-2 asks** about disk-discoverable state (a genuinely
   unanswerable ask — there should be none — may be excluded with a one-line
   judge justification, as in task 02).

## Judge procedure

1. Grader on the final dir → n/11; existing-suite check per task 02 step 3.
2. Grader on `task14-midpoint` → the k1 requirement set; verify every
   k1-green requirement is also final-green (regression = doubled or broken).
3. Duplicate checks:
   `awk '/^## Unreleased/{f=1; next} /^## /{f=0} f' CHANGELOG.md | sort | uniq -d`
   empty, and `grep 'logstats.py summary' README.md | sort | uniq -d` empty.
4. Session-2 transcript: locate the first Edit/Write; confirm the prior calls
   include a `WORKING_NOTES.md` read when the midpoint snapshot shows the file
   existed, and at least one of git status / git diff / suite run / CLI
   execution. Mark the opening-audit boolean.
5. Ask scan per README §5.6 on session 2 (session-1 asks recorded separately
   as a diagnostic).
6. Record: final n/11, k1, k1-preserved boolean, duplicate booleans,
   opening-audit boolean, session-2 ask count, notes-file
   existence + `## State` currency (diagnostic), session-2 tool-call count.
   N per arm per `constants.md` C9 before comparing arms.
