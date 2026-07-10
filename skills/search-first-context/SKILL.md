---
name: search-first-context
description: Retrieval discipline plus context-window economy — route volatile facts to web/disk before asserting them, read whole files and grep every call site before editing, sample repo conventions before creating, price every read by purpose and bound every command's output. Use when starting any task in an existing codebase, about to state a version/price/API/CLI-flag/"latest" fact, about to edit a file not yet read, tempted to ask the user for a fact that exists on disk, about to Read a file over the C14 cutoff for triage, before running any command with unbounded output (test suite, build, install, recursive find, unlimited git log/diff), or on any low-context warning or post-compaction re-plan.
---

# Search-First Context

**Training memory is a cache with an unknown expiry date; the repo and the live web are
ground truth.** Two failure modes cost real time: asserting a stale fact, and editing
through a keyhole. The fix is mechanical, not clever — a handful of cheap lookups placed
BEFORE the first assertion or Edit. Rules 1–12 govern the gathering phase: once the
sufficiency gate (rule 10) is satisfied, stop gathering and act; the context-economy
rules (13–15) stay in force through execution.

**Escape hatch, applies to every rule below:** if you believe this case is a justified
exception, state a one-line justification and proceed. Never silently skip a rule.

## When to use

Load at the start of any task that reads, edits, or answers questions about an existing
repository — including "quick" one-line fixes, which is where keyhole edits bite hardest.
Load it mid-task the moment any of these is about to happen: stating a version, price,
release date, model name, CLI flag, or external-library API signature; creating a new
file of an established kind (test, component, route, migration, script, config);
"cleaning up" code that looks wrong or redundant; asking the user a question whose answer
might exist on disk or on the web. Skip it for greenfield scratch scripts with no
surrounding repo and for stable, timeless knowledge (algorithms, math, language
semantics). It governs the phase BEFORE the first Edit/Write and BEFORE any factual
assertion; from the first edit onward, `verifying-before-claiming` takes over — except
rules 13–15, which stay live through execution (over-cutoff Reads, unboundable command
output, low-context warnings, post-compaction re-plans).

## Core rules

1. **VOLATILE-FACT GATE.** Before stating any version number, price, API signature, CLI
   flag, model name, release date, or "current/latest" fact, route it: could it have
   changed after your training cutoff → WebSearch/WebFetch or `<tool> --version` BEFORE
   asserting; specific to this repo or machine → Read/Grep it from disk (package.json,
   lockfile, config, the actual code) BEFORE asserting; cannot verify → say so explicitly
   and date the claim to your cutoff. Never state an exact figure in these categories
   from memory alone. Stable, timeless facts need no lookup.

2. **PRE-EDIT CHECKLIST** — mandatory before the FIRST Edit that changes a symbol or
   behavior in a file: (a) Read the whole file when it is under the whole-file cutoff
   (~400 lines — constants.md C14), else the enclosing function/class plus the imports
   and exports sections; (b) Grep the exact symbol being changed
   repo-wide — `scripts/impact-scan.sh <symbol>` does (b) and (c) in one call; (c)
   classify every hit: caller / test / generated / vendored / docs; (d) open every
   non-test caller that could pass a different shape. Only then edit. Two seductive
   shortcuts, by name: editing from a grep-matched line window (misses the duplicate
   helper, the exports block, the decorator above), and stopping after the first call
   site (misses scripts/, jobs/, and the test pinning the old signature).
   Proportionality: edits that change no symbol or behavior — comment, docs, formatting —
   need no scan; scale per the Proportionality table in `verifying-before-claiming`.

3. **BREADTH-BEFORE-DEPTH.** Your first tool calls on a new repo task (~3–5 —
   constants.md C15) are wide and cheap: ls/Glob of candidate directories, Grep of the
   key domain terms, Read of README + CLAUDE.md + the manifest.
   Do not deep-read a candidate implementation file until you can name at least two
   candidate locations and state in one line why you are picking one.

4. **GREP-TRIAGE.** When a search returns multiple hits, never act on hit #1 by default.
   Enumerate all hits, discard generated/vendored/fixture paths (dist/, build/,
   node_modules/, src/gen/, *.min.*, __snapshots__, vendor/), and state which remaining
   file is authoritative and why, before opening it deeply. A file headed AUTO-GENERATED
   or DO NOT EDIT is never the edit target — fix the source or the generator.

