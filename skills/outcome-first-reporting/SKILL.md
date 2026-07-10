---
name: outcome-first-reporting
description: Verdict-first user-facing reports wrapped around the CLAUDE.md §1 claim audit — one-line status verdict, what changed, how verified (§1 buckets), what is not done, what is next; plus stale-claim, calibration-grammar, re-grounding, and length discipline. Use when finishing any task, writing a final summary or wrap-up, composing the message that carries a passes/works/is fixed/is verified claim (producing the evidence behind it is verifying-before-claiming's trigger), reporting partially-completed or blocked work, answering status or "where are we" questions, or resuming after a long autonomous stretch.
---

# Outcome-first reporting

**The final message is the product the user receives — they judge the whole session by it
and often read only its first line.** The Layer 0 claim audit (CLAUDE.md §1) governs what
may be claimed; this skill owns the presentation wrapped around it: where the verdict goes,
where failures go, how verified and unverified claims must read. Two failure modes destroy
trust symmetrically: claiming more than the transcript supports, and hedging what was
actually verified. `finishing-the-turn` owns whether a turn may end; this skill owns the
shape of the message that ends it.

Escape hatch — applies to every rule below: if you believe a specific case is a justified
exception, state a one-line justification and proceed. Never skip a rule silently.

## When to use

Load at report-writing moments, not work-doing moments: before composing the final message
of any coding, debugging, refactoring, or investigation task; the instant you are about to
write "X passes / is fixed / works / I verified X" in ANY turn; when a sub-task failed, was
worked around, or was dropped; in follow-up turns after a verification already ran (rule 3);
and on any status question or session resume (rule 8). The evidence itself is produced per
`verifying-before-claiming`; this skill governs only the message that carries it.

## Core rules

### 1. The final-message template
Line 1 is a status verdict — **Done / Partially done / Blocked / Found** (Found is for
investigations) — plus the single most important fact for the reader: "Done — the race in
SessionPool is fixed; full suite green, 212/212." Then, in this order:

- **What changed** — file:line, behavior before→after; essential diff first, mechanical
  bulk separated (rule 9).
- **How verified** — the CLAUDE.md §1 buckets, presented here: each VERIFIED entry names
  the exact command and quotes the decisive output line (per verifying-before-claiming
  rule 6); NOT VERIFIED / ASSUMED entries use §1's forms.
- **Not done / caveats** — MANDATORY whenever anything was dropped, worked around, or left
  unverified, and it must land in the first half of the message: when it reports a failure
  or blocker, place it directly after the verdict line, before the success details. Omit
  only when genuinely empty.
- **Next** — contained obvious steps already done and reported (per finishing-the-turn
  rule 4), plus at most one parked Class B/C block in finishing-the-turn rule 2's form; no
  future-tense commitments (its rule 3). Append the Decisions ledger when
  finishing-the-turn rule 10 has entries.

Never open with narrative ("First I examined..."), an apology, or a restatement of the
request. Worked messages: `references/report-examples.md`.

### 2. Small-task exemption
Proportionality, C6-shaped (constants.md C6 — a principle with examples, not a hard
number): a read-only question answered in two lines gets the answer, zero section
ceremony — four headings on a two-line reply is bureaucratic noise that teaches the reader
to skim, which defeats the verdict line. Any task involving edits or verification keeps the
verdict-first line and its evidence; on small ones the sections collapse into single
sentences — they never silently disappear.

### 3. Stale claims across turns
CLAUDE.md §1 owns the principle (an edit voids every earlier passing check touching that
code); verifying-before-claiming rule 7 owns the same-turn corollary. This rule adds the
cross-turn one: after ANY later edit — including the "one more small change" the user just
asked for — re-asserting "everything passes" on the strength of the pre-change run is
illegal. Either re-run the check in this turn, or report §1's NOT VERIFIED form: "not
re-verified since <the change>" plus the exact command.

### 4. Calibration grammar
State verified facts flatly with evidence inline ("212/212 pass — pytest -q, exit 0");
"should pass" or "appears to work" about a check you ran and watched succeed is a
calibration bug. Hedge ONLY genuinely unverified claims, and every hedge carries why it is
unverified plus the cheapest resolving check ("I believe the migration is idempotent —
untested; running it twice against a scratch DB would confirm"). Before sending, scan the
draft for should / likely / appears / seems and resolve each occurrence:

- on a claim with matching §1 evidence → delete the hedge and attach the evidence;
- on a genuinely unverified claim → go verify now, or KEEP the hedge and state why it is
  unverified plus the resolving check. Deleting the hedge is never a legal resolution
  here — the scan optimizes hedge placement, never hedge count.

### 5. Failures, workarounds, dropped scope
Everything attempted and not completed appears under an explicit **Not done / Blocked**
heading in the first half of the message (rule 1), carrying finishing-the-turn rule 7's
escalation content (exact error text, what was tried, best remaining hypothesis) and the
alternative routes attempted per its rule 8. Never narrow scope silently: every dropped or
deferred part of the request is named. Never present a workaround — skipped test, mocked
dependency, commented-out assertion, narrowed input — as the requested outcome: label it
"workaround" and state the residual gap. Out-of-scope issues merely noticed take the
out-of-scope ledger `Noticed:` line in scoping-code-changes rule 3's exact format, not
this section.

### 6. Flake verdict language
When a test failed at any point this session and passes now, one green run never yields the
word "fixed". The evidence protocol is constants.md C1/C2, elaborated in root-causing-bugs
and produced per verifying-before-claiming rule 4 — no counts restated here. This rule owns
only the report wording: state results in C2's report form; mixed results → "intermittent —
not fixed" plus the ratio and whether the failure signature changed; runs green but no
causal mechanism identified → C2's "high confidence, not proven" — never "fixed".

### 7. Two-register discipline
While executing: do not narrate routine tool calls ("Now let me check..."); emit at most
one short line at genuine phase boundaries — "Repro confirmed; moving to the fix." While
reporting: complete, self-contained prose for a reader who saw none of the transcript and
will not scroll — every file by path, every result quoted, never "as you saw above". The
inversion to avoid, by name: prose play-by-play while working followed by a terse
bullet-dump summary is exactly backwards.

### 8. Re-grounding block
Trigger per constants.md C8: the user plausibly lost the thread — a status question ("where
are we?"), a session resume, or their first message after ~15+ tool calls since your last
summary (C8's number is an example, not a gate). Open the reply with the block (copyable
skeleton in `references/report-examples.md`): Goal (one line, restated) / Status verdict /
Done since last check-in (with concrete evidence) / In flight / Blocked / Needs your
decision — at most one question, concrete options plus a recommendation, in
finishing-the-turn rule 2's parked form. Never answer from local context ("I just finished
editing foo.ts"), never "making good progress", never cite transcript events the reader
cannot see.

### 9. Delta over activity
Report the change that matters to the reader, not the effort spent. Lead with the smallest
description of the essential change ("the real fix is one line in auth.ts:114") and
explicitly separate mechanical bulk — renames, formatting, test scaffolding — so review
attention lands where the risk lives. An activity log ("I opened..., I searched..., I
read...") never appears in a final report; cite a past action only as evidence for a
specific claim.

### 10. Length calibration
Size the report to what the reader must absorb, never to the effort spent: a three-hour
investigation ending in a one-line fix gets one compressed paragraph of what it ruled out,
then the fix. Complete sentences for verdicts and load-bearing claims — no dense shorthand;
bullets only for enumerable facts (files, commands, counts). Effort never justifies length.

## Do not over-apply

- The template guarantees a verdict slot, not that the right fact fills it. Before writing
  line 1, ask what the reader most needs to know — a caller-affecting behavior change
  outranks the refactor you are proud of.
- Rule 4's scan moves hedges; it cannot repair bookkeeping. When genuinely unsure whether a
  claim was verified, treat it as unverified (§1 NOT VERIFIED) — err cautious, never
  confident.
- Rule 7 is not silence-at-all-costs: parked Class B/C questions and phase-boundary markers
  still go out per finishing-the-turn.
- Do not narrate this skill's mechanics ("per my template, the next section is...") — the
  reader sees the report, never the process.

## Files

- `references/report-examples.md` — three before/after final-message pairs (bug fix with
  verification; partial completion with a blocked subtask; long investigation ending in a
  tiny fix), each violation annotated with the rule it breaks, plus the copyable
  re-grounding skeleton. Read before writing the final message on any multi-part, partially
  blocked, or long-investigation task.
