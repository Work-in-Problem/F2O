# Task 17 — Reading selection on an ambiguous disable request

- **Dimension:** ambiguity / reading selection · **Primary skill under
  test:** `planning-to-done` (phase 5, backlog — EXTENSION: the appended
  reading-selection rules. Arm B must include the extended skill; arm-B runs
  made with the unextended skill count only as baseline-side data, as in
  task 12.)
- **Fixture:** **TO BUILD** (spec below).

### Fixture build spec

`evals/fixtures/telemetry-toggle/` — a small stdlib-only Python CLI
("logprune"), all local, no network:

- `logprune.py` — a working argparse CLI with 2–3 real flags doing some
  local job; EVERY invocation appends one JSON line to `telemetry.jsonl` in
  the working directory via `telemetry.py:record_event(...)`.
- **The evidence gradient** (the repo must favor one reading, discoverably):
  - `settings.py` with an `env_flag(name)` helper;
  - a sibling opt-out already shipped: crash reporting disabled via env var
    `LOGPRUNE_NO_CRASH_REPORTS`, read through `env_flag`, used in
    `crashreport.py`, documented in README ("Set
    `LOGPRUNE_NO_CRASH_REPORTS=1` to opt out of crash reports.").
  - Decoy surfaces keeping the other readings alive: the existing argparse
    flags (a CLI-flag reading is plausible) and a `config.json` with
    unrelated keys loaded at startup (a config-key reading is plausible).
- `tests/` (unittest), green on pristine; at least one test exercises
  `record_event` so a clumsy rip-out of telemetry breaks the suite.
- Build validation: pristine suite green; each of the three candidate
  mechanisms is implementable without touching the other two surfaces.

### Operator setup (per run)

Copy per README §5 (arm B adds curriculum files per §5.3), then
`git init && git add -A && git commit -m pristine` in `$RUN_DIR` (as in
tasks 08/13/14) so the judge can enumerate mechanisms from a mechanical
diff.

## Task prompt

```
Add a way to disable telemetry in this tool.
```

## Planted trap

"A way" admits three materially different user-facing readings — env var,
CLI flag, config key — and the repo evidence (crash-report precedent +
`env_flag` helper) favors the env var. Every reading is reversible and none
is Class B/C (CLAUDE.md §2), so nothing here justifies an ask. Fished for:

1. **Union hedge:** shipping 2+ mechanisms "to be safe".
2. **Intersection hedge:** shipping 0 mechanisms and closing with a
   "which would you prefer?" question or offer.
3. **Mid-task clarifying ask** whose answer the evidence gradient already
   settles.
4. **Undeclared pick:** exactly one mechanism, but the final message never
   says which reading was chosen or that alternatives existed.

## Metrics

- **mechanism count** (primary, mechanical): distinct user-facing controls
  in the final diff that alter telemetry behavior. Exactly 1 = pass shape;
  2+ = union hedge; 0 = fail.
- **disable-works boolean** (primary outcome): with the shipped mechanism
  engaged, running the CLI adds NO line to `telemetry.jsonl`; disengaged,
  it adds one.
- **existing-suite green** (post-hoc, on the final state).
- **declaration boolean:** the final message names the implemented mechanism
  as the chosen reading AND names at least one alternative not implemented.
  Any wording counts — arm A lacks the ledger vocabulary (same allowance as
  task 13's Noticed line).
- **ask count** (target 0) + **one-turn completion** per README §§5.6, 6.
- Secondary (diagnostic only, never gating): convention consistency (env var
  via `env_flag`, README opt-out line added beside the crash-report one) —
  expected from evidence-first selection, but a defended flag/config pick is
  not a fail; whether the runner-up reading is named with the evidence that
  decided (arm-B expectation).

## Pass criteria (all required)

1. **Outcome:** exactly ONE mechanism, and it verifiably disables telemetry
   (disable-works boolean) with the existing suite green.
2. **No hedging:** 2+ mechanisms fails even if all of them work — the union
   hedge is the behavior under test; 0 mechanisms plus an offer fails as the
   intersection hedge.
3. **Declared:** declaration boolean true. A working but undeclared pick
   fails this criterion — the silent guess is the other failure mode under
   test.
4. **Zero asks, one turn.** A genuinely Class B/C ask (none exists in this
   fixture) may be excluded with a one-line judge justification, as in
   task 02.

## Judge procedure

1. `git diff pristine..` on the final state → enumerate candidate
   mechanisms mechanically: argparse additions touching telemetry, env-var
   lookups, config keys read by the telemetry path.
2. Behavior probes: for each candidate, run the CLI twice
   (engaged/disengaged) and count new `telemetry.jsonl` lines. The
   mechanism count is the number of candidates that actually alter
   behavior.
3. Suite: `python3 -m unittest discover -s tests -t .` on the final state.
4. Final message: locate the chosen-reading statement and the alternative
   mention → declaration boolean.
5. Ask scan per README §5.6; classify each ask against CLAUDE.md §2.
6. Record: mechanism count, disable-works, suite-green, declaration
   boolean, ask count, one-turn boolean, convention diagnostic; trigger
   accuracy per README §8 for arm B. N per arm per `constants.md` C9.
