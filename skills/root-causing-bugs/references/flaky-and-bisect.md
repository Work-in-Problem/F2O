# Flaky-bug math, amplification, and history bisection

`root-causing-bugs` is the elaborating owner of the flake-statistics protocol; every
number here derives from constants.md C1/C2, and that table wins on any conflict. Plain
per-runner repeat invocations live in `verifying-before-claiming`
`references/flake-recipes.md`; the repeat tool is that skill's
`scripts/repeat-run.sh N -- <cmd>`. This file covers what those do not: the run-count
math, raising a too-low reproduction rate, heisenbugs, bisection, and input
minimization.

## Run-count math (constants.md C2)

The chance that M post-fix runs all pass while the bug is UNFIXED is (1 − r)^M at
baseline failure rate r. C2's M = max(20, min(100, ceil(3 / r))) holds that false-green
probability at or below ~e⁻³ ≈ 5% wherever the formula is uncapped: the floor of 20
covers high rates cheaply; the cap of 100 keeps low rates affordable.

Worked example: the C1 baseline loop gave 9/30 failures → r = 0.30. Even 10 clean runs
would be only 0.7¹⁰ ≈ 2.8% likely with no fix; C2's floor lifts M to 20, driving the
false-green chance to 0.7²⁰ ≈ 0.08%. Report: "pre-fix 9/30 failures, post-fix 0/20".

| baseline r | ceil(3/r) | M per C2 | P(0/M green while unfixed) | verdict if 0/M |
|---|---|---|---|---|
| 50% | 6 | 20 | ~0.0001% | fixed |
| 30% | 10 | 20 | ~0.08% | fixed |
| 20% | 15 | 20 | ~1.2% | fixed |
| 10% | 30 | 30 | ~4.2% | fixed |
| 5% | 60 | 60 | ~4.6% | fixed |
| 3% | 100 | 100 | ~4.8% | fixed |
| 2% | 150 → cap | 100 | ~13% | "high confidence, not proven" (C2) |
| 1% | 300 → cap | 100 | ~37% | "high confidence, not proven" (C2) |

Below a few percent baseline, the cap makes all-green weak evidence — which is exactly
why SKILL rule 3 amplifies BEFORE hypothesizing: debug and fix under the amplified
harness, verify 0/M under that same harness where r is high enough for a computable M,
then re-run the original un-minimized repro (SKILL rule 11).

Two cautions:

- r is an estimate. If the C1 baseline loop produced k ≤ 2 failures, the estimate is
  noise — amplify and re-measure rather than plugging a shaky r into the formula.
- The M runs must be identical invocations of the SAME command as the baseline (same
  harness, same instrumentation state), or the two counts are not comparable.

Sizing an amplification loop reuses the same shape: N ≈ ceil(3 / suspected-r), capped
like C2. Zero failures across that N means the suspected rate was too high — halve the
suspected r and re-derive, or switch amplifiers.

## Amplification recipes (raise r, then debug)

The goal is a HIGHER failure rate, never a clean run. Cheapest first. Record which
amplifier moved the rate in `## Experiments` — that is discriminating evidence by
itself: parallelism-sensitive → shared state; seed-sensitive → data or ordering;
clock-sensitive → time logic.

1. **Bigger loop** — `repeat-run.sh <N> -- <cmd>` with N from the sizing rule above.
2. **Parallelism** — races widen under contention:
   - pytest: `pip install pytest-xdist pytest-repeat && pytest -n 4 --count 20 <test>`
   - go: `go test -race -count=20 -parallel 8 ./pkg/...` — `-race` is mandatory
     anywhere near concurrency; it converts latent races into deterministic failures
   - jest/vitest: contrast default worker pool vs `--runInBand` (jest) /
     `--pool=forks --poolOptions.forks.singleFork` (vitest); a rate difference between
     the two modes is itself ledger evidence
   - cargo: contrast default threads vs `-- --test-threads=1`
   - rspec: seed sweep first (recipe in `flake-recipes.md`), then fix the seed and loop
3. **CPU stress** — run the loop while the machine is busy: start 2–4 concurrent copies
   of the loop in SEPARATE work directories, or any busy command alongside. Same-workdir
   copies collide on ports/files — do that only deliberately, when collision IS the
   hypothesis being tested.
4. **Sleep injection** — insert a short sleep or yield inside the suspected race window
   to widen it. It is a probe, never part of the fix (red-flag list, SKILL rule 7); tag
   it `[DBG-<id>]` like any instrumentation so the final grep removes it.
