---
name: verifying-before-claiming
description: Evidence-first verification for code changes — reproduce bugs before fixing, drive the changed behavior for real, re-verify after every edit. Use when implementing a feature, fixing a bug, handling a failing or flaky test, or before sending any message saying done, fixed, works, passes, or verified.
---

# Verifying Before Claiming

**A claim without a matching tool result from this session is a fabrication, even if it
happens to be true.** The Layer 0 claim audit (CLAUDE.md §1) is the final gate on what you
may say; this skill governs how the evidence behind it gets produced.

Escape hatch — applies to every rule below: if you believe a specific case is a justified
exception, state a one-line justification and proceed. Never skip a rule silently.

## When to use

Load at the start of any task that modifies product source (application code, libraries,
config that affects runtime): features, bug fixes, refactors, migrations. It governs
planning (acceptance checklist before the first edit), execution (red/green, fresh state),
and completion (producing the evidence the CLAUDE.md §1 summary requires). Escalate rigor
for flaky failures, multi-part specs, shared code with many importers, and data-touching
changes. Before applying heavy rules to a small diff, check the Proportionality table.

## Core rules

1. **ACCEPTANCE CHECKLIST.** Before your first edit, convert the request into a numbered
   checklist of acceptance criteria, including obvious implied items (help
   text, error messages, docs the spec mentions). If `finishing-the-turn` is loaded (the
   common case for feature/bugfix work), its definition-of-done checklist (its rule 5)
   IS this checklist — maintain exactly one list, stored where its rule 5 prescribes;
   this rule only adds the acceptance-criteria content and per-item evidence. Otherwise
   track it in TodoWrite. For each item, pre-declare the command
   or observation that will prove it. Mark an item complete only when that evidence exists
   as a tool result in this session. Re-read the checklist before the final summary — this
   catches the "shipped 2 of 5 requirements, declared done" failure.

2. **VERIFICATION LADDER.** typecheck < unit test < integration test < driving the real
   flow. When a change alters runtime behavior, verify at least once at the top rung
   before claiming completion: endpoint → curl with a real payload; CLI → run with real
   args; UI → load the page and interact; library → run a consumer test or a scratch
   script that imports it. If no harness exists, build the minimal one first. Typecheck,
   lint, or build success proves the code compiles — it is never evidence that behavior is
   correct. Changes with no behavioral surface (comments, docs, formatting, compiler-
   checked renames) do not require the top rung; pick the proportionate rung instead.

3. **RED/GREEN FOR BUGS.** Before editing, run a concrete command that demonstrates the
   reported failure and observe it fail. After the fix, re-run the exact same command and
   observe it pass, then state the causal mechanism linking your diff to the failure. If
   the reproduction is a new test, watch it fail on the intended assertion first — failure
   via ImportError or a fixture error means the test is broken, and a test never seen red
   is zero evidence. If you cannot reproduce the bug, label the change "speculative fix,
   unverified" and say what would confirm it — reserve "fixed" for red-then-green.

4. **FLAKE RULE.** Triggers: the failure was intermittent; the outcome differed between
   any two runs; time/sleep/ports/network/randomness/ordering/parallelism is anywhere
   near the diff; or a test went green first-try after your change with no stated
   mechanism. Then one green run is evidence of nothing — re-run per constants.md C1
   (10 consecutive runs; 30 when the observed failure rate is under ~20%), using
   `scripts/repeat-run.sh` or the runner-native flags in `references/flake-recipes.md`.
   Claiming "fixed" for a nondeterministic bug requires the constants.md C2 protocol
   (report "pre-fix k/N failures, post-fix 0/M"). Also require a stated causal mechanism
   connecting the diff to the failure mode — no mechanism, keep investigating.

5. **FRESH STATE.** Before any end-to-end check, restart or rebuild whatever serves the
   code and confirm the new code actually loaded — a new startup log line, a version
   marker, or behavior that observably differs from the old build. An observation made
   against a stale process verifies nothing.

6. **READ THE OUTPUT.** CLAUDE.md §1 defines what counts as affirmative output (tests
   ran > 0, failures == 0, expected value present; exit 0 alone proves nothing). This
   skill adds: quote the decisive output line whenever you claim success, and scan every
   green run against the trap catalog in `references/output-traps.md` (0 collected,
   all-skipped, empty glob, exit-0 curl on HTTP 500, stale hot-reload, wrong env banner,
   implausibly fast run).

