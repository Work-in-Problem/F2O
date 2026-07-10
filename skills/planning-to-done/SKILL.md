---
name: planning-to-done
description: Spec-driven planning for multi-step work — extract every explicit and implied requirement into the single done-checklist before the first edit, resolve unknowns by inspection, front-load discovery and baseline runs, order items by risk, reconcile the plan after every checkoff, and close only when each requirement maps to tool-result evidence. Use BEFORE the first edit on any multi-part request, feature build, refactor, migration, or rename, on changes touching 3+ files, on long-running or autonomous runs, when resuming interrupted or compacted work, and when a request term admits 2+ materially different readings after disk/web lookups fail to settle it — reading selection (rules 9–10) is not gated out by C6 on small tasks. Skip for quick fixes per the right-sizing principle (constants.md C6).
---

# Planning to Done

**Multi-step tasks rarely fail loudly — requirements fall off silently: the trailing
items of a six-part request, the implied test update, the doc mentioned once.** This
skill keeps the whole request alive from first read to evidence-backed close: Extract →
Triage → Discover → Order → Execute-and-reconcile → Close, plus resumption. It owns
plan construction and maintenance; checklist storage, asking discipline, evidence
standards, and delegation are referenced per rule from their owners, never restated.

**Escape hatch, applies to every rule below:** if you believe this case is a justified
exception, state a one-line justification and proceed. Never silently skip a rule.

## When to use

Load BEFORE the first Edit/Write when any of these holds: the request has multiple
sentences or clauses each implying distinct work; the change touches 3+ files or spans
code + tests + docs + config; the task is a feature build, refactor, migration, rename,
or dependency upgrade; the run will be long or autonomous (the constants.md C3 scale);
or the session is resuming interrupted or compacted work — rule 8 applies even when
the plan was built in a prior session. Load mid-task the moment a second requirement
surfaces in a "quick fix". Skip when rule 1 says skip — except rules 9–10, which fire
even on gated-out tasks when a request term shows two materially different readings. Boundaries: from the first edit
onward, per-item evidence is `verifying-before-claiming`'s; how the turn may end is
`finishing-the-turn`'s; this skill is the connective tissue between them.

## Core rules

1. **RIGHT-SIZING GATE.** Constants.md C6 decides whether this pipeline runs: skip the
   ceremony when the task is completable in a handful of calls touching 1–2 files AND
   has no multi-part requirements. C6 is a principle with examples, not a number — per
   its own note, a genuinely tricky 4-call task still deserves a plan. A "quick" request
   hiding a quantifier (all/every X) is not quick — its denominator comes from
   finishing-the-turn rule 6. Applying the full pipeline to a one-line fix is this
   skill's own failure mode, not diligence. Gated out → just do the work.

2. **SPEC EXTRACTION.** Before the first Edit/Write, re-read the user's complete
   message — the actual text, not your recollection of it. Extract one checklist item
   per explicit requirement: the yield is roughly one item per sentence or clause, so
   count both and treat a large mismatch (six asks, three items) as a re-read signal.
   Then enumerate the implied items: finishing-the-turn rule 5's standing verification
   items (build/typecheck passes, tests covering touched code pass, changed behavior
   exercised end-to-end) plus the request-shaped ones — the new behavior is itself
   tested; help text/docs/changelog updated when behavior is user-facing; backwards
   compatibility preserved unless the request waives it. These items FILL the single
   done-checklist owned by finishing-the-turn rule 5 and integrated with
   verifying-before-claiming rule 1 — one list, stored where finishing-the-turn rule 5
   prescribes; a second plan list anywhere is the defect this sentence exists to
   prevent. The final item is always rule 7's closure audit. Worked extraction:
   `references/spec-extraction-example.md`.

3. **UNKNOWNS TRIAGE.** List every open question the spec leaves, then classify each.
   *Workspace-answerable* — the answer lives on disk, in a command, or on the web
   (test framework, build command, whether a helper exists, current behavior): retrieve
   it yourself per search-first-context rule 11 and feed it into rule 4's discovery
   batch. *User-blocking* — depends on preference, product intent, credentials, or
   information nowhere in the workspace: Class B/C per CLAUDE.md §2. Batch ALL
   user-blocking questions into the ONE parked block finishing-the-turn rule 2
   prescribes — the parking mechanics and placement are that rule's; this rule adds
   only the plan-time sweep, so questions surface once, up front, instead of
   drip-feeding as execution trips over them. Mark answer-dependent checklist items
   blocked-on-park; everything else proceeds. Zero user-blocking questions → start
   without commentary. Third arm: the lookups return empty but the choice stays
   Class A → rule 9's reading selection.

