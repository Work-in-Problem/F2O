---
name: producing-deliverables
description: End-to-end production process for non-code deliverables — reports, spreadsheets (xlsx/csv), documents (docx/pdf/markdown), slide decks (pptx), charts, and data analyses — via a data-profile gate before any computation, logged cleaning decisions, independent cross-checks on every headline number, one units-and-rounding policy, a whole-artifact consistency sweep, and reopen-the-file verification. Use when the task's primary output is a document, spreadsheet, deck, chart, or analysis rather than a code change — load BEFORE first reading the source data, and ALWAYS before claiming a produced artifact is done, correct, or ready. Format mechanics (how to build the file, chart visual design) stay with the loaded format skill; this skill owns only the validation process.
---

# Producing Deliverables

**An artifact built on unprofiled data, carrying numbers computed exactly once, shipped
without ever being reopened, is a plausible-looking fabrication — even when it happens to
be right.** The Layer 0 claim audit (CLAUDE.md §1) governs what may be said about a
deliverable; this skill governs how deliverable evidence gets produced: profile the data,
log the cleaning, cross-check the figures, hold one presentation policy, sweep for
internal drift, reopen the file, and confirm the artifact answers the question asked.

Escape hatch — applies to every rule below: if you believe a specific case is a justified
exception, state a one-line justification and proceed. Never skip a rule silently.

## When to use

Load when the task's primary output is a non-code artifact: a report, spreadsheet
(xlsx/csv), document (docx/pdf/markdown), slide deck (pptx), chart, or data analysis —
BEFORE first reading the source data, and mid-task the moment a "quick chart" or "short
summary" appears inside another task. Boundaries: file-format mechanics and chart visual
design belong to whatever format skill is loaded (xlsx/docx/pptx/dataviz) — this skill
owns only the production process (validation, cross-checks, consistency, reopening,
answer shape); evidence for code changes stays `verifying-before-claiming`'s.

## Core rules

1. **DELIVERABLE SPEC INTO THE ONE CHECKLIST.** Before touching source data, fill the
   single done-checklist — owned by finishing-the-turn rule 5, integrated with
   verifying-before-claiming rule 1, extraction mechanics per planning-to-done rule 2
   when loaded — with this dimension's items: the question the artifact must answer and
   for whom; the required format and sections; the units-and-rounding policy (rule 6);
   and standing items for the consistency sweep (rule 7) and the reopen check (rule 8).
   Never keep a second deliverable-spec list, and never open a parallel data-audit
   journal — profile output and metric tables go in `WORKING_NOTES.md` sections per
   CLAUDE.md §3 when constants.md C3 applies.

2. **PROFILE BEFORE COMPUTE.** On first loading any data source (csv/xlsx/json/db
   extract) and BEFORE the first aggregate, pivot, or chart: run one profiling pass —
   row count, column types, per-column null counts, duplicate-key count, min/max of
   every numeric and date column (`scripts/profile-data.py <file>` does it in one
   call) — and quote the resulting counts (`WORKING_NOTES.md ## Findings` when C3
   applies, else inline). Dates parsed as strings (they sort lexicographically —
   Apr, Aug, Dec...), negatives in quantity-like columns, high-null columns, and
   duplicate keys are findings to resolve or route through rule 3 — never chart through
   them silently. This is the data analog of search-first-context rule 2's pre-edit
   read: that rule owns pre-edit reading of code; this rule owns only pre-computation
   reading of data.

3. **EVERY CLEANING STEP IS A LOGGED DECISION.** Trigger: any drop, filter, dedupe,
   imputation, type coercion, or outlier exclusion. Classify per CLAUDE.md §2 and
   record it in the Decisions ledger (mechanics and placement: finishing-the-turn
   rule 10); this rule adds only the required content — the operation, the reason, and
   before→after row counts. When the exclusion is material — it could plausibly flip a
   headline conclusion; a judgment call example-shaped like constants.md C6, never a
   number invented inline — treat it as Class C: compute both with and without,
   present both, and park the choice in finishing-the-turn rule 2's form.

4. **CROSS-CHECK AND TRACE EVERY HEADLINE FIGURE.** Trigger: any figure destined for a
   title, executive-summary line, chart callout, or KPI cell. Recompute it by a second
   independent path — a different tool, the transposed grouping (sum of row totals vs
   sum of column totals), or a spot-total over the filtered source rows — and reconcile
   exactly under rule 6's policy; cross-foot every table (row totals vs column totals
   vs grand total). Keep the trace — the generating script, command, or formula
   chain — so "where does this number come from" is answered by re-running source file
   → rule 3's ledger entries → computation, never by re-deriving from memory. A figure
   with a single computation path, or whose trace is lost, sits in CLAUDE.md §1's
   NOT VERIFIED bucket regardless of the generating script's exit code.

