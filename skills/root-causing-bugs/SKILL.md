---
name: root-causing-bugs
description: Hypothesis-driven debugging loop — repro-first gate, falsifiable hypothesis ledger, one-variable discriminating experiments, statistical flake handling, history bisection, upstream root-cause tracing. Use when investigating any bug, crash, failing or flaky test, race condition, or regression — a reported symptom, error, or failing run exists (symptomless "find bugs in this code" routes to reviewing-code); when the report says "sometimes", "intermittent", "only in CI", "works on my machine", or "used to work"; or when the tempting fix is a null-guard, retry, sleep, or widened timeout.
---

# Root-causing bugs

**Debugging is hypothesis elimination, not code reading.** The three failures this skill
exists to prevent: theorizing before reproducing; declaring a flaky bug fixed after one
clean run; patching where the bug was detected instead of where it was caused. The loop:
Reproduce → Classify & baseline → Ledger → Discriminating experiments → Root cause →
Statistical verification → Audited report. This skill is the elaborating owner of the
flake-statistics protocol (constants.md C1/C2); `verifying-before-claiming` rule 4 is
its verification-side consumer.

Escape hatch — applies to every rule below: if you believe a specific case is a
justified exception, state a one-line justification and proceed. Never skip a rule
silently.

## When to use

Load when the task is diagnosing why something is broken, rather than building something
new: an error, crash, wrong output, failing or flaky test, race, performance regression,
or a "can't reproduce" report. Skip it when the fix is spelled out in the tool output
(missing import, lint autofix, type error with a fix-it) — but the moment that "obvious"
fix fails once, the bug is no longer trivial: load this skill and start at rule 1.
Division of labor: this skill governs the diagnosis loop between red and green;
`verifying-before-claiming` governs the evidence behind any claim (its rule 3 red/green
runs on the same repro command rule 1 builds). The ledger and experiment log live in
`WORKING_NOTES.md ## Experiments` and `## Ruled out` per CLAUDE.md §3 (one file — never
DEBUG_NOTES.md), elaborated by `managing-working-memory`; below the notes trigger
(constants.md C3), keep the same structures inline in the transcript.

## Core rules

1. **REPRO GATE (blocking).** Before proposing any cause or editing any source file,
   produce ONE command that fails with the user's exact symptom, run it, and quote the
   failing output. Catching yourself reading code to build a theory before this command
   exists means stop and build the repro. Symptom-equivalence check: the repro's failure
   must match the user's verbatim report — same error type, message shape, and
   conditions; a nearby-but-different failure means you are about to fix the wrong bug.
   If you cannot make it fail after materially different attempts (escalation count per
   constants.md C5), ship NO speculative fix: report reproduction as NOT VERIFIED per
   CLAUDE.md §1 with the attempts listed, and park a request for ONE specific artifact
   (log, HAR, core dump, env values, prod config) per `finishing-the-turn` rule 2.
   "This should fix it" next to a source edit is the named anti-pattern.

2. **CLASSIFY DETERMINISM, MEASURE THE BASELINE.** Classify the bug nondeterministic if
   ANY hold: the report says sometimes / intermittent / flaky / randomly / only-in-CI /
   works-on-my-machine; the implicated path touches time, randomness, parallelism,
   network, retries, or async ordering; or two repro runs disagree. On classification,
   BEFORE changing anything, loop the repro per constants.md C1 (10 consecutive runs;
   30 when the observed failure rate is under ~20%) using `verifying-before-claiming`'s
   `scripts/repeat-run.sh`, and record "baseline: k/N failures" in `## Experiments`.
   Every later claim is measured against this number. Deterministic bug → the single
   quoted red run is the baseline.

3. **AMPLIFY LOW RATES BEFORE HYPOTHESIZING.** If the baseline rate is below C1's
   low-rate boundary, do not start theorizing — raise the rate first: bigger loop
   (sized by the C2 math — `references/flaky-and-bisect.md`), parallel runs, CPU
   stress, sleep injection in suspected race windows, clock pinning, RNG seeding. The
   goal at this stage is a HIGHER reproduction rate, not a clean run. Which amplifier
   moved the rate is itself ledger evidence — a rate that jumps under parallelism
   implicates shared state.

4. **HYPOTHESIS LEDGER.** Before the first probe, write falsifiable candidate causes in
   `## Experiments`: `| # | Hypothesis | Layer | Prediction if true | Cheapest
   discriminating test |`. Consider at least three distinct layers when generating —
   input data / state-ordering / concurrency / config-env / dependency version / logic —
   but write only rows you genuinely hold: padding the table to hit a row count is the
   failure mode, and a one-row ledger is legal when the layer is obvious. Falsifiability
   test per row: it must complete "if this is the cause, then <action> will <observable
   result>"; a row that cannot is a vibe — sharpen it or discard it. Show the ledger in
   your response before the first probe (do not block for a reply). Every subsequent
   probe names the row(s) it discriminates. A killed row moves to `## Ruled out` with
   the evidence that killed it; never re-run a recorded experiment except to probe
   determinism itself.

5. **ELIMINATION POWER, ONE VARIABLE.** The next experiment is the cheapest one whose
   possible outcomes EACH rule out at least one live row — never the probe most likely
   to confirm the front-runner. Logging the already-known-bad value at the crash site is
   confirmation theater; a discriminating log sits at the boundary between two rows'
   territories. Change exactly ONE variable per experiment; a pending edit that bundles
   fix + refactor + logging is split into separate runs. Update the ledger with the
   result before choosing the next probe.