4. **DISCOVERY BEFORE MUTATION.** Bright-line invariant, auditable from the transcript:
   your first Edit postdates the last constraint-establishing read — every file the
   change touches, its callers and tests, and the configs that govern them (what and
   how much to read: search-first-context rules 2–3, constants.md C14/C15). Two
   additions beyond reading: (a) run the existing test/build suite BEFORE any edit and
   record the baseline verdict verbatim in the plan artifact — a post-change failure is
   uninterpretable if you cannot say whether it failed before your change; (b) issue
   independent lookups as one parallel batch, never a serial drip. The signature of a
   skipped discovery phase is the reverted Edit a grep would have prevented. When the
   constraints are known, stop gathering (search-first-context rule 10), freeze the
   plan per rule 5, and start editing.

5. **VERIFIABLE ITEMS, RISK-FIRST ORDER.** Attach to every item the observable
   completion criterion verifying-before-claiming rule 1 requires — a command plus its
   expected decisive output, a named test that must pass, a string present at a path.
   This rule adds the rewrite discipline: convert activity phrasing into outcomes —
   "handle migration" → "migration runs clean on the fixture DB"; "improve auth" →
   "login integration test passes". An item you cannot attach a criterion to is an
   unresolved unknown — send it back through rule 3. Then order: (1) spike the
   highest-uncertainty item first — the one whose failure would invalidate the most
   downstream work must fail while it is cheap; (2) topological dependency order;
   (3) any destructive or hard-to-reverse step sits AFTER a verification gate
   confirming its preconditions (the step itself is Class B — CLAUDE.md §2 governs the
   asking); (4) mechanical low-risk items — docs, changelog, comments — last, so they
   are written once, after behavior freezes. Ordering also exposes independence: when
   the ordered plan shows genuinely independent workstreams at the fan-out bar
   (constants.md C4), execution mode is `delegating-parallel-work`'s call — load it;
   this skill keeps only the plan.

6. **CHECKOFF AND RECONCILE.** After each item: verify its criterion, mark it done in
   the artifact, then re-read the REMAINING items from the artifact — never from
   memory — and answer one question: does anything just learned invalidate, weaken, or
   reorder a remaining item, or expose a done item's criterion as too weak? If yes:
   stop editing, update the plan first — rewrite the criterion, reopen the item, add or
   drop items, with a one-line note why — then resume. Never patch around an
   invalidated assumption at the current edit site: the local patch keeps this item
   green while shipping the half-migrated state the next item builds on. Mid-item
   decision forks route per CLAUDE.md §2 (Class A: decide, one Decisions-ledger line
   per finishing-the-turn rule 10, continue). Adjacent issues noticed en route are NOT
   new plan items — record them per scoping-code-changes' report-don't-fix rule and
   hold the plan's scope.

7. **GROUNDED CLOSURE.** The mandatory final item executes as: (1) re-read the user's
   ORIGINAL message — not your rule 2 extraction of it, which may itself have missed a
   requirement; anything absent from the checklist is added and handled now; (2) walk
   the checklist pairing every item with the specific tool result that proves it —
   file path, quoted decisive output line, exit status — produced after the last edit
   touching that code (CLAUDE.md §1 staleness); (3) an item without evidence is either
   done now or reported NOT VERIFIED, never claimed; (4) intermittent checks re-run per
   constants.md C1, and "fixed" on nondeterministic behavior follows C2 — "passed once"
   and "verified" are different claims (recipes: verifying-before-claiming rule 4). The
   evidence bar and buckets are CLAUDE.md §1's; the closing-message shape is
   `outcome-first-reporting`'s; the end-of-turn gates are finishing-the-turn rules 3–4.
   This rule owns only the item-by-item walk and the original-message re-read.

8. **RESUMPTION.** After any interruption, restart, context compaction, or a bare
   "continue": FIRST action, re-read the plan artifact — per CLAUDE.md §3 it lives in
   `WORKING_NOTES.md ## Plan` / `## State` when constants.md C3 applies, else the
   TodoWrite list. Never reconstruct remaining work from memory: reconstruction
   duplicates finished items and drops unfinished ones. SECOND action, diff the
   artifact against reality, because the artifact can be stale too: `git status` /
   `git diff` for actual file state, and re-run the completion criterion of the most
   recently checked-off item — an interrupted session may have died between the edit
   and its verification. Trust the artifact over memory, and reality over the artifact.
   The wider ritual — which notes sections to read, what to write back — is
   `managing-working-memory`'s post-compaction ritual; this rule owns the
   plan-vs-reality diff. Then re-enter rule 6's loop at the first unchecked item.

