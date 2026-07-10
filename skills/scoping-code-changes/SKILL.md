---
name: scoping-code-changes
description: Scope discipline for code changes in existing repos — a one-sentence scope contract with an always-in-scope floor, every hunk traceable to the request, gated guards and abstractions, report-don't-fix for adjacent issues, and a terminal diff audit. Use when fixing, adding, or modifying code in an existing repo — load BEFORE the first Write/Edit, and whenever tempted to refactor nearby code, add try/except or null checks, extract a helper/base class/config object, add comments, or bundle cleanup into the task diff.
---

# Scoping code changes

**Every hunk in the final diff must trace to words in the request, AND the request's
obvious mechanical completions must ship in the same turn without asking.** Those are
the twin failures this skill kills: bloat (defensive code, premature abstraction,
drive-by cleanup, rewrites) and under-delivery (leaving the asserting test red, closing
with "want me to also update the tests?"). This skill owns one curriculum-wide
artifact: the `Noticed:` line format (rule 3) — other skills reference it, never redefine it.

Escape hatch — applies to every rule below: if you believe a specific case is a
justified exception, state a one-line justification and proceed. Never skip a rule
silently.

## When to use

Load at the start of any task that writes or modifies code in an existing codebase —
bug fixes, features, endpoint/CLI additions, signature or config changes — before the
first Write/Edit, not after problems appear. Re-apply mid-task at the trigger written
on each rule: writing a guard (4), extracting anything shared (5), noticing an
unrelated issue (3), writing a comment (6), changing a signature (8), writing tests
(9), declaring done (10). Two carve-outs where the restraint rules do not apply:
greenfield scaffolding the user explicitly asked to build out, and an explicitly
requested refactor/cleanup — there the refactor IS the scope contract, and rules 1, 3,
and 10 still police its edges.

## Core rules

1. **SCOPE CONTRACT** (at task start, before the first edit). Write a one-sentence
   acceptance criterion — "the bug where getItems returns N-1 items no longer
   reproduces and existing tests pass" — as the header of the single done-checklist
   (one list: finishing-the-turn rule 5 / verifying-before-claiming rule 1, stored
   where finishing-the-turn rule 5 prescribes). Every hunk in the final diff must be
   necessary to satisfy that sentence. The ALWAYS-IN-SCOPE floor is part of the
   contract, done in the same turn WITHOUT asking: (a) the test(s) that directly
   assert the behavior you changed; (b) compile/type errors your change causes;
   (c) the single doc line that states the changed fact. Asking permission for a floor
   item is an implied-continuation offer, forbidden per finishing-the-turn rule 4. The
   floor is the anti-backfire device: "minimal" never means "incomplete"
   (diff-examples.md pair 6).

2. **CONVENTION SAMPLING** — owned by search-first-context. Sampling siblings and
   mirroring their idioms before writing new code is its rule 5 (its rule 2 covers
   files you modify); the grep proving no equivalent helper exists before you create
   one is its rule 7 — apply both as written there. Delta owned here: before ADDING a
   new dependency, scan the manifest for an already-installed equivalent and use it
   (its rule 6 checks the manifest before importing; this adds the equivalent-check
   before installing anything new).

3. **REPORT, DON'T FIX** (on noticing any issue outside the acceptance criterion —
   bug, smell, TODO, missing test, bad name). Leave its lines byte-identical and add
   one line to the final summary, exactly this format:
   `Noticed: <issue> in <file> — left untouched.`
   Park it in `WORKING_NOTES.md ## Findings` when the notes trigger applies
   (constants.md C3, CLAUDE.md §3). Both silent behaviors are failures — silent
   fixing is scope creep, silent ignoring is information loss; the Noticed line is
   the required middle path (diff-examples.md pair 5). Sole exception: the issue
   blocks the requested change — fix the minimum to unblock and say so explicitly.

4. **TRUST-BOUNDARY GUARDS** (before writing try/except, a null check, input
   validation, or a fallback value). Add it only if (a) the data crosses a trust
   boundary — user input, network, disk, env vars, external APIs — or (b) the task
   named this failure mode. Let internal invariant violations throw naturally. Never
   validate the same data at two layers. Never add branches for states the type
   system or the caller contract already excludes — a fallback there converts a loud
   bug into a silent wrong answer (diff-examples.md pair 1). In-rule valve: justified
   exception → state the one-line justification and proceed.

5. **RULE OF THREE** (before extracting a helper, base class, interface, factory,
   registry, or options/config object). Count concrete usages. Extract only at 3+
   usages (constants.md C17) or when the task explicitly
   requests the abstraction; below that, duplicate the concrete code — with no
   apologizing comment (diff-examples.md pair 2). When two designs both satisfy the
   acceptance criterion, pick the one introducing fewer new files, exports,
   parameters, dependencies, and config options — literally count each. In-rule
   valve: justified exception → state the one-line justification and proceed.

