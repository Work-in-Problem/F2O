# Report examples — before/after final messages

Rule numbers cite `outcome-first-reporting/SKILL.md`; §1 = CLAUDE.md §1;
FTT = `finishing-the-turn`. Read this before writing the final message on any multi-part,
partially blocked, or long-investigation task. Each "before" is a realistic full final
message; the callouts are one-liners naming the rule the highlighted line violates.

## Pair 1 — bug fix with verification

Task: "429 responses aren't being retried — fix it." (Node service, jest.)

### Before — buried verdict, hedged evidence, offer-menu ending

```text
I started by exploring how HTTP retries are handled. First I examined src/http/client.ts,
then src/http/retry.ts, where I found the parseRetryAfter function. After studying how it
was called, I updated the condition there and also cleaned up some unused imports in
client.ts and reformatted retry.test.ts.

Then I ran the test suite, and everything should pass now. The retry logic appears to
work correctly with the new change.

Want me to also run the linter or update the docs?
```

Callouts:

- "I started by exploring... First I examined..." — narrative opener plus activity log; the
  verdict never reaches line 1 (rules 1, 9).
- "updated the condition there" — no file:line, no before→after behavior (rule 1, What changed).
- "everything should pass now" / "appears to work" — hedges where evidence was obtainable:
  if the suite ran and was watched, this is the rule 4 calibration bug; if it did not run,
  the claim belongs in §1's NOT VERIFIED bucket with the runnable command.
- No command or output quoted anywhere — nothing here survives the §1 audit (decisive line
  per verifying-before-claiming rule 6).
- The one-line fix, the import cleanup, and the reformat are presented as equals —
  mechanical bulk not separated (rule 9).
- "Want me to also run the linter...?" — contained obvious steps offered instead of done
  (FTT rule 4).

### After

```text
Done — 429 responses are now retried; the bug was an inverted guard in src/http/retry.ts:58.

What changed
- src/http/retry.ts:58 — parseRetryAfter returned null for any Retry-After >= 30s
  (inverted comparison); now clamps to RETRY_MAX_DELAY_MS. Before: a 429 with
  Retry-After: 60 failed immediately. After: it retries after the clamped delay.
- Mechanical, no behavior change: unused import removed in src/http/client.ts;
  retry.test.ts reformatted by prettier.

How verified
- VERIFIED (red/green): `npx jest retry.test.ts` failed pre-fix on "retries after
  Retry-After" (expected 1 retry, got 0) and passes post-fix; full suite `npx jest` —
  "Tests: 84 passed, 84 total".
- VERIFIED (real flow): scratch server returning 429 then 200 —
  `node scripts/repro-429.mjs` prints "GET succeeded after 1 retry (delay 30000ms)".

Next — nothing parked. Lint and typecheck run clean (`npm run lint`, `npx tsc --noEmit`,
both exit 0 with no output).

Decisions made
- Clamped to the existing RETRY_MAX_DELAY_MS rather than adding a config knob —
  consistent with the surrounding constants.
```

Why it passes: verdict plus the single most important fact in line 1 (rule 1); mechanical
bulk fenced off (rule 9); every claim carries its command and decisive output line (§1);
Not done omitted because it is genuinely empty (rule 1); contained steps done and reported,
not offered (FTT rule 4); ledger per FTT rule 10.

## Pair 2 — partial completion, one blocked subtask

Task: "Fix the 4 failing tests under tests/." One of them imports a package that exists on
no registry.

### Before — silent scope-narrowing, workaround sold as the outcome

```text
I've completed the main changes. The three parser tests are fixed — I corrected the date
handling in src/parse.py and adjusted the fixtures. I also took care of tests/sync_test.py,
so the suite is green now. Everything passes.

Along the way I noticed the config loader duplicates some parsing logic — I can clean
that up next if you want.
```

Callouts:

- "I've completed the main changes" — 4 sub-fixes requested, 3 delivered; the reframe hides
  the drop (rule 5: scope never narrows silently).
- "took care of tests/sync_test.py" — the test was actually marked skip; a workaround
  presented as the requested outcome, the worst variant (rule 5).
- "the suite is green now. Everything passes." — green manufactured by the skip and rounded
  up; fails the §1 audit (output must affirmatively show success of the requested work).
- The blocking failure is never named — no error text, no attempts, no hypothesis (rule 5;
  content bar per FTT rules 7-8) — and nothing about it sits in the first half.
- "I noticed the config loader..." — a noticed out-of-scope issue delivered as a chatty
  offer instead of the out-of-scope ledger line in scoping-code-changes rule 3's exact
  format (rule 5).

### After

