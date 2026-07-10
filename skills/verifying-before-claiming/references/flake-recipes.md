# Flake recipes: repeat-running tests per runner

How many runs and when: constants.md C1 governs re-run counts (10 consecutive; 30 when
the observed failure rate is under ~20%), and C2 governs the run count required before
claiming a nondeterministic bug "fixed". Never invent a local number — cite the constant.

## When repeat-running is REQUIRED

Any of these makes a single green run worthless (SKILL.md rule 4):

- The test's outcome differed between any two runs, ever, anywhere (including CI).
- The failure or the diff involves time, sleep, ports, network, random seeds, ordering,
  or parallelism.
- A previously failing test went green on the first try after your change and you cannot
  state the causal mechanism.
- You are about to claim "fixed" for a nondeterministic bug — the C2 protocol applies:
  report "pre-fix k/N failures, post-fix 0/M".

## When a single re-run is enough

The failure was deterministic (same failure every run), the fix has a clear stated
mechanism, and the test is deterministically green after it. Repeat-running here is
optional; spend the time on blast-radius checks instead. If you believe a required case
is a justified exception, state a one-line justification and proceed.

## Generic wrapper (any runner)

```sh
bash scripts/repeat-run.sh 10 -- <exact test command>
```

Prints a pass/fail tally and the first failing output. Prefer this when the runner has no
native repeat flag, so the before/after counts are directly comparable.

## Per-runner invocations

### pytest

```sh
pip install pytest-repeat
pytest --count 10 tests/test_upload.py::test_upload_retry
```

Without the plugin, use `repeat-run.sh`. Add `-p no:cacheprovider` to rule out
cache-order effects. To separate ordering flakes from timing flakes, run the test alone
AND inside the full suite — a test that only fails in the suite is order/shared-state
dependent.

### vitest / jest

No native whole-run repeat flag — loop it:

```sh
bash scripts/repeat-run.sh 10 -- npx vitest run src/upload.test.ts
bash scripts/repeat-run.sh 10 -- npx jest src/upload.test.ts
```

Do NOT use `--retry` (vitest) or retry wrappers to verify a fix — retries mask flakes by
counting a retried pass as green. Retry flags are for CI resilience, not for evidence.

### go

```sh
go test -count=10 -race -run 'TestUploadRetry$' ./pkg/upload
```

`-count` also bypasses Go's test cache — an `ok ... (cached)` line is not a fresh run.
Always add `-race` when the diff is anywhere near concurrency.

### cargo

```sh
bash scripts/repeat-run.sh 10 -- cargo test upload_retry -- --exact
```

The first iteration pays the build; later iterations are cheap. Vary `--test-threads=1`
vs the default to expose parallelism dependence.

### rspec

Order-dependence sweep (different seeds shuffle test order):

```sh
for s in 1 7 42 1337 31337; do bundle exec rspec spec/upload_spec.rb --seed $s || break; done
```

Then repeat a single fixed seed via `repeat-run.sh` — failures across seeds indicate
order dependence; failures on a fixed seed indicate timing/resource dependence.

## Reporting

Always report counts, not adjectives: "pre-fix 4/10 failed, post-fix 0/30" (per
constants.md C2), and state the causal mechanism. If the C2 run count M is impractical,
the verdict is "high confidence, not proven" — never "fixed".