6. **WHY-ONLY COMMENTS** (before writing any comment or docstring). Comments state
   WHY — a constraint, gotcha, or spec/issue link — never WHAT the code does, never
   the change history ("changed X to Y", "NEW:", "now uses"); keep tense timeless
   (diff-examples.md pair 3). Default: match the file's comment/docstring density —
   where sibling functions have none, add none. Exception, stated inline when used:
   a genuinely non-obvious invariant deserves a why-comment even in an uncommented file.

7. **EDIT, DON'T REWRITE** (when modifying existing code). Make the smallest textual
   edit that achieves the change; never regenerate a function or file body when
   targeted edits suffice — full-body replacement silently drops edge-case handling
   and breaks git blame (diff-examples.md pair 4). No reformatting, import
   reordering, or renaming outside the lines you must change; if a formatter fights
   you, format only your lines. Carve-out: when targeted edits would leave the
   function incoherent — contradictory halves, unreachable branches — rewrite the
   smallest coherent unit and say so. A fix ships alone; a refactor you also want is
   a `Noticed:` line (rule 3).

8. **NO SHIMS IN PRIVATE CODE** (when changing a signature, name, or config format
   in a private repo/monorepo). Grep every call site (discovery per
   search-first-context rule 2) and update all of them in this diff,
   enumerate-then-exhaust style per finishing-the-turn rule 6 (full list first, n/n
   reported). No deprecated aliases, dual code paths, or compat wrappers unless the
   task states external consumers exist.

9. **TEST RIGHT-SIZING** (when writing tests for the change). Open the nearest
   existing test file first and copy its structure, fixtures, and assertion style
   (that read is search-first-context rule 5). Write the fewest tests that pin the
   changed observable behavior — typically 1–3 (constants.md C18) — selected
   per verifying-before-claiming rule 15: enumerate candidate cases
   fully, then filter; "fewest" governs what you write, never what you consider. No
   tests for behavior the change did not touch; no mirroring the implementation
   line-by-line through mock-call assertions (mocks per verifying-before-claiming
   rule 13).

10. **DIFF AUDIT** (before declaring done). Run `git diff --stat`, then `git diff` —
    `scripts/diff-audit.sh` prints both plus a noise scan. Per touched file: did the
    task require this file? Per hunk: which words of the request necessitate it?
    Revert every hunk with no answer. Strip self-introduced noise: debug prints,
    commented-out code, stray logging, unused imports, change-narration comments.
    Confirm the rule 1 floor is complete — asserting test updated, build green, doc
    line corrected. Then state completion in terms of the acceptance criterion — the
    claim, its evidence, and the VERIFIED / NOT VERIFIED / ASSUMED buckets are
    governed by CLAUDE.md §1 — and close with the `Noticed:` lines, if any.

## Quick reference

| Temptation | Rule |
|---|---|
| "Wrap this in try/except, just in case" | Trust boundary or named failure mode, else no guard — 4 |
| "Extract a base class / registry / options object" | Count usages first; below the bar, duplicate — 5 |
| "Rename/reformat this while I'm here" | Out of contract → `Noticed:` line — 3, 7 |
| "Rewriting the function is easier" | Targeted edit unless incoherent — 7 |
| "Add a comment explaining what changed" | Change narration → delete — 6 |
| "Ask whether to update the failing test / doc line" | Floor item: just do it — 1 |
| "Keep the old signature as an alias" | Update every call site — 8 |
| "Add tests for the neighboring functions too" | Only the changed behavior — 9 |

Adherence decays with context growth: when a staleness trigger (constants.md C16)
fires for a file you are editing, re-read this table and your acceptance criterion.

## Do not over-apply

- The floor outranks minimalism: a diff that leaves the asserting test red or the
  build broken fails this skill no matter how small it is.
- An explicitly requested refactor/cleanup is not scope creep — it is the contract;
  the gates then police additions beyond it, not the requested work itself.
- Do not narrate contract bookkeeping, gate decisions, or usage counts to the user
  (finishing-the-turn, "Do not over-apply") — they see the summary and `Noticed:` lines.

## Files

- `references/diff-examples.md` — six paired bad/good diffs, one per gate; read the
  matching pair when a gate fires and the call feels close.
- `scripts/diff-audit.sh [<git-diff-args>]` — read-only rule 10 helper: diff stat,
  per-file hunk counts, self-introduced-noise scan. Advisory only; always exits 0.
