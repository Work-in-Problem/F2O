---
name: inventorying-capabilities
description: Capability-surface inventory and task-to-tool matching — read the session's ACTUAL attached tool surface (mcp__-prefixed tools, deferred-tool lists, MCP server instruction blocks, installed skills beyond this curriculum, harness features like background execution and scheduled tasks) and match every task feature against it. Use at the start of any session whose tool list extends beyond the built-in core; BEFORE driving a web page, browser, pdf/docx/xlsx/pptx, database, screenshot, app, or message channel through Bash improvisation (curl, python -c, ad-hoc converters); before writing "I can't do X" or "there's no tool for X" or promising "I'll send/post/deploy it"; before asking the user to perform by hand an action a connected tool might reach; and mid-task the moment a new deliverable format, data source, or external system surfaces. In a core-tools-only session this skill costs one line and goes inert.
---

# Inventorying capabilities

**A capability you never read is a capability you don't have: the session's real tool
surface — MCP servers, deferred tools, installed skills, harness features — is ALREADY
in context, and routing work from a memorized core toolset (Bash/Read/Edit/Grep) instead
of from that text is the defect.** Once matching is a checklist step, tool
under-triggering stops being a recall problem: every task feature either names its tool
or records an explicit no-match. This skill governs execution-route selection only — how
a chosen route is verified, reported, or scoped belongs to the skills that own those
phases.

**Escape hatch, applies to every rule below:** if you believe this case is a justified
exception, state a one-line justification and proceed. Never silently skip a rule.

## When to use

Load at the start of any session whose tool surface extends beyond the built-in core:
any mcp__-prefixed tool, a deferred-tool list, MCP server instruction blocks, installed
skills beyond this curriculum's own, or named harness features. Load mid-task the moment
any of these is about to happen: driving an external system or non-text format (web
page, browser, pdf/docx/xlsx/pptx, database, app, message channel) through Bash; writing
"I can't do X" / "there's no tool for X" / "I'll send/post/deploy it"; asking the user
to open, paste, upload, or click something; a new deliverable format, data source, or
external system surfacing. In a session exposing only the built-in core set, rule 1
collapses to one line and the rest is inert — this skill adds no rule load to ordinary
coding tasks.

## Core rules

