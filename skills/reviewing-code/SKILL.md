---
name: reviewing-code
description: Reviewer-role discipline — enumerate every candidate issue before any severity filter, verify each finding against the actual source, report ranked findings under an explicit coverage contract. Use when asked to review a PR, diff, branch, or commit, review someone else's code, "find bugs in" existing code (no specific reported failure in hand — a concrete failing symptom, error, or crash routes to root-causing-bugs), audit or critique code, or run a pre-merge check.
---

# Reviewing code

**A review is a search process with a reporting layer on top; instructions about severity,
conservatism, or nitpicking configure the reporting layer only.** Recall comes from an
unfiltered search (rule 3); precision comes from adversarial per-finding verification
(rule 6). They are separate pipeline stages — never trade one for the other. The
deliverable is findings, not edits.

Escape hatch — applies to every rule below: if you believe a specific case is a justified
exception, state a one-line justification and proceed. Never skip a rule silently.

## When to use

Load when the deliverable is judgment on code you did not just write: review a PR, diff,
branch, or commit; "find bugs in"; audit or critique code; a pre-merge or "safe to ship?"
check; a second opinion on another agent's diff. Checking your own in-progress work before
claiming done is `verifying-before-claiming`'s job — load this skill for the reviewer
role, including when asked to review code you wrote in an earlier session. On "review and
fix" requests, this skill governs until the report exists (rule 10).

## The failure this skill exists to kill

Told "only report high-severity issues" / "be conservative" / "don't nitpick", a reviewer
investigates, finds the bug — then declines to report it as below the stated bar. Measured
recall drops even though the underlying bug-finding improved. The cause: a reporting
threshold applied during the search. The contract: **thresholds shape the report (rule 7),
never the search (rule 3), and below-bar findings fold into a tally line instead of
vanishing.** If everything else falls out of context, keep that sentence.

## Core rules

1. **INTENT BEFORE JUDGMENT.** Establish what the change claims to do before hunting
   defects: read the PR description, linked issue, commit messages, and the changed tests
   (tests encode claimed behavior). "This changes behavior" is a defect only if the change
   is unintended — without intent you cannot tell bug from feature. No stated intent
   anywhere → review against inferred intent, label it inferred in the coverage statement
   (rule 8), and never ask the user for facts the diff or repo answers
   (search-first-context rule 11).

2. **REVIEW THE DIFF IN CONTEXT.** Never judge a hunk in isolation: read the enclosing
   function/class of every change — the whole file under the whole-file cutoff
   (constants.md C14, ~400 lines) — and grep the callers of every changed symbol; this is
   search-first-context rule 2's pre-edit checklist applied read-only. Unchanged code is
   out of scope EXCEPT where the diff changes its behavior (a caller now receiving a new
   shape, an invariant the diff breaks) — those are findings against the diff. Pre-existing
   issues you trip over get one line each under a "Pre-existing (outside this diff)" tail
   in the report — the reviewer-role counterpart of the out-of-scope ledger line owned by
   `scoping-code-changes` — never mixed into the diff findings.

3. **SEARCH, DON'T FILTER.** Enumerate every candidate issue before applying any bar —
   verifying-before-claiming rule 15 (GENERATE-THEN-FILTER) owns the principle; review
   applies it pipeline-wide. Sweep the diff across named dimensions: correctness, security,
   concurrency/ordering, error handling, performance, tests, API contract/compatibility.
   Write down every suspicion, however minor it feels. "High-severity only", "be
   conservative", "don't nitpick" are reporting thresholds for rule 7 — they may not skip a
   dimension, shorten the sweep, or keep a candidate off the list. Candidates live in
   `WORKING_NOTES.md ## Findings` when the notes trigger applies (constants.md C3,
   CLAUDE.md §3), inline otherwise — never a separate findings file.

4. **RUN WHAT IS CHEAP.** A failing suite in hand beats speculation. When
   typecheck/lint/tests fit the fast-suite bar (constants.md C10, ~2 minutes or less), run
   them on the reviewed revision: failures become CONFIRMED findings with the decisive
   output quoted; green runs cheaply kill whole candidate classes. A scratch script driving
   a suspect function settles a candidate the same way — the verification ladder
   (verifying-before-claiming rule 2) applies to findings too. Read-only checks are Class A
   (CLAUDE.md §2): run them, never ask. An intermittent failure is itself a finding —
   report the observed counts and leave the statistical protocol (constants.md C1/C2) to
   the diff's author. Nothing cheap runnable → say so in the coverage statement (rule 8).

