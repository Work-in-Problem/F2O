---
name: delegating-parallel-work
description: Partition multi-part work into parallel sub-agent workstreams and orchestrate them to a verified merged result. Use BEFORE starting any task spanning multiple packages, modules, or independent questions — batch changes, migrations across components, wide codebase surveys — and mid-task the moment work reveals itself as partitionable.
---

# Delegating parallel work

**When the fan-out trigger (constants.md C4) is met, parallel delegation is the default
execution mode — executing qualifying independent workstreams serially with your own
tool calls is a defect, not a style choice.** The loop: Partition → Decide → Size →
Dispatch → Continue own work → Verify the union → Re-delegate fixes.

Escape hatch — applies to every rule below: if you believe this case is a justified
exception, state a one-line justification and proceed. Never skip a rule silently.

## When to use

Load at task start whenever the request could plausibly meet constants.md C4 — 3+
genuinely independent workstreams, each ≥ ~10 minutes of agent work: the same mechanical
change across multiple packages, batch fixes across modules, multi-module features,
several independent codebase questions, wide surveys. Load mid-task the moment serial
work reveals a repeating pattern across independent locations — do not finish serially
just because you started serially. When in doubt, rule 1's table is the cheap test.
Do not load for single-module tasks or refactors where every stream writes the same
core files.

## Core rules

### 1. Partition first
Whenever C4 might apply, produce the workstream table as your FIRST work artifact,
before any edit: `stream | files/dirs touched | read-only or write | depends-on`.
A stream is write-disjoint-independent iff its write set intersects no other stream's
write set AND its depends-on column is empty or names only finished streams; everything
else is entangled. Count workstreams, never files: **3 files is not 3 workstreams** — a
workstream is a coherent deliverable meeting C4's per-stream floor. Produce the table
even when the verdict turns out to be "do it all myself"; the table makes the decision
auditable. Storage: `WORKING_NOTES.md ## Delegation` when the notes trigger applies
(constants.md C3, CLAUDE.md §3), otherwise inline in the transcript.

### 2. Fan out by default under C4
If the table shows C4 met and each independent stream can be fully specified in a
standalone prompt, fan-out is the default: dispatch those streams to parallel
sub-agents. Deviating requires the escape hatch's one-line justification — legitimate
ones include results that are not mechanically mergeable, or work that depends on
session judgment you cannot paste into a prompt. Below C4, do the work yourself:
dispatch overhead exceeding the work is the equal-and-opposite failure mode (see
Do not over-apply). Implementation streams get write responsibility — do not delegate
only searches while keeping every edit for yourself.

### 3. Never ask permission to parallelize
Delegation topology — whether to fan out, how to split, when to proceed after an agent
finishes — is Class A per CLAUDE.md §2: decide silently, add one Decisions-ledger line.
"Should I use subagents?" must never appear in a message. The only stream-related user
escalation is a requirements-level conflict between streams — that is Class C, parked
at turn end per finishing-the-turn rule 2.

### 4. Size sub-tasks
Each sub-task is one coherent deliverable with a runnable done-condition, sized per the
sub-task band (constants.md C12): roughly 10–30 minutes of agent work, proxy ~1–10
files or one module/test suite, split along module/directory/test-suite ownership
boundaries. Two named anti-sizes: the **mega-agent** that re-runs
the whole task (adds latency, zero parallelism, loses your session context) and the
**per-file micro-agent** (spawn overhead exceeds the work; collisions likely).

### 5. One writer per file
If two candidate streams would write the same file, pick one: **merge** them into a
single sub-task, **retain** that file's change yourself, or **sequence** the shared-file
change after the fan-out completes. Never assign one file to two concurrent writers.
Worked merge/retain/sequence decision: `references/workstream-table-examples.md`, ex. 2.

### 6. Self-contained dispatch prompts
Every dispatch prompt must contain all six items: **(a)** a one-sentence objective;
**(b)** exact absolute file paths; **(c)** every piece of session context the agent
needs — conventions, decisions, code patterns — PASTED inline: catching yourself writing
"as discussed", "from before", "the bug we", "like earlier", or "the pattern from" means
stop and inline the actual content, because the sub-agent cannot see this conversation;
**(d)** an explicit "Do not touch" list; **(e)** a done-condition as a runnable command
plus its expected output; **(f)** a return contract beginning "Report:" — files changed,
commands run with exit codes, open issues as a list. A prompt failing any item may not
be dispatched. Run `scripts/lint-dispatch-prompt.sh <prompt-file>` when convenient (it
machine-checks b, c, d, f); check a and e by eye.

### 7. Fire and continue
Dispatch all independent agents in ONE burst (parallel Task calls in a single block, or
background jobs). Then immediately continue orchestrator-owned work, in priority order:
(1) the retained shared-file or entangled stream, (2) integration scaffolding, (3)
writing the union-level verification commands rule 9 will need. Never emit a turn whose
only content is that agents are running — that is a plan-shaped ending and violates
finishing-the-turn rule 3. If the harness only exposes blocking sub-agent calls, still
batch them in one parallel block and do retained work before and after the batch.