1. **INVENTORY-AND-MATCH.** At task start, inside the breadth-first opening window
   (constants.md C15 — the window itself is search-first-context rule 3's) and alongside
   managing-working-memory rule 1's memory sweep, read the capability surface attached
   to THIS session: the system-prompt tool list including every mcp__-namespaced tool,
   any deferred-tool list, MCP server instruction blocks, the installed-skills list, and
   named harness features (background execution, scheduled tasks, hooks, preview/browser
   bridges). This costs ZERO tool calls — the text is already in context; choosing an
   execution route without having read it is the defect. Then, before the first
   execution-route decision — after spec extraction when planning-to-done runs (its
   rule 2 owns the checklist; when constants.md C6 gates planning out, do the pass
   inline) — map each task feature (deliverable format, data source, external system,
   output channel, observation target) to the matching tool or skill, or record
   "no match — core tools". A feature whose domain a connected MCP server's name, tool
   names, or instruction block covers routes through that server by default. Two
   carve-outs: sub-agent fan-out is one row of this pass, but its verdict belongs to
   constants.md C4 and `delegating-parallel-work`; the curriculum's own skills route
   per CLAUDE.md §5, never per this pass. Closing clause: a relevant tool you
   deliberately do NOT use gets one line — tool + reason — in the Decisions ledger
   (finishing-the-turn rule 10; storage per CLAUDE.md §3 when notes are live), because
   silent non-use is indistinguishable from a blind spot. That ledger line is the ONLY
   artifact this skill adds: match results live inline or in existing §3 sections, never
   in an INVENTORY.md or standalone inventory table (CLAUDE.md §3). A session exposing
   only the built-in core set gets one line noting that, and no further ceremony.

2. **PURPOSE-BUILT OVER IMPROVISED.** Before driving an external system or non-text
   format through Bash — curl/wget for web content, python -c or CLI converters for
   pdf/docx/xlsx/pptx, ad-hoc scripts for screenshots, database CLIs, message channels —
   check the inventory for a listed tool or skill purpose-built for it. Listed wins by
   default; the Bash improvisation requires the escape hatch's one-line justification,
   turning the demotion from silent into auditable. Corollary — one error never demotes:
   when a purpose-built call fails, debug the CALL — parameter shape, unloaded schema
   (rule 3), missing setup step (access grant, workspace selection), wrong tool tier —
   before any improvised fallback, escalating per constants.md C5 (the retry protocol
   itself is finishing-the-turn rule 7's). Silently abandoning a listed tool for Bash
   after one error is the named failure mode. Two-sided: when core tools genuinely
   suffice — a local text file needs Read, not a document pipeline — reaching for the
   exotic tool for its own sake is the mirror defect.

3. **DEFERRED MEANS AVAILABLE.** A tool named in a deferred/searchable list is a real
   capability, not a missing one. Check the deferred list before any "no tool for X"
   conclusion. When deferred tools are needed, load ALL anticipated schemas in ONE
   batched discovery call — never one round-trip per tool — and never invoke a deferred
   tool before its schema is loaded. A schema-validation error on a deferred tool means
   "load the schema and retry", never "the tool is broken or absent".

4. **CAPABILITY CLAIMS NEED RECEIPTS.** Never write "I can't do X", "there's no tool
   for X", or "that would need Y access", and never promise a forward action ("I'll
   post/send/deploy/schedule it"), without having checked the inventory — including the
   deferred list (rule 3) — in THIS session. This extends search-first-context rule 7's
   receipts standard from codebase-structure claims to the tool surface. Boundary:
   claims about actions already COMPLETED stay under the Layer 0 claim audit
   (CLAUDE.md §1) and `verifying-before-claiming`; this rule covers only availability
   assertions and forward promises.

5. **TOOLS BEFORE THE USER'S HANDS.** Before asking the user to perform an action —
   open a page, paste its contents, upload a file, click through an app, read what
   their screen shows — check whether a connected tool can perform or observe it
   directly, and use it when the action is Class A (CLAUDE.md §2). This extends
   search-first-context rule 11 from disk/web-discoverable FACTS (which stay that
   rule's) to tool-reachable ACTIONS. Class B/C actions route to the user regardless
   of tooling, parked per finishing-the-turn rule 2.

6. **MID-TASK RE-MATCH.** Re-run rule 1's match pass for the NEW feature only — never
   the full sweep — when any of these fires mid-task: a new deliverable format or data
   source appears, the task pivots to a new external system, a phase boundary passes
   (build → verify → report), or an error shows the current route lacks a needed
   capability. The trigger is the feature event, not a call count: inventory recall
   decays as context grows — a tool surface read once at session start and never
   re-consulted is how a renamed CSV ships as "the xlsx". The event trigger bounds the
   decay windows.

## Do not over-apply

- Core-tools-only sessions: rule 1 is one line and everything else is inert. Do not
  manufacture a match pass for a task that Read/Edit/Grep/Bash fully covers.
- The pass forces the read and the match step, not matching quality: a vaguely-phrased
  need can still miss a sparsely-described tool. Cheap second look before recording
  "no match": scan tool NAMES and server instruction blocks for the feature's domain
  nouns — not an extended research detour.
- Purpose-built precedence is a default, not a ban: whether a marginally-relevant tool
  beats a core-tool route in a specific case is a judgment call. Rule 1's ledger line is
  what makes choosing core tools legitimate — use it rather than forcing an ill-fitting
  tool.
- Do not narrate the sweep or the match pass to the user — they see the routes chosen
  and the Decisions ledger, not inventory mechanics.

## Files

- `references/inventory-and-match-examples.md` — the five-category task-feature
  taxonomy (deliverable format / data source / external system / output channel /
  observation target) with matching keywords per category, plus three good-vs-bad
  traces: Bash-curl improvisation vs a listed fetch tool; a false "no tool for X" claim
  vs one batched deferred-schema load; a late format pivot shipped as a renamed CSV vs
  a rule 6 re-match that finds the spreadsheet tool. Read when unsure how the match
  pass applies to a concrete feature — not routinely (token cost).
