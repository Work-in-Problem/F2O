---
name: managing-working-memory
description: File-based working notes and durable memory — sweep memory surfaces at session start, keep the one WORKING_NOTES.md on long tasks, recover after context compaction, harvest lessons at task end. Use at the start of every session (memory sweep before the first substantive action), on long or multi-session tasks, immediately after any context compaction, when resuming or continuing earlier work, and when the user says continue later, overnight, keep going, or long-running.
---

# Managing working memory

**The context window is lossy — compaction rewrites history and sessions end mid-thought;
files are the only store that survives.** CLAUDE.md §3 declares the single notes file;
this skill governs how the two memory surfaces get used well: when to read, when to
write, and how to make every line resumable. `WORKING_NOTES.md` holds this task's state;
the durable memory surface (MEMORY.md, `.claude/memory/`, or the project CLAUDE.md —
whichever the workspace already uses) holds lessons that outlive the session.

Escape hatch — applies to every rule below: if you believe a specific case is a justified
exception, state a one-line justification and proceed. Never skip a rule silently.

## When to use

Two activation layers. Layer 1, every session: run the memory sweep (rule 1) before the
first substantive tool call, even on small tasks — an unread existing memory surface is
the cheapest failure there is. Layer 2, conditional: the notes-file discipline (rules
2–6, 11, 14) activates when the task meets the working-notes trigger (constants.md C3: long,
multi-component, or explicitly long-running / multi-session work) or the user signals
long-horizon work ("overnight", "keep going", "continue later", "resume"). Hard triggers
regardless of task size: after any context compaction, or when unsure whether earlier
work actually happened → rule 10; about to run a destructive step with a notes file live
→ rule 4's write-ahead; task end with a notes file present → rule 12 harvest.

## Core rules

1. **MEMORY SWEEP.** At session start, before the first substantive tool call, check in
   fixed order: `./CLAUDE.md`, `./MEMORY.md`, `./.claude/memory/`, `./notes/`, plus any
   file the prompt names. Read what exists — this fits inside the breadth-first opening
   window (constants.md C15) — and restate the entries that constrain THIS task, one
   line each, as active constraints before planning. Skipping an existing memory surface
   is an error, not a judgment call. An entry contradicting visible repo state is
   neither obeyed nor dropped silently: mark it and verify per rule 9. A memory entry
   that disagrees with constants.md loses — the table wins (CLAUDE.md §4).

2. **ONE FILE — THE §3 FILE.** Evaluate the notes trigger once at task start
   (constants.md C3 — plausibly exceeds ~25 tool calls, spans components/repos, or is
   explicitly long-running / multi-session). When it fires, create `WORKING_NOTES.md`
   immediately, not after the mess: repo root for multi-session work, the session
   scratchpad directory otherwise. Never create PROGRESS.md, DEBUG_NOTES.md, TODO.md,
   delegation-log.md, or any other parallel journal (CLAUDE.md §3) — the other skills
   already route into §3 sections: done-checklist and batch checkpoints → `## Plan` /
   `## State` (finishing-the-turn rules 5–6); eval logs → `## Experiments`
   (verifying-before-claiming rule 14); fan-out records → `## Delegation`
   (delegating-parallel-work rule 12). A stray parallel journal found mid-task gets
   merged in and deleted.

3. **SECTIONS ON DEMAND.** The §3 section set is a menu, not a form: sections you don't
   need stay absent. Open with `## Goal` (the ask verbatim, the done-condition, swept
   constraints), `## Plan`, and `## State`; add `## Findings`, `## Ruled out`,
   `## Experiments`, `## Delegation`, `## Lessons` only when content exists for them.
   A dutifully empty section is noise that buries the line the next reader needs.

4. **CHECKPOINT ON EVENTS, NOT COUNTS.** Write to the notes file at exactly these
   events: (a) a plan item completes or a phase boundary passes (hypothesis settled,
   module done, fan-out merged) → tick `## Plan`, refresh `## State`; (b) a result
   surprises — failing test, contradicted assumption, unexpected output → one line in
   `## Findings` or `## Ruled out`; (c) WRITE-AHEAD: before any long, destructive, or
   irreversible step (Class B territory per CLAUDE.md §2) → record intent plus recovery
   route in `## State` FIRST, then run it, so a crash mid-step is resumable from the
   file. No call-count cadence — never meter writes by tool calls. Update by Editing
   sections in place to current state; never append a "then I tried..." narrative log.

5. **STRANGER TEST.** Every note must let a fresh session with zero conversational
   context resume from the file alone: absolute paths, exact commands with flags and
   cwd, a status tag per item (DONE / DOING / NEXT / BLOCKED + why), one-line rationale
   per decision. A line that fails the test gets rewritten before you move on. Worked
   mid-debugging example: `references/notes-and-lessons.md`.