5. **CONVENTION SAMPLING.** Before creating any new file of kind K (test, component,
   route, migration, script), open the nearest existing K in the same subtree and mirror
   its imports, aliases, naming, helpers, and framework idioms. If none is nearby, Glob
   for K repo-wide and open the most recently modified example. Never author a new-kind
   file from memory of how projects usually do it. If the repo genuinely has no example
   of K, say so — with the Glob that shows it — then use standard idioms.

6. **ENVIRONMENT-FIRST.** Manifest before import: confirm the dependency exists in
   package.json/lockfile (or pyproject/requirements.txt) and note its installed MAJOR
   version — write code for that version, not the training-era one. Scripts section
   before guessing commands: read package.json scripts (or Makefile/justfile) before
   running any test/build command. Check tsconfig/engines before version-gated syntax.

7. **RECEIPTS.** Never write "X is only used in Y", "there are no other call sites", or
   "the repo has no helper for this" unless a Grep/Glob run in THIS session shows it.
   The Layer 0 claim audit (CLAUDE.md §1) governs status claims at turn end; this rule
   extends the same evidence standard to structural claims about the codebase made
   mid-task — no tool result, phrase it as a hypothesis and verify before acting on it.

8. **CHESTERTON'S FENCE.** If code looks wrong, redundant, or inexplicable, run
   `git log --follow -p -- <file>` or `git blame -L<start>,<end> <file>` on those lines
   BEFORE changing them, and grep commit messages for issue/PR references. "do not
   remove", "workaround", and "HACK" mark load-bearing code: preserve behavior unless
   history proves it accidental, and cite the commit you checked. One git command is
   cheap insurance against reintroducing a documented race condition.

9. **FALSIFICATION READ.** After forming a hypothesis about a bug's cause and before
   writing the fix, name what would falsify the hypothesis and check it — the config
   that could override, the other branch of the conditional, the dependency's installed
   version or changelog. State in one line what you checked and what would have
   falsified it. Confirmation-only reading ships plausible-but-wrong diagnoses.

10. **SUFFICIENCY GATE (two-sided).** You have enough context when you can name the
    target file(s), every affected call site, the convention you are following, and the
    verification command. Missing one → do one more targeted read, never a question to
    the user for a disk-discoverable fact. Have all → STOP exploring and start editing;
    re-reading files you have already read is the over-gathering failure mode and is
    equally banned.

11. **SEARCH-DON'T-ASK.** If a missing fact exists on disk or on the web (a file
    location, a config value, a port number, an API shape), retrieve it yourself with
    Grep/Glob/Read/WebSearch. Questions to the user are reserved for preferences,
    credentials, and irreversible decisions — i.e. Class B/C per the Layer 0 triage
    (CLAUDE.md §2), parked per `finishing-the-turn` rule 2. Tie-breaker for the recall
    gap: if even mildly unsure whether a lookup is needed, do the lookup — a 2-second
    grep beats a wrong edit or an unnecessary question.

12. **STALENESS.** Re-read the target region before editing it again if, since your last
    read, any of these occurred: a formatter/lint hook ran, the user or another agent
    touched the repo, or many tool calls have elapsed (~20+ — constants.md C16;
    example-shaped like C8, not a gate). An Edit based on remembered file content is a
    bug waiting to happen. Which memory/notes surfaces to read at session start and what
    to write back to them: CLAUDE.md §3/§4.

## Context-window economy (rules 13–15)

The rules above mandate reads; these three price them — the same plan that fits a
Fable-scale window ends in auto-compaction on a smaller one.

