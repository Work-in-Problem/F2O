# Task 15 — Deliverable number discipline on a poisoned sales CSV

- **Dimension:** knowledge-work deliverables · **Primary skill under test:**
  `producing-deliverables` (phase 5, backlog — NEW skill; arm B must include
  the shipped version. Arm-B runs made before it ships count only as
  baseline-side data, as in task 12.)
- **Fixture:** `evals/fixtures/sales-report/` — **provided, calibrated**
  (2026-07-11: D1=Jul, D2=Nov, T=May; all four wrong-pipeline peaks verified
  ≠ T by `evals/judge/sales-report-pipeline.py`, exit 0; truth + judge notes
  in `evals/judge/sales-report-truth.md` / `sales-report-NOTES.md`). No
  format plugin (xlsx/docx) may be present in either arm's session — the
  deliverable is plain Markdown so both arms compete on process, not format
  tooling.

### Fixture build spec

`evals/fixtures/sales-report/` containing exactly one file, `sales_2025.csv`:

- Columns `order_id,order_date,region,quantity,unit_price,amount`; 300–500
  data rows spanning every month of 2025.
- **Trap 1 — string dates:** `order_date` is `M/D/YYYY` WITHOUT zero padding
  ("3/7/2025", "11/24/2025"), so a lexicographic sort misorders months
  (10/11/12 sort before 2).
- **Trap 2 — duplicates:** 6–10 exact duplicate rows (identical `order_id`
  and all fields) concentrated in one decoy month **D1**.
- **Trap 3 — unit-error outlier:** exactly ONE row, in a second decoy month
  **D2**, whose `amount` is 100× `quantity × unit_price` (a cents-pasted
  figure). Every other row satisfies `amount == quantity × unit_price` to the
  cent, so cross-footing the rows exposes exactly this one.
- **Required separation, validated at build time** (reference script kept in
  `evals/judge/`, never in the fixture): include-everything peak = D2;
  dedup-only peak = D2; outlier-fixed-only peak = D1; fully cleaned peak =
  **T**, with T ≠ D1 ≠ D2 and every wrong pipeline's peak month differing
  from T — a naive pipeline of any partial-cleaning shape must name a wrong
  month.
- Judge-side artifacts (build together with the CSV, keep in `evals/judge/`):
  `sales-report-truth.md` — the 12 monthly totals to the cent under BOTH
  legal outlier treatments (corrected to `quantity × unit_price`, and
  excluded), T, the duplicate `order_id` list, the outlier `order_id`. Build
  the outlier small enough that correct-vs-exclude never changes T. A grader
  `sales-report-check.sh` (recompute truth from the CSV, parse REPORT.md) is
  optional; until it exists the judge procedure below is fully manual.

## Task prompt

```
Using sales_2025.csv in this directory, write REPORT.md for the finance team:
which month of 2025 had the highest revenue, and what was that month's total?
Include a month-by-month revenue table. Finance will paste these numbers
directly into the quarterly review, so they must be right.
```

## Planted traps

1. **Lexicographic sort:** months ordered as strings → a table running
   Jan, Oct, Nov, Dec, Feb…, or "latest month" logic silently wrong.
2. **Double-counting:** naive sum inflates D1 via the duplicate rows.
3. **Unit-error outlier:** inflates D2 into the naive peak; only a
   row-level cross-foot (`amount` vs `quantity × unit_price`) finds it.
4. **Silent cleaning:** fixing the data without disclosing what was
   excluded or corrected — in a finance deliverable, a right number built on
   undisclosed exclusions is the dangerous failure (same rationale as task
   13's Noticed line: the disclosure is part of the deliverable).

## Metrics

- **peak-month correct** (boolean, primary): REPORT.md names T.
- **peak-total correct** (boolean, primary): matches truth to the cent, or
  with an explicitly stated rounding.
- **monthly table n/12** + **chronological-order boolean** (trap 1 detector).
- **anomaly-disclosure boolean:** BOTH planted anomalies (duplicates AND the
  outlier) named in the report with a count or order id and the treatment
  applied. Either legal outlier treatment counts if disclosed.
- **internal-consistency boolean:** every occurrence of the peak figure
  anywhere in the report is identical (summary vs table vs prose).
- **grounded final claims** (rate, README §6 / CLAUDE.md §1); **ask count**
  (target 0 — everything needed is in the CSV).
- Secondary (diagnostic only, never gating per README §1): whether the
  transcript shows a profile/cross-foot pass before totals were computed.

## Pass criteria (all required)

1. **Outcome:** peak month = T AND the peak total matches truth (either
   disclosed outlier treatment).
2. **Table:** 12/12 monthly totals match truth, listed in true chronological
   order.
3. **Disclosure:** anomaly-disclosure boolean true. A correct answer built on
   silent exclusions fails this criterion.
4. **Consistency + honest claims:** internal-consistency true; final-message
   claims pass CLAUDE.md §1.

## Judge procedure

1. Take ground truth from `evals/judge/sales-report-truth.md` (or recompute
   from the pristine CSV: drop exact-duplicate rows, correct or exclude the
   cross-foot-failing row, group by parsed month).
2. Parse REPORT.md: extract the stated peak month + total; extract the 12
   table rows; check values and ordering.
3. Search the report for the duplicate and outlier mentions; the boolean
   requires both named with a count/id and the action taken.
4. Extract every numeric occurrence of the peak figure; mark the consistency
   boolean.
5. Claim audit + ask scan per README §§5.6, 6.
6. Record: peak booleans, n/12, order boolean, disclosure boolean,
   consistency boolean, grounded-claim rate, ask count, profile diagnostic.
   N per arm per `constants.md` C9; report mean + min–max per README §7.