6. **TWO SURFACES, ONE-WAY FLOW.** Session scratch — current hypothesis, step state,
   intermediate values — lives ONLY in WORKING_NOTES.md, never in CLAUDE.md or the
   memory surface. Durable cross-session lessons — env quirks, required flags,
   invariants — live ONLY on the durable surface, never solely in scratch that gets
   wiped. Content crosses in one direction, scratch → durable, at harvest time
   (rule 12), rewritten into lesson form (rule 7) on the way through.

7. **LESSON FORMAT.** Every durable entry reads
   `[YYYY-MM-DD] When <trigger>, do <action> because <evidence>` — action as the exact
   command where one exists. Never a bare observation ("the build failed"); record the
   rule that prevents recurrence. Six bad→good rewrites:
   `references/notes-and-lessons.md`.

8. **UPDATE-BEFORE-APPEND.** Before writing any durable entry, grep the memory surface
   for two or three keywords from it. Related entry found → Edit it in place: correct
   it, date the revision, mark the displaced fact `superseded YYYY-MM-DD`. Append only
   when grep finds nothing related. Two live contradictory entries about one fact is a
   corrupted memory file.

9. **VERIFY-BEFORE-TRUST.** A memory entry is a dated hypothesis, not gospel. When one
   drives a concrete decision — a port, a path, a flag, "X is broken" — spend one cheap
   tool call confirming it against current reality before acting on it (the same
   route-to-disk discipline as search-first-context rule 1, with memory as the stale
   cache). Reality contradicts memory → fix the entry in the same turn via rule 8, not
   "later".

10. **POST-COMPACTION RITUAL.** After any context compaction — and whenever unsure
    whether you already did something — do NOT trust the compaction summary or your
    recollection. In order: (1) re-read WORKING_NOTES.md — it, not the summary, is the
    task-state source of truth; (2) audit claimed progress against ground truth:
    `git status` / `git diff` for edits, `ls` for created files, a targeted test run
    for anything claimed fixed; (3) only then continue from `## State`. Progress claims
    after compaction fall under the CLAUDE.md §1 claim audit like any others — matching
    tool result from this session, or NOT VERIFIED.

11. **RULED-OUT LEDGER.** The moment evidence falsifies a hypothesis, add it to
    `## Ruled out`: the hypothesis, the killing evidence, and the exact command that
    produced it. Before testing any new hypothesis, scan the ledger — a listed
    hypothesis is never re-diagnosed. This is compaction insurance: deep into a long
    debug, the ledger is what stands between you and re-running a slow diagnostic whose
    answer you already own.

12. **HARVEST AT BOUNDARIES.** At task end — BEFORE the final summary — and at natural
    phase boundaries of long runs (a debugging arc closes, a migration lands, a fan-out
    merges), read `## Lessons` and promote what generalizes to the durable surface,
    applying rules 7 and 8. Altitude test: would this entry fire on a future task that
    is not this one? Task-specific residue stays behind. Then mark the notes file
    COMPLETE or leave `## State` resumption-accurate. Harvest at boundaries, never by
    call count.

13. **SIZE BUDGET.** When the durable memory surface exceeds the consolidation budget
    (constants.md C7, ~150 lines), run the consolidation pass BEFORE appending anything:
    merge duplicates onto the newest date, delete superseded entries, keep
    trigger→action form. Procedure with before/after: `references/notes-and-lessons.md`.
    The surface must stay readable in one Read call — memory that costs more to read
    than it saves is net-negative.

14. **DISTILL AND DROP.** Corollary of rule 4: a checkpoint write is a distillation,
    not a copy. (a) Once a phase's conclusions are written into the §3 file, treat
    that phase's raw transcript as expendable — compaction may take it at any time,
    and the compaction summary is NEVER the distillation (rule 10 re-reads the file,
    not the summary). (b) Each distilled line records path + line anchor + the one
    decisive output line + the exact command that regenerates the rest — never
    pasted file bodies, diffs, or whole logs (capture timing on first read is
    search-first-context rule 15's). A note that needs the transcript to be
    intelligible fails rule 5's stranger test. Worked before/after:
    `references/notes-and-lessons.md`.

## Do not over-apply

- Below the C3 trigger, skip the notes ceremony entirely — a two-edit task gets no notes
  file. The rule 1 sweep still runs; it costs a few Reads.
- Over-logging is the mirror failure: writes outside rule 4's events burn tokens and
  bury the one line the next session needs. Three sharp lines beat thirty.
- Do not narrate checkpoint bookkeeping to the user — they see outcomes (per
  finishing-the-turn), not note mechanics.
- The stranger test disciplines wording, not volume; the rule 12 altitude test exists
  because a lesson that can never fire again is dead weight under the C7 budget.

## Files

- `references/notes-and-lessons.md` — a filled-in WORKING_NOTES.md captured
  mid-debugging (state-shaped, status tags, ruled-out ledger with commands, a
  write-ahead entry before a destructive step); six bad→good lesson rewrites; the C7
  consolidation pass with a before/after; a rule 14 distill-and-drop checkpoint,
  bad→good. Read it before creating the first notes file of a session and before any
  harvest.