## Reading selection (ambiguous requests)

9. **READING SELECTION.** Trigger: a request term maps to 2+ materially different
   deliverables, rule 3's lookups (search-first-context rule 11) RETURNED and
   settled nothing, and the choice is not itself Class B/C; trivially-different
   readings are not ambiguity — pick either (constants.md C6). (1) ENUMERATE 2+
   readings as one-line "means X → deliverable looks like Y" pairs before
   evaluating any (enumerate-then-filter: verifying-before-claiming rule 15).
   (2) SELECT by precedence: (a) repo evidence (sampling: search-first-context
   rule 5; receipts: its rule 7) beats any prior about what users usually mean;
   (b) smallest wrong-guess cost — extend over rewrite; a Class B-requiring
   reading (CLAUDE.md §2) is never silently selectable; (c) tie-break: narrowest
   literal reading, then fewest new files/exports/params (scoping-code-changes
   rule 5's count). (3) DIVERGENCE TEST: silent selection is legal only while
   Class A (CLAUDE.md §2); park per finishing-the-turn rule 2 — readings AS the
   options, step 2's winner as default, reading-independent work first — when
   readings imply different public APIs or removed user-visible behavior, a wrong
   guess would junk most of the deliverable (C6-shaped), or every reading needs a
   Class B step. (4) DECLARE at selection time, never in the closing draft: the
   chosen reading becomes the scope-contract sentence (scoping-code-changes
   rule 1) — the interpreted deliverable, not the ambiguous words — plus one
   Decisions-ledger entry (mechanics: finishing-the-turn rule 10) owning:
   ambiguous phrase, chosen reading, strongest evidence fact, rejected runner-up;
   the user's veto costs one word. (5) STRUCTURE, within rule 5's order:
   reading-independent items first; reading-dependent behavior behind one seam
   narrow enough to NAME the hunks a reading-switch would revert.

10. **ONE READING IN THE CODE.** From selection to the diff audit (re-checked there —
    scoping-code-changes rule 10), the diff implements exactly the declared reading.
    No union hedge: two mechanisms shipped "to be safe" are the untraceable hunks
    scoping-code-changes rule 1 forbids. No intersection-plus-offer: the uncontested
    overlap plus "want me to do X instead?" is the implied-continuation offer
    finishing-the-turn rule 4 forbids; runner-up readings live only in rule 9's
    ledger entry or its parked options. Two events re-run rule 9's selection
    with the new evidence — never a patch around it: a second material guess existing
    only because of the first (divergence-test the COMBINED chain — chained Class A
    guesses compound into a Class C shape; a chain parks as ONE finishing-the-turn
    rule 2 block), and any tool result inconsistent with the chosen reading (a
    pinning test, doc line, config value) — ALWAYS a rule 6 reconcile; evidence is
    never bent to fit the guess (verifying-before-claiming rule 10). On a reading
    switch, update the ledger entry and contract sentence in place and sweep
    written hunks for fossils of the abandoned reading.

## Do not over-apply

- The pipeline orders work; it cannot make your risk ranking correct. When a spike
  surprises you, the ranking is off — re-rank the remainder at the next rule 6 checkpoint.
- If reconcile keeps rewriting the plan, discovery was incomplete — return to rule 4
  and close the gap; do not iterate the plan into shape one collision at a time.
- Right-sizing cuts both ways (constants.md C6): ceremony on a one-liner wastes the
  turn; but the moment a gated-out task grows a second requirement, load the pipeline.
- Do not narrate the pipeline to the user — no phase names, no reconcile bookkeeping.
  They see the plan's outcomes, the Decisions ledger, and at most one parked block.
- Rule 9 forces a second reading to exist, not to be serious: a strawman defeats it.

## Files

- `references/spec-extraction-example.md` — one full trace (8-requirement request →
  extracted checklist, unknowns-triage table, risk-first order, mid-task reconcile
  reopening a weak item) plus two reading-selection traces: fake ambiguity dissolved
  by one grep, and a genuine select-and-declare with the exact contract sentence and
  ledger line. Read when unsure how rules 2, 3, 5, 6, or 9–10 apply — not routinely.
