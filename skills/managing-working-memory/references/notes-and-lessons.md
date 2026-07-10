# Notes and lessons — worked examples

Companion to `managing-working-memory`. Four parts: a WORKING_NOTES.md captured
mid-task, six lesson rewrites, the consolidation pass, and a distill-and-drop
checkpoint. Paths, ports, and commands are illustrative — the shapes are the point.

## Part 1 — A WORKING_NOTES.md captured mid-debugging

Snapshot from partway through diagnosing intermittent 500s on a webhook endpoint. Read
it as a stranger would (skill rule 5): could you resume from this file alone, with zero
transcript? Note what is ABSENT — `## Experiments` and `## Delegation` never earned
content, so they do not exist (skill rule 3). Every update so far has been an Edit of a
section to current state, not an appended log line (skill rule 4).

```markdown
# WORKING_NOTES.md

## Goal
- Verbatim ask: "Webhook deliveries to /api/webhooks/stripe intermittently 500 in
  staging since Tuesday. Find the cause and fix it."
- Done means: red/green per verifying-before-claiming rule 3, then 0 failures across
  the repeat protocol (constants.md C1), plus a stated causal mechanism.
- Constraints from memory sweep (verify before trust):
  - [2026-06-30] When running payments tests, export STRIPE_MOCK_PORT=12111 —
    re-verified 2026-07-10: `grep STRIPE_MOCK_PORT /Users/dev/acme/apps/payments/.env.test` → present.

## Plan
- [x] Reproduce the 500 locally
- [x] Rule out connection-pool exhaustion
- [x] Rule out clock skew in signature verification
- [ ] DOING: test the raw-body double-read hypothesis
- [ ] Fix + red/green on the same repro command
- [ ] Repeat-run per constants.md C1; harvest lessons

## State
- DONE: repro established. `cd /Users/dev/acme && pnpm --filter payments test:int
  webhooks -- --repeat 20` → 3/20 runs fail with SignatureVerificationError at
  /Users/dev/acme/apps/payments/src/webhooks/verify.ts:41.
- DOING: instrumenting verify.ts to log rawBody byte length on failure — if length
  differs from Content-Length on failing runs, double-read is confirmed.
- WRITE-AHEAD [2026-07-10 14:32]: about to run `pnpm --filter payments db:reset`
  (DROPS and reseeds local payments_test DB) to rule out state pollution. Recovery if
  interrupted: the command is idempotent from zero — re-run it; seed lives at
  /Users/dev/acme/apps/payments/prisma/seed.ts.
- NEXT: if double-read confirmed → capture the raw buffer before the JSON middleware
  in /Users/dev/acme/apps/payments/src/app.ts (line 27 registers the parser).
- BLOCKED: none.

## Findings
- Failures cluster when two deliveries arrive <50ms apart — staging log pull,
  logs/staging-webhooks-0708.txt lines 1123–1180.
- verify.ts reads `req.rawBody`, which is set by middleware at src/app.ts:27 —
  registration order-dependent, so any earlier consumer of the stream corrupts it.

## Ruled out
- Connection-pool exhaustion — killed by: `grep -c "pool timeout"
  logs/staging-webhooks-0708.txt` → 0 in the failure window; pool metrics flat
  during the 500 bursts.
- Clock skew (signature tolerance window) — killed by: same repro command with the
  test clock frozen via the `withFrozenClock` hook → still 3/20 failures; tolerance
  is not the variable.
- stripe-mock version drift — killed by: `pnpm why stripe-mock` → 0.180.0 in both
  local and CI lockfiles; identical failure rate in both environments.

## Lessons
- Candidate: when signature verification fails intermittently under concurrent
  deliveries, suspect body-parsing middleware consuming the raw stream before
  checking clocks or tolerances. (Promote at harvest only if the mechanism confirms.)
```

What makes this resumable: status tags on every State line; exact commands with cwd and
flags; the write-ahead entry means a crash during `db:reset` costs nothing; each
ruled-out line carries the killing command, so no dead hypothesis gets re-diagnosed
after compaction (skill rules 10–11); the Lessons entry is explicitly a candidate — it
is not promoted until the evidence exists (skill rule 12).

## Part 2 — Six lesson rewrites, bad → good

Target form (skill rule 7): `[YYYY-MM-DD] When <trigger>, do <action> because
<evidence>`.

**1. Observation → rule**
- Bad: `The build failed with an out-of-memory error.`
- Good: `[2026-07-10] When building @acme/api, export
  NODE_OPTIONS=--max-old-space-size=4096 before pnpm build, because the tsc step OOMs
  on the default heap (hit 2026-07-08 and 2026-07-10).`

**2. Observation → rule**
- Bad: `Prisma types were stale again.`
- Good: `[2026-07-10] When schema.prisma changes, run pnpm prisma generate before
  typecheck, because @prisma/client is generated and a stale client fails typecheck
  with phantom type errors.`

**3. Narrative → trigger-action**
- Bad: `Spent a while on flaky tests today. Tried a few things, turned out to be
  timezone related, fixed now.`
- Good: `[2026-07-10] When running apps/web date tests, export TZ=UTC first, because
  date-boundary assertions fail in non-UTC zones (failures reproduced, then 0 across
  the C1 repeat protocol after the fix).`