### 8. Harness-conditional monitoring
Establish what the harness supports first; never instruct monitoring theater it cannot
express.
- **Running-agent output is inspectable** (pollable background tasks, a message channel
  to running agents): check each agent at least once mid-flight, at natural pause points
  after your own work units. Drift signals: edits outside the assigned file set,
  repeated failing attempts at the same command, output answering a different question
  than assigned. On drift, stop the agent and respawn with a repaired prompt — name what
  was misread, tighten the "Do not touch" list — rather than letting it finish wrong.
- **Dispatch-and-await** (the common Task-tool case — no mid-flight visibility): state
  that once, skip monitoring entirely, and put ALL the rigor into rule 9. The post-hoc
  gate is then the entire safety mechanism, so it may not be softened or sampled.

### 9. Trust but verify (the synthesis gate)
Sub-agent reports are claims, not facts — they fall under the Layer 0 claim audit
(CLAUDE.md §1) exactly like your own claims. Before incorporating any report:
(1) confirm claimed edits exist via git diff or grep — an agent that "changed 3 files"
must show 3 files in the diff; (2) run build/typecheck/tests over the UNION of all
parallel changes YOURSELF — per-stream checks cannot cover cross-stream interactions;
(3) re-run at least one result each agent reported; (4) when two reports overlap or
conflict, adjudicate by opening the source, never by preferring one report's prose.
Completion is claimable only after the merged check passes, quoting the decisive output
line per verifying-before-claiming rule 6.

### 10. Re-delegate remediation
When the union check fails, classify each failure. **Stream-localized** (traceable to
one agent's file set): dispatch parallel fix-up agents scoped to those streams, with the
EXACT failure output — error text, failing test names, stack traces — pasted into each
prompt; a fix-up prompt without the pasted failure is invalid. **Cross-stream** (emerges
only from the combination): fix it yourself; it needs the whole-system view. Never
discard a mostly-correct agent result and redo it from scratch — the fix-up inherits the
existing work. Loop back through rule 9 until the merged check passes.

### 11. Survey, don't hoard — two-sided
For genuinely wide surveys — needed information scattered so broadly that reading it
yourself would consume a large fraction of remaining context (constants.md C13; "on
the order of a dozen files" is an example, not a gate) — dispatch read-only survey
agents: each gets ONE specific question, absolute directories to search, and a
required structured answer format with a hard line cap (~30 lines — C13), e.g.
"Answer / Evidence as file:line quotes / Confidence". Consume only the
digests; preserved orchestrator context is what keeps rule 9 sharp. Two-sided: reading
~12 small files yourself is often cheaper and higher-fidelity than 12 sub-agent digests
— delegate when breadth threatens your context budget or the questions parallelize
cleanly, never because a file count ticked past a number.

### 12. Delegation records
When the notes trigger applies (constants.md C3), record each fan-out in
`WORKING_NOTES.md ## Delegation` (CLAUDE.md §3): the workstream table used; per-agent
outcome (clean / wrong-scope / drifted / failed — for wrong-scope, WHICH rule 6 item
was underspecified); merge conflicts and resolutions; the union-check command and
result. Read the section before designing the next fan-out and tighten prompts along
previously failing items. Journal placement and the ban on parallel log files:
CLAUDE.md §3.

## Do not over-apply

- **Over-delegation is this skill's signature pathology.** Below C4, a six-item
  self-contained prompt costs more than the work it delegates. Symptom: the dispatch
  prompt is longer than the expected diff. Do the work yourself.
- **Formally disjoint is not semantically independent.** Seam-risk signals to check
  before dispatch: two streams will each need a helper, type, or naming convention that
  does not exist yet (two agents inventing incompatible helper APIs is the classic
  failure); the same data shape crosses a stream boundary; both streams extend one
  conceptual surface (error taxonomy, config keys, public API naming). Mitigation:
  pre-decide the shared convention and paste it into every affected prompt (rule 6c),
  or retain the shared piece yourself (rule 5). If the seam cannot be de-risked, keep
  the work serial — see `references/workstream-table-examples.md`, example 3.
- **Do not narrate topology mechanics to the user** — they see outcomes and the
  Decisions ledger, not the partition deliberations.

## Files

- `references/dispatch-prompt-template.md` — annotated GOOD dispatch prompt (all six
  rule 6 items) plus a BAD counterexample with each defect's downstream failure; read
  before writing the first dispatch prompt of a session.
- `references/workstream-table-examples.md` — three worked partitions: clean 5-package
  fan-out; shared-utility seam (merge/retain/sequence); entangled refactor kept serial.
- `scripts/lint-dispatch-prompt.sh <prompt-file>` — machine-checks rule 6 items b/c/d/f;
  exit 0 when clean, non-zero listing named violations.
