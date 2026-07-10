# Finding format — template, calibration, worked examples

Read before writing the first review report of a session. The per-finding shape exists so
a downstream step — a human, a stricter filter, a merge bot — can re-rank or re-cut the
findings without redoing the review (SKILL.md rule 7).

## The per-finding template

```
[severity/confidence] file:line — one-sentence defect
Scenario: <concrete input or state> → <wrong outcome>
Evidence: <lines read / command + decisive output quoted>          (CONFIRMED findings)
Would confirm: <the exact check that would confirm or kill it>     (HYPOTHESIS findings)
Fix direction: <one line — a direction, never a patch (SKILL.md rule 10)>
```

## Severity — impact if merged, never effort-to-fix

| Level | Meaning |
|---|---|
| blocker | merged as-is: data loss, security hole, crash or silently wrong results on a mainline path |
| major | wrong behavior on realistic edge/error/concurrent paths; correctness bug with a workaround |
| minor | real but low-stakes: misleading name, missing test for changed behavior, avoidable hot-path cost |
| nit | style or polish with no behavioral stake — normally lives in the folded tally |

## Confidence — how far YOU traced it (CLAUDE.md §1 discipline, per finding)

- **CONFIRMED** — failure path traced end-to-end against the actual source this session;
  the finding quotes its evidence (code read, command output).
- **HYPOTHESIS** — plausible mechanism you could not fully trace (no runtime access,
  dynamic dispatch, unreadable vendored code); the finding states exactly what would
  confirm or kill it.

Never average the two axes: rank by severity, display confidence. A [blocker/HYPOTHESIS]
leads the report; a [nit/CONFIRMED] stays in the tally. Demoting a scary-but-unconfirmed
finding is precisely the recall failure the skill exists to kill (SKILL.md, trap section).

## Report skeleton

1. Findings, most-severe first — everything above any threshold in force
2. Folded tally: "+ N minor/nit findings — available on request"
3. Pre-existing (outside this diff): one line each (SKILL.md rule 2)
4. Coverage statement (SKILL.md rule 8)

## Worked finding — CONFIRMED

```
[major/CONFIRMED] src/billing/invoice.py:142 — apply_credit mutates invoice.total before
the currency guard, so a failed guard persists a corrupted total
Scenario: invoice in USD, credit in EUR → line 142 subtracts credit.amount from total →
the currency guard at line 151 raises → the `finally: self.save()` at line 158 persists
anyway → invoice total is short by the raw EUR amount.
Evidence: read apply_credit in full (lines 138–160): mutation at 142, guard at 151,
save-in-finally at 158, no rollback between. Scratch run `python -m scratch.credit_repro`
printed `total=61.00` for a 100 USD invoice + 39 EUR credit (expected: 100.00 unchanged,
plus CurrencyMismatch raised).
Fix direction: validate currency before mutating, or move the save out of `finally`.
```

Why it is CONFIRMED: the path is traced line-by-line AND a cheap scratch run reproduced
the wrong outcome — evidence quoted, not asserted (SKILL.md rules 4 and 6).

## Worked finding — HYPOTHESIS

```
[blocker/HYPOTHESIS] src/workers/cache.go:88 — new RefreshCache goroutine appears to
write cache.entries concurrently with Lookup's read at cache.go:41, no lock on either path
Scenario: refresh tick races a request → concurrent map read/write → runtime panic kills
the worker process.
Would confirm: `go test -race ./src/workers/` (not run: no Go toolchain in this
environment — recorded in the coverage statement), or reading vendor/libbase's embedded
struct for an internal mutex (vendored source unreadable in this pass; grep for
`Lock\|RLock` in src/workers/ returned 0 hits).
Fix direction: guard entries with the struct's mutex, or switch to sync.Map.
```

Why it is a HYPOTHESIS, not dropped: the mechanism is concrete and blocker-grade, but one
defeater (an internal mutex in the vendored base) could not be ruled out. It is reported —
labeled, ranked by severity, with its confirming check named — never silently withheld.

## Worked coverage statement

> Coverage: read all 6 changed files (diff hunks + enclosing functions;
> src/billing/invoice.py in full, 214 lines — under the constants.md C14 cutoff).
> Dimensions swept: correctness, error handling, security, tests, API compatibility.
> NOT swept: performance (no profile taken). Checks run: `pytest tests/billing -q` →
> `47 passed in 31.2s`; `mypy src/billing` → `Success: no issues found`. NOT covered:
> migrations/0042_backfill.sql (needs staging-shaped data to exercise),
> src/workers/cache.go beyond static read (no Go toolchain here). Pre-existing issues
> outside this diff: 1, listed above.

Every "NOT" line is load-bearing: it converts silent gaps into explicit ones the reader
can route elsewhere. A review that omits them claims coverage it does not have.

## Buried bug vs ranked — before and after

**Before (illegal — the real bug is item 8 of 8, in file order):**

```
1. imports in payments/retry.ts not alphabetized
2. `MAX_ATTEMPTS` could be a named export
3. docstring on capture() outdated
4. prefer const over let at retry.ts:12
5. rename `tmp` → `pendingCharge`
6. trailing whitespace in retry.spec.ts
7. test names inconsistently cased
8. Also, I think the retry loop in payments/retry.ts might re-send the payment on
   timeout? Worth a look.
```

Outcome: the reader fixes seven nits, skims the hedge in item 8, ships a double-charge.

**After (SKILL.md rule 7 — ranked, folded, evidence-first):**

```
[blocker/CONFIRMED] payments/retry.ts:57 — timeout branch re-enqueues an
already-captured charge
Scenario: gateway capture succeeds but the response times out → catch block at 57
re-enqueues the job → second capture on retry; customer charged twice.
Evidence: traced capture() → enqueueRetry() with no idempotency key (grep `idempotency`
in payments/: 0 hits); retry.spec.ts only covers pre-capture timeouts.
Fix direction: attach an idempotency key, or gate re-enqueue on capture status.

+ 7 nit findings — available on request.
```

Same search, same candidates — the difference is entirely in the reporting layer: the one
real bug leads with a scenario and evidence, and the nits fold instead of competing.