**4. Undated → dated, with the supersession syntax**
- Bad: `Dev API runs on port 3001.`
- Good: `[2026-07-10] When hitting the dev API, use http://localhost:8080 — port 3001
  superseded 2026-07-10 (moved in apps/api/.env.example; confirmed via
  curl -s localhost:8080/health → ok).`
- How this was written (update-before-append, skill rule 8): `grep -in "3001\|dev
  api\|port" MEMORY.md` → hit on the stale line → Edit that line in place to the Good
  form above. No new bullet appended; the file holds one truth about the port, dated.

**5. Vague → command-exact**
- Bad: `Start the mock server before integration tests or they fail.`
- Good: `[2026-07-10] When running packages/billing integration tests, first run
  pnpm --filter billing mock:stripe and wait for "listening on :12111", because the
  suite hits the local mock and dies with ECONNREFUSED otherwise.`

**6. Vague → command-exact (and altitude — skill rule 12)**
- Bad: `Fixed the webhook test by bumping the timeout in webhooks.test.ts.`
  (Task-specific residue: the trigger can never fire again, and it hides the
  mechanism.)
- Good: `[2026-07-10] When a payments integration test fails only under parallel
  workers, re-run it with --runInBand before touching timeouts, because the shared pg
  testcontainer serializes badly and timeout bumps only mask that.`

## Part 3 — The consolidation pass (constants.md C7)

Trigger: the durable memory surface exceeds the C7 budget. Run the pass BEFORE
appending the entry that prompted the check — never append onto rot.

1. Read the whole file in one Read call.
2. Bucket entries by topic (ports, env vars, build, tests, deploy) — grep keyword
   clusters to find scattered relatives.
3. Merge duplicates and overlaps into one entry per fact: keep the newest date, fold
   unique evidence in, keep trigger→action form.
4. Delete: entries marked `superseded` whose replacement survives; entries whose
   trigger can never fire again (tool removed, repo migrated); narrative residue that
   never had a trigger.
5. Do not re-date untouched entries — the date is evidence age, not a freshness stamp.
6. Confirm the result reads in a single Read call, then write the new entry via
   update-before-append (skill rule 8).

**Before** (fragment of a rotted file — duplicates, contradictions, narrative):

```markdown
- Dev API runs on port 3001
- [2026-04-12] When hitting the dev API, use port 8080
- The build failed today, watch out for memory
- [2026-03-02] When building @acme/api, export NODE_OPTIONS=--max-old-space-size=4096 because tsc OOMs
- build OOM again 2026-05-20, the NODE_OPTIONS trick still works
- Tests are flaky sometimes
- [2026-05-01] When running apps/web tests, export TZ=UTC because date tests fail otherwise
- TZ thing again — remember UTC!
- [2026-02-11] When deploying, run smoke tests (superseded 2026-04-03)
- [2026-04-03] When deploying, run pnpm smoke:staging before promoting because it catches config drift
```

**After** (one truth per fact, newest dates, evidence folded in):

```markdown
- [2026-04-12] When hitting the dev API, use http://localhost:8080 — port 3001 superseded 2026-04-12.
- [2026-05-20] When building @acme/api, export NODE_OPTIONS=--max-old-space-size=4096 first, because the tsc step OOMs on the default heap (seen 2026-03-02, 2026-05-20).
- [2026-05-01] When running apps/web tests, export TZ=UTC first, because date-boundary tests fail in non-UTC zones.
- [2026-04-03] When deploying, run pnpm smoke:staging before promoting, because it catches config drift the unit suite cannot.
```

Ten lines of rot became four load-bearing lines: the port contradiction is resolved and
dated, two OOM sightings merged into one entry with both dates as evidence, the
narrative fragments are gone, and the superseded deploy entry is deleted because its
replacement survives.

## Part 4 — Distill and drop (skill rule 14)

The moment: the webhook diagnosis from Part 1 has just confirmed its mechanism. The
transcript holds ~400 lines of test output, the full instrumentation diff, and three
staging-log excerpts. What gets written into WORKING_NOTES.md now decides what a
post-compaction session can still do — the raw transcript must be treated as already
gone.

**Bad checkpoint** — pasting the 40 decisive-looking lines of test output and the
whole instrumentation diff into `## Findings`. It bloats the file past what one Read
should carry, buries the one line that matters, and is STILL not resumable: the paste
shows what happened but not how to regenerate or extend it.

**Good checkpoint** — anchors, one decisive line, regenerating commands:

```markdown
## Findings
- CONFIRMED: rawBody double-read. Decisive line: `rawBody len=0, Content-Length=482`
  on every failing run of `cd /Users/dev/acme && pnpm --filter payments test:int
  webhooks -- --repeat 20` (3/20 fail). Guilty registration:
  /Users/dev/acme/apps/payments/src/app.ts:27.
- Instrumentation patch is throwaway: `git diff apps/payments/src/webhooks/verify.ts`
  regenerates it; revert before the fix lands.
```

The transcript is now expendable: everything a stranger needs is the anchor
(app.ts:27), one decisive output line, and the two commands that regenerate the rest.
When compaction hits, the rule 10 ritual re-reads THIS file — the compaction summary
("investigated webhook failures, found a middleware issue") could not have reproduced
the repro command, the failure rate, or the line anchor.
