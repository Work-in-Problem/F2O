# Reopen recipes — per-format mechanics for producing-deliverables rule 8

One principle, applied per format: reopen the artifact with an INDEPENDENT reader —
never the library object or buffer that generated it. The reopened content is the
CLAUDE.md §1 evidence; the generating script's exit code is not. Any re-export,
re-render, or re-save voids a prior reopen and re-triggers rule 8 (the artifact analog
of verifying-before-claiming rule 7). When a format skill (xlsx/docx/pptx/dataviz) is
loaded, its mechanics win over the recipes below — these are the fallback.

## xlsx

**The trap.** openpyxl NEVER evaluates formulas. `load_workbook(path)` returns formula
STRINGS; `load_workbook(path, data_only=True)` returns the values cached by the last
spreadsheet app that recalculated the file — and a file openpyxl itself wrote has no
cache, so every formula cell reads `None`. Two passing-looking non-checks, by name:
reading back your own formula strings and calling them "verified totals", and treating
a wall of `None`s as "no errors found".

**Recipe A — recalculate with LibreOffice headless.**

```bash
soffice --headless --convert-to xlsx --outdir /tmp/reopen produced.xlsx
```

LibreOffice computes formula results while saving (an openpyxl-authored file has no
cached results, so it must calculate them). Then read the EVALUATED values:

```python
from openpyxl import load_workbook
wb = load_workbook("/tmp/reopen/produced.xlsx", data_only=True)  # now has a cache
```

Single-sheet shortcut: `soffice --headless --convert-to csv --outdir /tmp/reopen
produced.xlsx` exports the first sheet with formulas evaluated. Caveat for files NOT
authored this session: an existing cache may be stale — prefer Recipe B's comparison.

**Recipe B — cross-check written values (always available).** Compare the cells the
workbook should show against independently computed aggregates (e.g. pandas over the
same cleaned source — rule 4's second path). If no recalculation engine exists in the
environment, this comparison is the admissible evidence: name the cells checked and
quote both sides.

**Also while reopened:** cross-foot totals (rule 4), and check cell number formats
against the rule 6 policy — a policy that dies in formatting is a defect.

## pptx

Render every slide to an image and VIEW every image (Read tool on the PNGs) — text
extraction alone cannot catch overflow or overlap:

```bash
soffice --headless --convert-to pdf --outdir /tmp/reopen deck.pptx
pdftoppm -png -r 110 /tmp/reopen/deck.pdf /tmp/reopen/slide   # poppler
```

No poppler → any available pdf→png path (e.g. pypdfium2, pdf2image). The requirement is
viewed pixels of every slide, not a specific tool.

What to look for, per slide:

- text overflowing its box or the slide edge; "..." truncation in titles or labels
- overlapping elements — legend covering bars, callouts covering data, images over text
- leftover placeholder text ("Click to add title", "Lorem", "TODO", template names)
- clipped or off-slide elements; unreadably small labels
- chart values and axis labels vs the rule 7 sweep and the rule 6 policy
- slide order, numbering, and section headers vs the rule 1 checklist

## docx / pdf

Re-extract the text with an independent reader and read it end to end:

- docx: python-docx — iterate paragraphs AND tables (tables are the classic miss); or
  `soffice --headless --convert-to txt --outdir /tmp/reopen doc.docx`.
- pdf: `pdftotext -layout doc.pdf -` (poppler), or pypdf.

Confirm against the artifact's own contract: every required section present and in
order (rule 1 checklist); every figure/table the prose references actually exists;
every extracted number matches the rule 7 sweep; the rule 6 policy survived rendering
(a "14%" the template rendered as "0.14" is exactly what this catches). When layout is
part of the deliverable (letterhead, multi-column, embedded charts), also convert to
pdf and render pages to images as in the pptx recipe.

## csv

Round-trip parse with a fresh reader using the intended consumer's settings (delimiter,
quoting, encoding). Confirm: parsed row count matches the written count; min/max of key
numeric columns match rule 4's traces; dates render in the declared grain; no mojibake
in text columns. A csv that parses differently than it was written is a defect even if
the bytes were written "successfully".

## markdown / html report

Re-read the FILE from disk top to bottom as a reader would — never your generation
buffer. html: render it (or extract text) and check internal links/anchors resolve.
Every number in the re-read text must match the rule 7 sweep; every section, the rule 1
checklist.
