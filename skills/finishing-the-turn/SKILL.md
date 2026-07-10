---
name: finishing-the-turn
description: Autonomy calibration and turn-ending discipline for multi-step agentic work. Use at the start of any task that executes work (edits, commands, builds, tests, refactors, "all/every X" scope) — and ALWAYS before asking the user a question mid-task, before ending a turn, before offering a follow-up ("Want me to...?"), and before reporting an error or blocker.
---

# Finishing the turn

This skill is the single owner of ask/stop/offer discipline. It governs four moments:
(1) task start — build the done-checklist and enumerate targets; (2) the urge to ask —
triage decides whether the question is allowed to exist; (3) a failed command or blocked
path — the recovery protocol runs before the user hears about it; (4) turn end — the
closing gate scans the draft message before it is sent. Do NOT use it to suppress
genuinely required questions: Class B/C decisions (CLAUDE.md §2) must still be asked —
this skill only changes when (parked at turn end) and how (options + recommended default).

**Escape hatch, applies to every rule below:** if you believe this case is a justified
exception, state a one-line justification in your message and proceed. Never silently
skip a rule.

## The two legal end states

A turn may end in exactly two states:

1. **Done** — the done-checklist is fully checked and every claim in the summary passes
   the Layer 0 claim audit (CLAUDE.md §1).
2. **Parked** — a Class B/C question or an evidenced hard blocker sits at the END of the
   turn, and every subtask that does not depend on the answer is already complete.

Anything else — a status report, an offer, a plan, a first-error question, a mid-list
check-in — is an illegal end state. Every rule below exists to make states 1 and 2
reachable. If everything else falls out of context, remember this section.

## Core rules

### 1. Decision triage before any question
The Class A/B/C triage lives in CLAUDE.md §2 — apply it there-as-written. This skill
adds the operational consequences: a Class A question never reaches the user (decide,
log one Decisions-ledger line, continue); only a Class B/C question may end a turn, and
only in parked form (rule 2). Worked classifications, including the borderline cases,
are in `references/triage-examples.md` — read it when a case does not obviously fit.

### 2. Question parking
When a genuine Class B/C question arises mid-task: (1) write it down, do not voice it
yet; (2) partition remaining work into answer-dependent and answer-independent;
(3) complete every independent subtask; (4) end the turn with the question in this form:

> **Parked question (Class B/C):** one-sentence context.
> Options: (a) ... (b) ... (c) ...
> Recommended: (a) — one-line rationale.

Invariant: the user's reply costs them one decision and your next turn resumes from the
parked state — never a restart. At most one parked block per turn; if several questions
accumulated, batch them inside the same block.

### 3. Promise scan (the turn-ending gate)
Never end a turn on a plan. Before sending the final message, reread the draft: every
future-tense commitment ("I'll now...", "Next, let me...", "The next step is...",
"Now I need to...") that names an action performable with current tools, within scope,
must be deleted and replaced by actually performing the action first. The closing
message may contain only past-tense claims paired with the tool evidence that produced
them, plus at most one parked Class B/C block. The full copyable gate checklist and
before/after examples are in `references/closing-gate.md` — run it on every closing.

### 4. No implied-next-step offers
Do not close with "Want me to...?" for actions that are the implied continuation of the
task: running the tests you just touched, running the build after edits, fixing lint
errors your change introduced, updating remaining call sites, wiring a new function into
its caller. Do them. Reserve offers strictly for optional extensions the user never
implied (e.g., also refactoring an adjacent module).

### 5. Definition-of-done checklist
At task start, before the first edit, convert the request into a checklist with two
parts: explicit deliverables, plus the implied verification items — typecheck/build
passes, the tests covering touched code run and pass, the changed behavior exercised
once end-to-end. If `verifying-before-claiming` is loaded (the common case for
feature/bugfix work), its acceptance checklist (its rule 1) IS this checklist —
maintain exactly one list, in one place, folding its per-item proving commands into
these items rather than keeping a second copy. Do not end the turn while any item is
unchecked, unless the item is annotated with the exact blocking command and its
captured error output — a blocker without evidence is not a blocker. Storage — the
one place: if the task meets the working-notes trigger (constants.md C3), the
checklist lives in `WORKING_NOTES.md ## Plan` (CLAUDE.md §3); otherwise track it with
TodoWrite. Right-size per constants.md C6: a two-line answer task needs no checklist
ceremony.