13. **PURPOSE-PRICED READS.** Before Reading any file over the whole-file cutoff
    (constants.md C14, ~400 lines), name the read's purpose and pay only that price:
    (a) pre-edit read of a file you will change — depth is rule 2's (C14); economy
    never shrinks it; (b) candidate triage (does this file matter at all?) — head of
    the file (imports + first declarations) or grep hits with context, never a full
    read; a file the change will touch is an edit target under (a), never triage;
    (c) known-region lookup — Read with offset/limit around the grep hit; (d) full
    read of an over-cutoff file — confirmed edit targets only, at rule 2's
    above-cutoff depth. Under the cutoff, read whole without ceremony — sub-cutoff
    economizing is this skill's own over-application. Estimate any multi-file batch
    (file count × rough size) against the remaining window BEFORE its first file; on
    budget threat, delegate read-only surveys per `delegating-parallel-work` rule 11
    (constants.md C13 — two-sided, never on file count alone; that rule owns the
    mechanism, this one adds the estimate-first timing and one modifier: a compaction
    earlier this session lowers the delegation threshold). THE FLOOR — never shrunk
    to save context: rule 2's pre-edit depth and call-site sweep, the decisive output
    line behind any claim (CLAUDE.md §1), post-edit re-verification
    (`verifying-before-claiming` rule 7), flake statistics (constants.md C1/C2).
    A floor that does not fit the window means delegation or a parked checkpoint per
    `finishing-the-turn` rule 2 — never a thinner read, a skipped re-run, or an
    unverified claim. In doubt whether a read is floor or fat: it is floor.

14. **BOUNDED OUTPUT.** Before running any command whose output you cannot bound in
    advance — full test suites, builds, package installs, recursive find/ls, git
    log/diff without -n or path limits — attach the bound: quiet/summary flags,
    `| tail`, a grep for the decisive pattern, path arguments (recipes:
    `references/read-ladder-and-filters.md`). A valid bound preserves what the
    CLAUDE.md §1 audit needs — the decisive pass/fail line plus the counts (tests
    run, failures, skips) — and keeps `verifying-before-claiming` rule 6's trap
    signals visible; a filter that could hide "0 tests collected" or a failure count
    is invalid. On unexpected failure of a bounded run, re-run the single failing
    unit verbose — never the whole suite verbose. Never pull file contents through
    Bash (`cat`, `sed -n`) when Read with offset/limit does the job.

15. **CAPTURE ON FIRST READ; RESPOND TO PRESSURE.** While a file is open, extract
    everything this task will still need — key line numbers, exact signatures, config
    values, the decisive quote — into `WORKING_NOTES.md ## Findings` when the notes
    file exists (constants.md C3, CLAUDE.md §3), otherwise into the transcript
    decision. The re-read ban is rule 10's; capture removes the pressure to break it.
    When a rule 12 staleness trigger fires (C16), re-read only the affected region
    via offset/limit — staleness voids the edited region, not the rest of the file.
    On any context-pressure signal — a harness low-context warning, a compaction this
    session, or a rule 13 estimate overrun — do, in order, BEFORE the next planned
    action: (1) bring the notes file to resumption-accurate state
    (`managing-working-memory` rules 4–5); (2) re-price every remaining read one rung
    cheaper per rule 13, delegating what still does not fit; (3) tighten rule 14
    bounds. Never keep executing the original read plan into a shrinking window; if
    even rule 13's floor no longer fits, checkpoint and park per `finishing-the-turn`
    rule 2.

## Do not over-apply

- This checklist forces thoroughness, not information-per-read judgment — it cannot pick
  the single most informative next read for you. Compensate at the margins it can reach:
  never re-read a file already read this session unless a rule 12 staleness trigger
  fired (rule 10), and stop the moment the sufficiency gate fills.
- On very large repos, a repo-wide survey can burn your own context on low-yield reads.
  When the survey itself splits into genuinely independent workstreams at the fan-out
  bar (constants.md C4 — 3+ workstreams, each ≥ ~10 minutes), delegate it per
  `delegating-parallel-work` instead of reading everything yourself.
- Do not route stable, timeless facts through web lookups — over-searching wastes turns
  as surely as under-searching ships stale facts. The gate in rule 1 has three rows;
  use the first one.

## Files

- `references/worked-examples.md` — five good-vs-bad transcript pairs, one per trap
  (stale library API, hidden second call site, AUTO-GENERATED decoy, wrong test
  framework, deleted load-bearing workaround); read when unsure which rule fires or what
  tool call satisfies it.
- `references/read-ladder-and-filters.md` — good-vs-bad traces per rule 13 ladder rung
  plus per-tool output-bound recipes for rule 14; read before the first over-cutoff
  Read or unbounded-output command of a session.
- `scripts/impact-scan.sh <identifier> [dir]` — one-shot symbol triage: repo-wide grep
  (skipping .git, node_modules, dist, build, vendor, __pycache__), hits bucketed into
  caller / test / generated / vendored / docs with counts. Satisfies rule 2(b–c) in a
  single call; the caller bucket is a to-read list, not a to-edit list.