5. **NO MEMORY-TYPED NUMBERS.** Trigger: about to write any digit into the
   deliverable's prose, tables, or charts. Its provenance must be a computation or
   retrieval from THIS session — search-first-context rule 1 owns the volatile-fact
   gate and its rule 7 the receipts standard; this rule extends them only into
   deliverable content: benchmark figures, market sizes, "typical" rates, and rounded
   recollections of your own earlier outputs are fabrications. Compute from the
   provided data, retrieve and cite, or write the slot as "PLACEHOLDER — needs source"
   and surface it per outcome-first-reporting rule 5.

6. **ONE UNITS-AND-ROUNDING POLICY.** Before writing the first output section, declare
   once: currency and scale (k/M/B), decimal places per metric family, percent vs
   proportion, date grain (and timezone when relevant). Apply it in every section,
   axis, and label. Where rounded components visibly fail to sum to the rounded total,
   fix the presentation or add a footnote — a silent 101% pie is a defect, not a
   rounding shrug.

7. **WHOLE-ARTIFACT CONSISTENCY SWEEP.** After the last content edit and before
   rule 8: list every metric that appears in 2+ places (summary prose, tables, charts,
   slide callouts, appendix) and diff the occurrences — any mismatch is a defect to fix
   now. Corollary of CLAUDE.md §1's edit-voids-evidence, applied to sections: an edit
   to source data, a filter, or an upstream figure voids every downstream figure,
   chart, and prose mention — regenerate the dependents from their rule 4 traces, never
   hand-patch the one cell you remember.

8. **REOPEN BEFORE DONE.** verifying-before-claiming rule 2's ladder maps to
   artifacts: generating-script exit 0 ≈ typecheck, never the top rung. Before any
   done/ready/correct claim, reopen the artifact with an independent reader and inspect
   the content: xlsx with formulas actually evaluated, pptx slides rendered to images
   and each one viewed, docx/pdf text re-extracted, csv round-trip parsed. Per-format
   mechanics (including the openpyxl never-evaluates-formulas trap):
   `references/reopen-recipes.md`; when a format skill (xlsx/docx/pptx/dataviz) is
   loaded, defer format how-to to it. The reopened content, not the generating script,
   is the CLAUDE.md §1 evidence; any regeneration of the artifact re-triggers this rule
   (the artifact analog of verifying-before-claiming rule 7).

9. **ANSWERS-THE-QUESTION PASS.** At closure, after planning-to-done rule 7's
   original-message re-read (when loaded; otherwise re-read the request now): state in
   one line how the artifact's HEADLINE answers the request's question-shape — a
   which/should-we request needs one explicit recommendation with quantified rationale;
   a top-N-by-X request needs a list actually ordered by X; a why request names a
   cause. An artifact that only presents data around the question is Partially done —
   reported per outcome-first-reporting rules 1 and 5, never silently shipped as the
   answer.

## Do not over-apply

- Right-size per constants.md C6: a two-line computed answer pasted into chat keeps
  rules 4 and 5 — a wrong number is a wrong number at any size — but needs no declared
  policy document, no sweep, and no reopen of a file that does not exist.
- Rule 9 forces AN answer, not the insightful one — it cannot pick the cohort analysis
  a retention question deserves. Likewise rule 2 surfaces the numbers; recognizing a
  domain-implausible 400% margin still takes judgment — when a profiled value smells
  impossible, say so rather than charting it.
- The rule 7 sweep is a content diff over repeated metrics, not scope enumeration: when
  the request carries a quantifier (all regions, every product), the denominator
  belongs to finishing-the-turn rule 6.
- This skill is process-only: slide layout, chart design, and file-format how-to belong
  to the loaded format skill — do not re-derive them from these rules.
- Do not narrate the pipeline (profile tables, sweep bookkeeping) beyond quoting
  rule 2's counts and the ledger lines — the user sees the artifact, the counts that
  justify trusting it, and at most one parked block.

## Files

- `references/reopen-recipes.md` — per-format reopen/verify mechanics for rule 8: xlsx
  recalculation (LibreOffice headless; the openpyxl `data_only` trap), pptx
  slide→image rendering plus a what-to-look-for checklist, docx/pdf text re-extraction,
  csv round-trip. Read when rule 8 fires.
- `scripts/profile-data.py <file> [--key COL[,COL]] [--sheet NAME]` — one-shot rule 2
  profile: rows, dtypes, per-column nulls, duplicate rows/keys, numeric/date min–max,
  strings-that-parse-as-dates detection, printed as a quotable table.
