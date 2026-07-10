---
name: extracting-from-images
description: Procedural extraction from screenshots, scans, charts, dense tables, and degraded images — probe pixel dimensions with bash, crop and zoom before reading dense regions, transcribe-then-verify tables, cross-check pixel-read numbers against any machine-readable source, bucket per-value confidence, never silently guess an illegible cell. A support skill — load mid-task, alongside the task's primary skill, the moment any image or scanned PDF must yield exact strings, numbers, table cells, or chart values (screenshots, UI captures, dashboards, receipts, photographed documents), BEFORE answering any extraction question from a just-Read image, and when the user disputes a previously delivered extracted value. Gist-only reads (layout, which dialog is open, rough colors) are exempt.
---

# Extracting from images

**A value read from pixels is a claim like any other, and "I looked at the image" is not
evidence for it.** Pixels are the lowest-fidelity source in the room; the expensive failure
is not misreading a blurry digit but delivering the misread in the same flat register as a
legible one. This skill converts perceptual limits into flagged uncertainty: probe before
reading, zoom before asserting, cross-check before delivering, and mark what could not be
resolved instead of guessing. It owns two curriculum deltas — pixels-are-last-resort source
routing (rule 4, extending search-first-context rule 11 to images) and per-value extraction
buckets (rule 5, applying the CLAUDE.md §1 buckets per extracted value) — other skills
reference these, never redefine them.

Escape hatch — applies to every rule below: if you believe a specific case is a justified
exception, state a one-line justification and proceed. Never skip a rule silently.

## When to use

This is a support skill: it never rides alone. Load it mid-task — alongside whatever
primary skill the CLAUDE.md §5 router chose — the moment an image or scanned PDF must
yield exact strings, numbers, table cells, or chart values: transcribing a table or
receipt, quoting an error message from a screenshot, reading figures off a dashboard or
chart, extracting config values from a photographed document. Load it BEFORE answering
any extraction question about an image already Read this session, and whenever the user
challenges a value you extracted earlier (rule 6). GIST reads are exempt and take one
full-frame Read with zero ceremony: page layout, which dialog is showing, rough colors,
what a large-print banner says. A batch of many images that meets the fan-out bar
(constants.md C4) is orchestrated per `delegating-parallel-work` — this skill defines no
multi-image parallelization and rides inside each stream.

## Core rules

1. **CLASSIFY THE READ, THEN PROBE.** Trigger: any image or scanned PDF enters the task.
   Classify what is being asked of it: GIST (one full-frame Read suffices — see When to
   use) vs EXTRACTION (exact strings, numbers, cells, chart values — the rules below
   govern). For EXTRACTION, before asserting any value, run one bash probe of pixel
   dimensions and format (recipes in `references/preprocessing-recipes.md`); the probe
   tells you whether the content's detail can survive at this resolution and whether the
   target needs cropping. Never answer an EXTRACTION question from a single full-frame
   Read when the target region is a small fraction of the frame or any character is
   uncertain after the first read — a qualitative trigger, example-shaped like
   constants.md C6/C8, not a hard number.