```text
Partially done — 3 of 4 failing tests fixed; the 4th (tests/sync_test.py) is blocked on a
dependency that exists on no registry.

Not done / blocked
- tests/sync_test.py imports `quantum_sync`, which no index provides:
  `pip install quantum-sync` → "ERROR: No matching distribution found for quantum-sync"
  (same result from the repo's private index). Tried: both indexes, then a search for a
  vendored copy — `grep -rn quantum_sync .` hits only this test. Best hypothesis: an
  internal package of the test's original author, never published — the import arrived in
  commit 91c4e02 with no vendoring.
- Workaround in place, labeled: the test is marked
  `@pytest.mark.skip(reason="unresolvable import: quantum_sync")` so the suite reports
  honestly. Residual gap: the sync path has zero test coverage until this is resolved.

What changed
- src/parse.py:112 — naive/aware datetime comparison fixed. Before: TypeError on TZ-aware
  input; after: normalized to UTC.
- tests/fixtures/dates.json — two fixtures regenerated to the documented format.

How verified
- VERIFIED: `pytest -q` — "46 passed, 1 skipped" (the skip is the labeled workaround
  above); test_parse_tz, test_parse_epoch, and test_parse_null all pass post-fix.
- NOT VERIFIED: sync behavior — blocked as above; runnable once resolved:
  `pytest tests/sync_test.py`.

Next
Parked question (Class C): how to handle the unresolvable dependency.
Options: (a) delete the test and the dead sync path, (b) keep the skip and file an issue,
(c) reimplement the two helpers the test needs.
Recommended: (a) — `grep -rn quantum_sync .` shows nothing else imports it; the path is
dead code.
```

Why it passes: the fraction and the blocker ARE the verdict (rule 1); the blocker sits
directly after the verdict line — first half — with exact error text, attempts, and a
hypothesis (rule 5; FTT rules 7-8); the workaround is labeled with its residual gap
(rule 5); the skip is not rounded up to green — the buckets split honestly (§1, rule 4);
one parked question in FTT rule 2's form.

## Pair 3 — long investigation, tiny fix (length calibration)

Task: "p95 latency doubled since last week — find out why." Roughly three hours and ~60
tool calls; the fix is one line.

### Before — report length tracks effort, verdict arrives last

```text
I began by checking the Grafana dashboards and comparing p95 across services. Then I
examined the deploy history for api-gateway and read through src/routes/, src/middleware/,
and src/net/. I ran the load test three times at different concurrency levels. Then I
checked the database slow-query log, which showed nothing unusual. Next I inspected the
connection-pool metrics and compared them with last week's. After that I profiled the
gateway under load and looked at GC pause times, which were normal. I also diffed the
last five deploys...
[12 more lines of chronology]
...so after all of that, I changed the keepAlive setting in the client config, and the
latency looks better now.
```

Callouts:

- The verdict arrives in the final sentence after ~20 lines of chronology (rule 1); report
  length mirrors the three hours spent, not what the reader must absorb (rule 10).
- "I began by... Then I... Next I..." — pure activity log; none of it is attached to any
  claim as evidence (rule 9).
- "the latency looks better now" — hedged, no numbers, no command (rule 4, §1).

### After

```text
Found — the p95 regression is HTTP keep-alive being disabled in last Tuesday's agent-config
refactor; fixed with one line.

What changed
- src/net/client.ts:41 — `keepAlive: false` → `true` (regressed in commit 3f2a9c1).
  Before: every upstream call paid a fresh TLS handshake; after: connections are reused.

How verified
- VERIFIED: `k6 run load/p95.js` on staging — p95 412ms before the fix, 198ms after (last
  week's baseline: 195ms). Handshake rate via `ss -ti` dropped ~900/min → ~40/min.
- NOT VERIFIED: production impact — staging numbers only; runnable after deploy:
  `k6 run load/p95.js -e ENV=prod`.

Ruled out, compressed: the database (slow-query log empty across the window), GC (pause
times flat under load), and route-level code (p95 doubled uniformly across ALL endpoints —
that uniformity is what pointed at the shared transport layer).

Next — nothing parked.
```

Why it passes: three hours compress into one ruled-out paragraph in which each item carries
its decisive evidence rather than its discovery story (rules 9, 10); the verdict and the
one-line fix lead (rule 1); staging vs production is split into VERIFIED / NOT VERIFIED
instead of rounded up (§1, rule 4).

## Re-grounding block skeleton (copyable)

Trigger: constants.md C8 — the user plausibly lost the thread (status question, session
resume, or first message after ~15+ tool calls since your last summary; the number is an
example, not a gate). SKILL.md rule 8. Omit sections that are empty — an empty "Blocked:"
heading is noise — but never omit Goal or Status.

```text
Goal: <one line, restated — assume it is not remembered>
Status: <Done / Partially done / Blocked / Found> — <single most important fact>

Done since your last check-in:
- <item — with concrete evidence: command + decisive output line, per CLAUDE.md §1>

In flight:
- <item — what is mid-way and what completes it>

Blocked:
- <item — exact error text, attempts, best remaining hypothesis (finishing-the-turn rules 7-8)>

Needs your decision (at most one, in finishing-the-turn rule 2's form):
**Parked question (Class B/C):** <one-sentence context>
Options: (a) <...> (b) <...>
Recommended: (<letter>) — <one-line rationale>
```