5. **Clock pinning** — freeze or step time to force boundary conditions (midnight, DST,
   month-end) or to remove time-of-day masking: libfaketime (any binary), freezegun
   (python), `vi.useFakeTimers()` / `jest.useFakeTimers()` (js), or an injected clock
   where the code already accepts one.
6. **RNG seeding** — two directions: sweep seeds to FIND a failing ordering
   (`rspec --seed <n>`, `pytest -p randomly --randomly-seed=<n>`, `jest --seed=<n>`),
   then PIN the failing seed so the rare path becomes deterministic. Pin hash
   randomization too (`PYTHONHASHSEED=<n>`) when iteration order is implicated.

## Heisenbug caveat (instrumentation changes r)

- Compare like with like: the baseline k/N and the post-fix 0/M must run with the same
  instrumentation state. If logs were added mid-investigation, re-measure the baseline
  before comparing counts.
- A log line that makes the failure vanish or spike is EVIDENCE of timing sensitivity
  near that line — write it into the ledger; do not fight it.
- Prefer low-perturbation probes: an in-memory counter or ring buffer dumped at exit,
  or one debugger/REPL inspection, over per-iteration stdout prints — stdout writes
  serialize threads and shift race windows.
- Breakpoints stop the world: fine for state inspection on deterministic bugs, useless
  and misleading inside race windows.

## git bisect run — copy-paste recipe

Verdict-script contract: exit 0 = good, 1 = bad, 125 = cannot judge this commit (skip).
Exit codes ≥ 128 abort the whole bisect — normalize with if/else rather than passing
through a raw status that might come from a signal kill.

```sh
cat > /tmp/bisect-verdict.sh <<'EOF'
#!/bin/sh
# Verdict for `git bisect run`: 0 good / 1 bad / 125 skip.
set -u
npm ci >/dev/null 2>&1 || exit 125        # unbuildable commit: skip, not bad

# Deterministic bug — one run decides:
if npm test -- --run src/export.test.ts >/dev/null 2>&1; then exit 0; else exit 1; fi

# Flaky bug — replace the if/else above with a loop per constants.md C1;
# ANY failure is a bad verdict:
#   i=1; while [ "$i" -le 10 ]; do
#     npm test -- --run src/export.test.ts >/dev/null 2>&1 || exit 1
#     i=$((i+1))
#   done
#   exit 0
EOF
```

```sh
git bisect start
git bisect bad HEAD
git bisect good v1.2                  # tag, hash, or the known-good date's commit
git bisect run sh /tmp/bisect-verdict.sh
git bisect log   # quote the first-bad line into ## Experiments before resetting
git bisect reset
```

Flaky-bisect warning: bisect trusts every verdict absolutely. One false "good" (bug
present, loop happened to pass) poisons the remaining search. Size the in-script loop
so P(all green while the bug is present) = (1 − r)^N stays small — same table as above.
And the first-bad commit is only where the cause ENTERED: the mechanism-completeness
check (SKILL rule 8) still stands between the commit hash and the words "root cause".

## git log -S / -G — when history is not bisectable

Squashed or rebased history, an unbuildable range, or an environment-dependent repro →
search content history instead of bisecting, BEFORE any manual code reading:

```sh
git log -S'invalidateCache' --oneline --since='2026-05-01' -- src/
git log -G'timeout\s*[:=]' --oneline -- src/ config/
git show <hash>
```

`-S` finds commits that change the OCCURRENCE COUNT of the string (an addition or
removal); `-G` finds commits whose diff text matches the regex, catching edits within a
line and moves that `-S` misses. Take the symbols from the failing trace or the repro's
output, not from guesses.

## Delta-debugging a failing input

For data-dependent failures — a specific payload, fixture, or file triggers the bug:

1. Confirm the FULL input fails under the repro loop (per C1 when flaky).
2. Split the input in half; run each half through the same loop.
3. A half fails → recurse into it. Both halves pass → the failure needs elements from
   both: switch to removing one element at a time from the smallest failing set.
4. Stop when removing ANY remaining element makes the failure vanish — every element
   left is load-bearing. The minimal payload usually names the layer; update the
   ledger with it.
5. Keep the original input. The eventual fix is verified against the ORIGINAL
   un-minimized repro (SKILL rule 11), not only the minimized harness.

When the bug is flaky, every "passes" verdict during minimization needs the C1 loop —
one green cut is the same false-good trap as flaky bisect.