2. **CROP-ZOOM LADDER.** Trigger: the extraction target is small, dense, blurry,
   low-contrast, or a read left any character uncertain. Escalate one step at a time,
   re-Reading the tile after each step: (a) crop the target region to its own tile;
   (b) upscale the tile — `scripts/tile.sh` does (a)+(b) in one call; (c) enhance —
   grayscale, contrast stretch, threshold, invert for dark-mode screenshots, deskew for
   photographed pages (recipes in `references/preprocessing-recipes.md`); (d) if
   tesseract is installed, run it on the tile as a second independent reader and diff
   its output against your own reading — agreement corroborates, disagreement marks the
   value UNCERTAIN (rule 5), and OCR output alone is never truth. After EVERY crop, Read
   the tile and confirm it shows the intended region before trusting anything extracted
   from it — a wrong-coordinates crop verifies nothing (`verifying-before-claiming`
   rule 5's fresh-state principle, applied to tiles). Write all tiles and intermediates
   to the scratchpad, never into the user's repo.

3. **TRANSCRIBE-THEN-VERIFY TABLES.** Trigger: extracting any multi-row or multi-column
   structure. First transcribe into a machine-checkable block (markdown or CSV) stating
   explicit row and column counts. Then verify: (a) re-Read crops of every region marked
   uncertain plus at least one spot-check band; (b) execute in bash/python every piece
   of arithmetic the table itself carries — totals, subtotals, percentages, deltas — and
   reconcile each mismatch to either a transcription error (fix it) or a source
   discrepancy (report it, never silently resolve it). A transcription whose totals row
   was never executed is unverified. Row completeness is `finishing-the-turn` rule 6
   (enumerate-then-exhaust) applied to rows: state the in-image count, deliver n/n or
   name the missing rows — never silently drop rows; very long tables batch per that
   rule and constants.md C11.

4. **MACHINE-READABLE FIRST.** Trigger: about to deliver numbers or text extracted from
   pixels. Spend one search checking whether the same data exists machine-readably
   within the session's reach: the PDF behind the screenshot (pdftotext), a CSV/JSON
   export in the repo, the source database or API, the HTML behind a page capture. This
   is `search-first-context` rule 11 (search-don't-ask) extended to pixels — the image
   is the last-resort source, not the default one. If a machine-readable source exists,
   extract from it and use the image only to confirm you have the right region; on
   disagreement the machine-readable source wins and the disagreement is reported.

5. **PER-VALUE CONFIDENCE.** Trigger: delivering any extracted value the user will act
   on. Bucket every value: **CONFIRMED** — legible in a zoomed tile, or matched a
   machine-readable source or the table's own arithmetic; what counts as affirmative
   evidence is CLAUDE.md §1's standard, not a parallel definition. **UNCERTAIN** — best
   reading plus the specific ambiguity ("1,847 or 1,347; comma region blurry") plus the
   resolving step. **ILLEGIBLE** — sentinel per rule 6, never a guess. These are the
   CLAUDE.md §1 buckets applied per extracted value; the final message presents them per
   `outcome-first-reporting` rule 4's calibration grammar — this rule adds only the
   per-value granularity during extraction. On a degraded input, every value arriving
   CONFIRMED is itself a calibration defect: re-check before sending.

6. **NEVER SILENTLY GUESS.** Trigger: a cell, label, or digit remains unresolved after
   the full rule 2 ladder. Emit the ILLEGIBLE sentinel in place, state which ladder
   steps were attempted, and attach the crop's scratchpad path so the user can look
   themselves. Substituting a plausible value is a fabrication under CLAUDE.md §1 even
   if it happens to be right. Corollary — when the user disputes a delivered value,
   never produce a different guess from the same pixels: escalate the ladder on that
   region or declare it unresolvable with the tile attached.

7. **CHART VALUES ARE RANGES.** Trigger: extracting numbers from a chart with no printed
   data labels. Crop and read the axis tick labels and the legend FIRST; bind each
   series to its color/marker from the legend crop before assigning any value to any
   series. Deliver interpolated values as ranges bounded by tick granularity ("between
   4.0M and 4.5M, nearer 4.2M"), never as exact figures; exact figures require printed
   data labels, an accompanying data table, or a machine-readable source (rule 4).

8. **DEGRADATION IS REPORTABLE STATE.** Trigger: the rule 1 probe or any read reveals
   resolution loss, compression artifacts, moiré, or scan skew that the ladder cannot
   recover. Name the degradation and its consequence in the report ("capture is 800px
   wide; the sidebar digits are unrecoverable at this resolution"). The unrecoverable
   value is NOT VERIFIED per `verifying-before-claiming` rule 11's blocked-verification
   shape, with the exact better capture the user can provide (original file, full-res
   screenshot, 300-dpi rescan) as the runnable remedy — and the request for it is parked
   at turn end per `finishing-the-turn` rule 2, after every subtask not depending on the
   re-capture is complete.

## Do not over-apply

- Right-size per the constants.md C6 principle: a GIST read takes one full-frame Read
  and zero ceremony; a single large legible label needs no ladder; the full ladder plus
  rule 3/4 verification is for extractions feeding code, config, finances, or a decision
  the user will act on.
- Rule 5 governs bucketing during extraction only; how the final message phrases
  verified and hedged claims is owned by `outcome-first-reporting` (its rules 1 and 4) —
  do not invent a second presentation format.
- The ladder raises effective resolution; it does not create pixels. When a value stays
  unreadable after the full ladder, the win is an honest ILLEGIBLE with the tile
  attached — burning further calls re-enhancing the same region is over-application.
- Do not narrate ladder mechanics tile-by-tile; the user sees extracted values, their
  buckets, and tile paths for the unresolved ones — not the process.

## Files

- `references/preprocessing-recipes.md` — copy-paste probe/crop/upscale/enhance/deskew
  recipes in three fallback tiers (sips on macOS, ImageMagick, Python PIL), plus
  pdftotext/pdfimages/pdftoppm for scanned PDFs and the tesseract cross-read invocation.
  Read when rule 1 or 2 fires, BEFORE improvising bash image commands.
- `scripts/tile.sh <image> <x> <y> <w> <h> [scale]` — one-shot crop+upscale that writes
  the tile outside the repo and prints its path; satisfies rule 2(a–b) in a single call,
  auto-selecting sips/ImageMagick/PIL by availability. Read the printed tile next and
  confirm the region (rule 2).