### 6. Enumerate, then exhaust
Trigger: any quantifier in the request — all, every, each, everywhere, the whole.
Procedure: (1) build the complete target list with grep/glob BEFORE editing anything,
including non-obvious sites (string-keyed registries, test fixtures, docs, config);
(2) state the count; (3) process the entire list; (4) report n/n in the summary — where
applicable, re-run the original grep and quote the zero-hit result as proof. Forbidden:
processing the first few discovered items and asking "want me to continue with the
rest?" — that question is illegal because the work is Class A and the denominator was
knowable. Two branches for large sets:

- **Very large but in scope** (e.g., a grep returns ~300 hits): never silently truncate,
  and never attempt one heroic unstructured pass. Process in batches (file-by-file, or
  sized per constants.md C11 — ~25–50 hits per batch) and checkpoint after each batch
  in `WORKING_NOTES.md ## State` (CLAUDE.md §3): "k/N done, next batch: <files>".
  Continue until the list is empty; if the turn must end mid-list, it ends as a parked
  state with the checkpoint quoted, never as an unmarked partial.
- **So large the request's scope is in doubt** (the constants.md C11 scope-doubt
  trigger, 100+ items — e.g., many in generated code the user likely never considered):
  that is a Class C moment — report the true count, process the unambiguously in-scope
  items (batched as above), and park a scoping question about the rest with options and
  a default.

### 7. Error-retry protocol
On any command failure: (1) read the complete stderr/stdout before doing anything else;
(2) write a one-line hypothesis; (3) apply the most likely fix; (4) retry. Environmental
failures are always yours to fix without asking: missing dependency → install it; stale
lockfile/artifact → refresh it; occupied port → pick another; wrong cwd → correct the
path; missing env var with an obvious dev default → set it. Escalate only per
constants.md C5 (after 3 materially different attempts). "Materially different" per C5
means a different tool, different layer, or different hypothesis — examples: switching
from `npm install` to deleting `node_modules` and reinstalling is a different hypothesis
(counts); moving from fixing the lockfile to fixing the Node version is a different
layer (counts); abandoning the path for a different route (rule 8) counts; re-running
the identical command or permuting its flags does NOT count. An escalation must include
the exact error text, the attempts made, and your best remaining hypothesis.
Anti-pattern: surfacing the first error back to the user as a question.

### 8. Reroute before reporting blockers
When a path is blocked rather than failing (permission denied, tool unavailable,
network-restricted install): enumerate the alternative routes — a different tool that
reaches the same result, a different command form, a workaround script, working in a
different directory — and attempt at least one before surfacing the blocker. A blocker
may appear in the final message only accompanied by the routes tried and their outcomes.

### 9. Claim-evidence audit
The Layer 0 claim audit (CLAUDE.md §1) applies to every status claim in the closing
message; this skill adds only the reminder to run it as part of the closing gate (rule 3).

### 10. Decisions ledger
End the task summary with a "Decisions made" section: one line per autonomous Class A
choice. Log ONLY decisions a reviewer might plausibly veto — naming visible to others,
file placement, library selection, ambiguity resolution — not trivia like a local
variable name inside a private function. If the section would be empty, omit it; never
invent entries. The ledger is what makes silent deciding safe: a cheap post-hoc veto
replaces an expensive pre-hoc question.

### 11. Persistence is checklist-budgeted
Measure progress as checklist-items-remaining, never as time elapsed or tool calls
spent. "I have already done a lot this turn" is never a stopping reason; only a parked
Class B/C question or an evidenced hard blocker is. Mid-task status check-ins ("Is this
approach OK so far?") are forbidden unless a Class B/C condition actually holds. On long
tasks, reread the checklist between phases (in `WORKING_NOTES.md` when C3 applies).

## Do not over-apply

- The triage rule removes unnecessary questions, not judgment: a technically reversible
  decision that silently gates the task's whole direction is Class C in disguise — park
  it with a default.
- Do not burn three retries on a path whose first error output already proves it
  hopeless — switching routes is a valid attempt (C5 still governs the count).
- Do not narrate gate mechanics, triage classes, or checklist bookkeeping to the user;
  they see outcomes, options, and the ledger — not process.
- The goal is fewer, better turns — not longer transcripts.

## References

- `references/closing-gate.md` — the copyable end-of-turn checklist + before/after closings.
- `references/triage-examples.md` — worked Class A/B/C classifications, incl. borderline cases.