7. **RE-VERIFY AFTER EVERY EDIT.** CLAUDE.md §1 already voids prior passing checks on
   edit. Operational corollary: the final tool call before your summary must be a passing
   verification of the final code state — never an edit. The classic trap is the late
   "small cleanup" or second fix applied after the green run.

8. **BLAST RADIUS.** After changing file X, grep for files that import X and run their
   tests too; if the full suite meets the fast-suite bar (constants.md C10, ~2 minutes
   or less), run all of it. Exercise at least one non-happy-path case (empty input,
   error branch, boundary value) beyond the behavior you just wrote.

9. **NEVER ASK TO VERIFY.** Tests, typechecks, builds, read-only commands, and local dev
   servers are Class A per the Layer 0 autonomy triage (CLAUDE.md §2): run them, never
   offer. "Want me to run the tests?" must not appear — run the check, then end the turn.

10. **TEST INTEGRITY.** Never change a test expectation to make it pass unless you can
    quote the spec/issue/docs line proving the test was wrong — and include that quote
    with the change. A mock that makes an assertion tautological counts as changing the
    expectation. Default presumption: the test encodes intent; your code is the suspect.

11. **BLOCKED VERIFICATION.** A check that fails for environmental reasons (missing dep,
    wrong cwd, occupied port, missing creds) makes the environment part of the job:
    repair it, following finishing-the-turn's error-retry protocol (escalation per
    constants.md C5). If still blocked, report the item as NOT VERIFIED per CLAUDE.md §1
    — the blocker plus the exact command the user can run. There is no banned-word list:
    the claim audit handles the substance, and an unverified claim stays in the
    NOT VERIFIED bucket whatever its phrasing.

## Test design

12. **PARTITION BEFORE TESTS** — scoped to creating a new test suite or covering a
    nontrivial input space (several input dimensions, parsing, boundary-heavy logic).
    Before writing test code, write the partition table in plain text: each input
    dimension, its valid/invalid equivalence classes, and boundary values (empty / zero /
    one / exact boundary / ±1 / max / malformed / unicode / duplicates / concurrent).
    Write at least one test per class, plus one adversarial test annotated with the
    specific bug it would catch. Adding a single regression assertion to an existing
    suite needs no table.

13. **MOCK BUDGET** — mock only at process or network boundaries you do not control. If
    every assertion in a test inspects mock call arguments, add or convert at least one
    test that asserts on real observable output (returned value, file contents, emitted
    bytes, DB state).

14. **EVAL DISCIPLINE** — when asked to measure whether a change helps: (1) fix the
    metric and pass threshold in writing before running anything; (2) run the baseline
    at least N times per constants.md C9 (N = 5 per arm), logging every result in
    `WORKING_NOTES.md ## Experiments` when the notes trigger applies (CLAUDE.md §3,
    constants.md C3), otherwise inline in the transcript — never a separate results
    file; (3) change exactly one variable; (4) run the treatment the same N (per C9)
    under identical conditions; (5) report mean and min–max spread for both
    arms; (6) a delta smaller than the run-to-run spread is "no measurable difference" —
    never an improvement. An eval that cannot output "no effect" is not an eval.

15. **GENERATE-THEN-FILTER** — when told to be minimal, conservative, or
    high-severity-only in tests or findings: first enumerate the complete candidate list
    (all edge cases, all suspected issues), then apply the filter to decide what to write
    or report. The filter governs output, never generation — letting it truncate
    generation measurably drops recall.

## Proportionality

Verification scales with the diff. Under-verification ships fabricated claims;
over-verification (restarting a server to check a comment typo) is pure cost.

| Change | Proportionate verification |
|---|---|
| Comment / docs / formatting only | nothing beyond lint or build — no restart, no suite |
| Isolated pure function | unit tests + one edge case |
| Shared module with many importers | importer tests + fast full suite (rule 8) |
| Endpoint / CLI / UI behavior | full ladder including real-flow drive (rule 2) |
| Migration / deletion / concurrency / data-touching | ladder + before/after counts, idempotency re-run, rollback check |

## Files

- `references/summary-template.md` — worked VERIFIED / NOT VERIFIED / ASSUMED summaries;
  read before writing the final summary on any multi-part task.
- `references/flake-recipes.md` — per-runner repeat invocations and when repeating is
  required vs optional; read when rule 4 triggers.
- `references/output-traps.md` — catalog of passing-looking failures; read when a green
  run feels too easy, and before quoting output in a VERIFIED entry.
- `scripts/repeat-run.sh N -- <command>` — runs the command N times, prints a pass/fail
  tally and the first failing output; default N per constants.md C1.