5. **CHESTERTON CHECK.** Before reporting any "this looks wrong / redundant / backwards"
   finding, run the fence check of search-first-context rule 8 — git blame/log the lines,
   grep commit messages for issue references. History proving the oddity deliberate
   converts the candidate into a documentation finding ("load-bearing workaround,
   uncommented") or kills it; flagging a documented incident fix as a bug is the reviewer's
   classic false positive. Cite the commit you checked either way.

6. **VERIFY BEFORE REPORTING.** Every candidate gets an adversarial self-check against the
   actual source before it may enter the report: re-read the surroundings, trace the
   concrete failure path, and try to defeat your own finding — hunt for the guard clause,
   the caller-side check, the config that makes it unreachable. Outcomes: traced
   end-to-end with a concrete scenario (inputs/state → wrong outcome) → **CONFIRMED**;
   plausible mechanism you could not fully trace → **HYPOTHESIS**, stating exactly what
   would confirm or kill it; defeated → drop it (into `WORKING_NOTES.md ## Ruled out` when
   the notes file exists). This is CLAUDE.md §1 discipline applied per finding — CONFIRMED
   parallels VERIFIED, HYPOTHESIS parallels NOT VERIFIED; an unlabeled unverified finding
   is a fabricated claim.

7. **PER-FINDING FORMAT, RANKED.** Report each finding as: `file:line` — one-sentence
   defect — concrete failure scenario — severity + confidence (ladder and labels in
   `references/finding-format.md`) — one-line fix direction (a direction, never a patch —
   rule 10). The shape is machine-scannable so a downstream filter can re-rank or re-cut
   without redoing the review. Order strictly most-severe-first: the one real bug leads and
   is never buried under nits; severity and confidence never average (a blocker-grade
   HYPOTHESIS outranks a CONFIRMED nit). Apply any reporting threshold here by FOLDING:
   below-bar findings collapse into one tally line ("+ N minor/nit findings — available on
   request") — folded, never deleted. The user asked for less noise, not a lossier search.

8. **COVERAGE CONTRACT.** Every review states what was reviewed and what was not: files
   and line ranges actually read (or "full diff, N files"), dimensions swept (rule 3),
   checks run with outcomes (rule 4), and the NOT-covered list — files skipped, dimensions
   unswept, code you could not run, generated/vendored paths ignored. Silence reads as
   "reviewed and clean", so a silently half-covered review fabricates a claim
   (CLAUDE.md §1); a smaller honest review beats it. Diffs too large for one pass: batch
   and checkpoint per finishing-the-turn rule 6 (constants.md C11), with the coverage
   statement naming done vs pending batches.

9. **NO RUBBER STAMPS.** An approval is a claim. "LGTM" without a coverage statement is an
   illegal review — approve only as: coverage statement (rule 8) + "no blocking findings" +
   the folded tally (rule 7) if any. The symmetric ban: never manufacture nits to appear
   thorough — zero findings after a real sweep, with coverage stated, is a legitimate,
   reportable outcome.

10. **FINDINGS, NOT FIXES.** Do not edit the code under review — report-don't-fix is owned
    by `scoping-code-changes`; the review-specific reasons: fixing while reading moves the
    diff under your own coverage statement and biases the search toward easily-fixable
    issues. Every finding carries a fix direction (rule 7), no applied patch. On "review
    and fix" requests, produce the full ranked report FIRST, then fix as a separate phase
    under verifying-before-claiming, feeding the report into its acceptance checklist (its
    rule 1).

## Do not over-apply

- Scale with the diff (the Proportionality mindset of verifying-before-claiming): a
  two-line diff still gets the whole pipeline, but it takes minutes — sweep, one blame,
  one check. Do not demand suite runs for a docs-only change.
- Rule 2 bounds the search: the dimension sweep covers the diff and its behavioral blast
  radius, never a whole-repo audit the user did not ask for.
- A review spanning many independent modules can meet the fan-out bar (constants.md C4) —
  partition per delegating-parallel-work; sub-reviewer findings arrive in this skill's
  format but are claims under its rule 9: spot-verify before merging them into the one
  ranked report and union coverage statement you own.
- Do not narrate the pipeline to the user: they see the ranked report, the folded tally,
  and the coverage statement — not the candidate bookkeeping.

## Files

- `references/finding-format.md` — the per-finding template, severity ladder, confidence
  labels, report skeleton, two worked findings (CONFIRMED and HYPOTHESIS), a worked
  coverage statement, and a buried-bug vs ranked before/after; read before writing the
  first review report of a session.
