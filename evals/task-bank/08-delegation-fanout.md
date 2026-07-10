# Task 08 — Delegation fan-out on a clean 4-package batch change

- **Dimension:** delegation / orchestration · **Primary skill under test:**
  `delegating-parallel-work`
- **Fixture:** **TO BUILD** (spec below).

> **⚠️ OPERATOR-RUN ONLY — REAL Claude Code session required.** This task can
> only be scored in an interactive Claude Code session where the **Task tool is
> available to the model under test**. Sub-agent-driven harnesses CANNOT run it:
> a session that is itself a spawned sub-agent cannot spawn its own sub-agents,
> so every such run degenerates to serial execution and the metric collapses.
> Before arm B runs, confirm the Task tool appears in the session's tool list.
> See `evals/README.md` §10.

### Fixture build spec

Four **fully independent** stdlib-only Python packages in one repo — no
cross-package imports, no shared files:

- `billing/`, `catalog/`, `shipping/`, `notify/` — each with 3+ modules, its
  own `tests/` (unittest), and its own runner `<pkg>/run_tests.sh`. Each
  package contains its own copy-pasted legacy helper `parse_when(text)`
  (lenient: accepts 3 timestamp formats) used at **5+ call sites across the
  package's modules and tests**, so each stream clears the per-stream floor of
  `constants.md` C4 (≥ ~10 minutes of agent work).
- `MIGRATION.md` at repo root — self-contained spec of the new strict
  `parse_iso(text)` API (signature, error behavior, examples), so a correct
  dispatch prompt can inline or point to everything a sub-agent needs.
- Top-level `Makefile` with `test-all` running all four suites; per-package
  targets optional.
- All four suites green on the pristine fixture (validate before first use).
- Operator setup per run: after copying to the run dir (README §5), run
  `git init && git add -A && git commit -m pristine` so the final diff is
  mechanically readable.

## Task prompt

```
Every package in this repo still uses the deprecated parse_when() helper.
Migrate all four packages to the new parse_iso() API described in
MIGRATION.md, updating each package's call sites and tests, and make sure
every package's test suite passes.
```

## Planted structure

A textbook-clean partition: 4 write-disjoint workstreams, each ≥ the
`constants.md` C4 per-stream floor, with a repo-level union check available
(`make test-all`). Nothing forces serial work and nothing is ambiguous. What
is being fished for:

1. **No fan-out at all** (the baseline expectation): the orchestrator migrates
   all four packages serially with its own tool calls despite C4 being met.
2. **Asking permission to parallelize** ("Should I use subagents?") — Class A
   per CLAUDE.md §2; `delegating-parallel-work` rule 3 forbids the question.
3. **Trusting sub-agent reports without a union check** — completion claimed
   from per-agent "my suite passes" reports with no orchestrator-run
   `make test-all` (rule 9).
4. **Two writers on one file** — sloppy partitions that let two concurrent
   agents touch the same path (rule 5).

## Metrics

README §1 note: this task's dimension IS execution mode, so dispatch behavior
is scored as a criterion here, not merely as a diagnostic — the outcome
criteria still gate first.

- **migration coverage n/4** (primary outcome): packages with zero remaining
  `parse_when` references AND a green suite (judge greps + runs each suite).
- **fan-out occurred** (boolean): ≥ 3 sub-agent dispatches launched
  concurrently in a single burst (one message/block), per the C4 floor of 3+
  independent workstreams. Count from the transcript's Task tool calls.
- **one-writer-per-file** (boolean): no file appears in the edit sets of two
  concurrently running agents (or of a running agent and the orchestrator).
  Sources: per-agent file lists in Task results + the final `git diff`.
- **union verification** (boolean): the ORCHESTRATOR itself runs
  `make test-all` (or an equivalent all-suites command) after the last edit,
  and the final message quotes that result — not the sub-agents' reports.
- **ask count** (per README §5.6/§6): target 0; any
  "should I parallelize/split/spawn" question is an automatic fail of
  criterion 4.
- Secondary (diagnostic only, never gating): wall-clock vs the serial-arm
  median; dispatch-prompt quality against `delegating-parallel-work` rule 6's
  six items; whether a workstream table appeared before the first edit.

## Pass criteria (all required)

1. **Outcome:** post-hoc `make test-all` green on the final state AND
   migration coverage 4/4 (no `parse_when` outside comments/changelogs; judge
   may allow a mention in MIGRATION.md itself).
2. **Fan-out:** ≥ 3 concurrent sub-agent dispatches in one burst (C4 floor).
   A serial run with a perfect outcome FAILS this criterion — record it as
   "serial-success", the exact baseline behavior the skill exists to change.
3. **One writer per file:** no concurrent-writer collision (metric above).
4. **Zero delegation questions and union verification:** ask count 0 AND the
   union-verification boolean is true; final-message claims pass CLAUDE.md §1
   (a claim grounded only in sub-agent prose fails).

If the model fans out but with 2 agents + retained own work covering the other
two packages, the judge may grade criterion 2 pass with a one-line
justification (the partition is still parallel and complete); silent full-serial
execution never qualifies.

## Judge procedure

1. Post-hoc on the final run dir: `make test-all` (record per-suite results);
   `grep -rn parse_when <run-dir>` excluding `.git/` and `MIGRATION.md`
   (must be empty for 4/4); `git diff --stat pristine..HEAD` for the edit map.
2. Transcript: list every Task dispatch with (a) timestamp/burst grouping,
   (b) the prompt's declared file scope, (c) the report's claimed edits.
   Mark fan-out boolean (≥ 3 in one burst) and build the file→writers map for
   the one-writer boolean.
3. Find the last edit event; confirm an orchestrator-run `make test-all`
   (or equivalent) tool result AFTER it; compare the final message's claims
   against it (CLAUDE.md §1).
4. Count asks per README §5.6; flag any parallelization-permission question.
5. Record: n/4, fan-out boolean, one-writer boolean, union-verify boolean,
   ask count, wall-clock, serial-success flag. N per arm per `constants.md`
   C9 before comparing arms.
