---
name: conducting-agent-fleets
description: Conduct long-running multi-agent work — discover the dispatch surface before conceding serial (including deferred Agent tools behind ToolSearch), run subagents and long jobs in the background while continuing own work, phase multi-episode campaigns with resumable checkpoints, and gate every integration on verified evidence. Use when work spans multiple fan-out episodes or hours, when a command or agent could run in the background, when a completion notification arrives, when resuming an interrupted campaign, and ALWAYS before concluding "there is no subagent tool" or ending a turn only to wait.
---

# Conducting agent fleets

**On partitionable or long-running work you are a conductor, not a soloist: progress is
measured by fleet state advanced per unit of wall-clock, and doing qualifying work
serially with your own tool calls — or idling while a background result is pending —
is a defect, not a style choice.** The loop: Discover the surface → Phase the campaign
→ Dispatch → Work while waiting → Integrate through gates → Checkpoint → Resume.

Escape hatch — applies to every rule below: if you believe this case is a justified
exception, state a one-line justification and proceed. Never skip a rule silently.

Ownership boundaries (cross-reference, never restate): WHAT to split, per-stream floors,
sub-task sizing, dispatch-prompt contents, and the trust-but-verify synthesis gate belong
to `delegating-parallel-work` (rules 1, 4, 6, 9) with numbers in constants.md C4/C12/C13.
Reading the session's tool surface belongs to `inventorying-capabilities`. Notes files
and durable memory belong to `managing-working-memory` (CLAUDE.md §3). This skill owns
the CONDUCT: surface discovery at the dispatch decision, the standing posture across
episodes, background execution, and campaign lifecycle.

## When to use

Load when work will outlive a single fan-out episode (multi-phase builds, migrations,
experiment campaigns, overnight or multi-hour tasks); when any command or agent result
could arrive later instead of now; the moment a background-completion notification
arrives; when resuming interrupted or compacted long work; and ALWAYS before writing
"I can't parallelize this" or ending a turn with nothing but "waiting for X".
For a single self-contained fan-out burst, `delegating-parallel-work` alone is the
primary — do not add this skill's campaign ceremony to a one-episode task.

## Core rules

### 1. Discover the dispatch surface before conceding serial
"No subagent tool in my tool list" is a claim under CLAUDE.md §1 — verify it before
acting on it. The check, in order, costs under a minute: **(a)** core tools (Task /
Agent / dispatch); **(b)** the deferred-tool list — harnesses hide dispatch tools behind
a loader such as ToolSearch: query it for agent/task/dispatch names before concluding
absence (sessions have been observed loading todo-list tools through ToolSearch while
never asking it for the Agent tool sitting in the same list); **(c)** background
execution for commands (run-in-background flags, `&` + notification hooks). Only after
all three miss may work proceed serially — and then record "no dispatch surface: checked
a/b/c" as a one-line Decisions entry. Finding a surface does not compel fan-out; it
compels running the `delegating-parallel-work` rule 1 partition table.

### 2. Conductor stance
When the C4 trigger is met and a dispatch surface exists, dispatch FIRST, then take
retained work — never the reverse. Grabbing the most interesting stream yourself and
"delegating the rest later" serializes the fleet behind your own hands. Your own edits
during a fleet run are limited to what `delegating-parallel-work` rule 7 assigns the
orchestrator: retained shared-file streams, integration scaffolding, and the union-level
verification commands the synthesis gate will need.

### 3. Phase the campaign
Work spanning more than one fan-out episode gets a phase plan before the first dispatch:
for each phase, one line — goal, fleet (who runs), and the integration gate (the runnable
check that ends the phase). Each phase must end at a VERIFIED state so the campaign can
resume from its boundary after interruption or compaction. Store phases under
`WORKING_NOTES.md ## Plan` and per-phase outcomes under `## Delegation` when the notes
trigger applies (constants.md C3); otherwise inline. A campaign without phase boundaries
cannot be resumed — it can only be restarted, which forfeits every finished stream.

### 4. Work while waiting
Before every dispatch burst, write down the next 2–3 orchestrator-owned items; execute
them while the fleet runs. Ending a turn whose only content is "agents are running" is
the plan-shaped ending finishing-the-turn rule 3 forbids. Two waiting modes, chosen by
what the harness supports: **(a)** notification-driven — when completions re-invoke you,
never poll; schedule at most a long fallback check for work that could hang silently;
**(b)** blocking-only — batch the blocking calls per `delegating-parallel-work` rule 7
and sandwich retained work around the batch. If genuinely nothing orchestrator-owned
remains, say so in one line and end the turn — idling disguised as "monitoring" is
theater.

### 5. Background-first for long work
Any command expected to run longer than ~2 minutes (full suites, builds, batch scripts,
long experiments) and any agent whose result is not needed for your IMMEDIATE next step
runs in the background when the harness offers it. Foreground-blocking on a long job
while ownable work exists is the same defect as rule 2's soloist stance, applied to
commands. On each completion notification: re-ground before integrating — reread the
notification's actual result (not your prediction of it), then the files it claims to
have produced (constants.md C16 staleness rule applies to them).

### 6. Integrate through gates, at fleet scale
The synthesis gate itself belongs to `delegating-parallel-work` rule 9 — reports are
claims; run the union check yourself. At fleet scale this skill adds one sizing rule:
verification effort scales with the blast radius and unverifiability of the claim, not
with how confident the report sounds. Mechanical, grader-checkable results get the union
check; high-stakes or textual claims (a "review found no issues", an eval score, a
security assertion) get INDEPENDENT re-verification — your own re-run, or a second agent
tasked to refute rather than confirm. An aggregate "all N streams green" summary never
substitutes for the union gate.

### 7. Fleet economics
Size the fleet to the task, not the ambition: per-stream floor and sub-task band are
constants.md C4/C12; survey scale is C13. Cap concurrency to what the machine and API
sustain without thrashing (timing-sensitive fixtures and benchmark streams get reduced
parallelism or exclusive slots). When budget or caps force dropping coverage — fewer
verification votes, a sampled instead of exhaustive sweep — say what was dropped in the
report; a silent cap reads as full coverage.

### 8. Resume protocol
Returning to an interrupted campaign (new session, compaction, next morning): read
`WORKING_NOTES.md ## State` and `## Delegation` FIRST; re-run the last phase's
integration gate before building anything on top of it (a checkpoint that no longer
passes is a stale claim — CLAUDE.md §1); then continue from the phase plan. Never
re-dispatch a stream whose gate evidence still verifies, and never trust a checkpoint
you have not re-run after an interruption you did not observe.

## Do not over-apply

- **One burst is not a campaign.** A single fan-out with an immediate merge is
  `delegating-parallel-work`'s territory end to end; phase plans and resume protocol
  add ceremony with no return.
- **Below C4, the conductor stance is over-delegation** — the equal-and-opposite
  pathology, owned and described by `delegating-parallel-work`'s "Do not over-apply".
  Discovering a dispatch surface (rule 1) never by itself justifies using it.
- **Do not background trivial commands** — a 2-second test run behind a notification
  round-trip is slower and noisier than just running it.
- **Do not narrate conducting mechanics to the user** — report fleet outcomes and
  decisions, not dispatch topology (finishing-the-turn owns report shape).