6. **BISECTION TRIGGER.** If a known-good past state exists ("used to work", "since
   upgrading", a version, tag, date, or green CI run), do NOT read diffs and speculate:
   wrap the repro in an exit-code script and run `git bisect run` (copy-paste recipe in
   `references/flaky-and-bisect.md`). Flaky bug → the verdict script loops per
   constants.md C1; a single-run verdict mislabels commits and poisons the whole bisect.
   History not bisectable (squashed, rebased, unbuildable range) → `git log -S<symbol>
   --since=<known-good>` on symbols taken from the failing trace, before any manual
   code reading. Data-dependent failure → delta-debug the input down to a payload where
   every remaining element is load-bearing (loop in the same reference).

7. **UPSTREAM WALK (anti-symptom-fix).** The crash site is where the bug was DETECTED,
   not where it was caused. Trace the bad value/state upstream hop by hop to the first
   frame where an invariant was violated by code you control; the fix belongs there.
   RED-FLAG LIST — if your proposed fix is an added null/undefined guard, a broadened
   try/catch, a retry, a sleep, a widened timeout, a test skip, or marking a test
   flaky: either justify in one sentence why the detection site IS the violation site,
   or keep walking upstream.

8. **MECHANISM COMPLETENESS.** Before writing "root cause", write the causal chain as
   one paragraph: trigger → propagation → observed symptom. Check it against every
   recorded observation: does it explain why the failure is intermittent? why only in
   environment X? why onset when it began? Each unexplained observation sends you back
   to the ledger. A revert or flag-toggle that makes the symptom vanish is correlation —
   you have the root cause only when the mechanism is stated. This paragraph is the
   root-cause entry the final summary carries (summary template owned by
   `outcome-first-reporting`).

9. **STATISTICAL FIXED-CLAIM.** For a nondeterministic bug, write "fixed" only under
   the constants.md C2 protocol: post-fix failures = 0 across
   M = max(20, min(100, ceil(3 / baseline-failure-rate))) runs, reported as "pre-fix
   k/N failures, post-fix 0/M". One clean run is NEVER evidence for a flaky bug — with
   only one, write "insufficient evidence". When M is impractical (the cap engaged at a
   very low rate, or each run is expensive), the verdict is "high confidence, not
   proven" per C2 — never "fixed"; prefer re-measuring under an amplified harness
   (rule 3) so a computable M exists. Run-count math table with a worked example:
   `references/flaky-and-bisect.md`.

10. **FIX-REVERT-REFIX (conditional).** Triggers: the bug is nondeterministic, the
    repro harness may be stateful, or the run went green without a stated mechanism.
    Sequence: after green — revert the fix, re-run (looped per C1 when flaky), confirm
    red; re-apply, re-run, confirm green. If reverting does NOT bring the bug back,
    your change is not what altered the outcome: find what did (stateful harness,
    cache, environment drift) before claiming anything. SKIP when the fix's mechanism
    is directly observable in the diff (a typo'd variable name, an inverted comparison)
    AND the bug is deterministic — state the skip in one line via the escape hatch.

11. **INSTRUMENTATION HYGIENE.** Tag every temporary log `[DBG-<id>] H<n>:` naming the
    ledger row it discriminates. Prefer one debugger/REPL inspection over ten logs;
    never log-everything-and-grep. Before finishing: grep the tag and remove every
    instance, then re-run the ORIGINAL un-minimized repro — the user's symptom command,
    not your minimized harness — because cleanup is an edit and voids earlier greens
    (CLAUDE.md §1). Instrumentation that changes the failure rate is evidence, not an
    obstacle: heisenbug protocol in `references/flaky-and-bisect.md`.

12. **AUTONOMY, CLAIMS, SECONDARY FINDINGS — by reference.** The next ledger-determined
    probe is Class A per CLAUDE.md §2: run it without asking, narrating at most one
    line naming the row it discriminates; questions and blockers follow
    `finishing-the-turn` (parking rule 2, error-retry rule 7). Every "reproduces /
    fixed / passes / stable / flaky" in the final message goes through the CLAUDE.md §1
    buckets. A real defect found that is NOT the reported bug: record it in
    `## Findings` and surface it via the out-of-scope ledger line owned by
    `scoping-code-changes` — never silently drop it.

## Do not over-apply

- The full loop is for bugs whose cause is not in the error message. A traceback that
  names the fix needs rule 1's red run and a green re-run, not a ledger.
- Deterministic red → mechanism-stated fix → deterministic green needs no repeat loops:
  the statistical machinery (rules 2/3/9/10) prices in only on rule 2's triggers.
- Rule 8 passing is the stop signal for diagnosis — do not keep probing a fully
  explained mechanism, and do not pad the ledger to look thorough.
- Performance bugs run the same loop with measurements as the repro: no baseline
  number, no "optimized" claim — measurement discipline per `verifying-before-claiming`
  rule 14.

## Files

- `references/flaky-and-bisect.md` — C2 run-count math with a worked example,
  amplification recipes per runner, heisenbug caveats, copy-paste `git bisect run`
  skeleton (exit 0/1/125), `git log -S`/`-G` usage, delta-debugging loop. Read when
  rule 2 classifies the bug nondeterministic or rule 6 fires.
- Repeat-loop tool: `verifying-before-claiming`'s `scripts/repeat-run.sh N -- <cmd>` —
  use it; never write another repeat script. Per-runner plain repeat invocations live
  in that skill's `references/flake-recipes.md`.
