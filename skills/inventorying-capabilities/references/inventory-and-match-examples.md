# Inventory-and-match examples

Rule numbers refer to `../SKILL.md`. Tool calls are abbreviated. Match results shown
here live inline in your reasoning (or in the existing `WORKING_NOTES.md` §3 sections
when notes are live) — never in a standalone inventory file or table artifact
(CLAUDE.md §3); the only durable output is the Decisions-ledger line for deliberate
non-use (SKILL.md rule 1).

## The five-category task-feature taxonomy (rule 1)

Decompose the task into features along these five categories, then check each against
the session's tool surface. The keywords are the domain nouns to scan tool names, MCP
server names, and instruction blocks for before recording "no match — core tools".

| Category | What it covers | Matching-keyword examples |
|---|---|---|
| Deliverable format | Non-text outputs the user will receive | pdf, docx, xlsx/sheet, pptx/slides/deck, image, video, audio, 3d, site/website, artifact |
| Data source | Where answer-critical data lives | query, db/database, records, search, fetch, memory, docs, transcript, registry |
| External system | A system the task must drive | browser/chrome/navigate, computer/click/type, deploy, publish, schedule/cron, repo/PR |
| Output channel | Where results must land beyond the repo | send, message, post, notify, mail, slack, upload |
| Observation target | Something to observe rather than compute | screenshot, read_page, console, network, logs, status, snapshot |

One feature can hit two categories (a status page is both data source and observation
target); matching either way reaches the same tool. A feature whose keywords hit an MCP
server's name or instruction block routes through that server by default (rule 1).

## Trace 1 — Bash-curl improvisation vs the listed fetch/browser tool

Task: "Check what our pricing page currently shows and update the README table to
match." Session lists a browser bridge (`mcp__chrome__navigate`, `mcp__chrome__read_page`)
plus a deferred `WebFetch`.

BAD
  Bash  curl -s https://example.com/pricing     # 403 — bot protection
  Bash  curl -A "Mozilla/5.0 ..." ...           # still blocked; JS-rendered anyway
  (message) "Could you paste the pricing page contents?"
                                                # rule 2 violated (improvised route past
                                                # two listed tools), then rule 5 violated
                                                # (user's hands asked for a tool-reachable
                                                # observation)

GOOD
  (rule 1 match: observation target "live web page" → chrome bridge / WebFetch)
  ToolSearch "select:WebFetch"                  # deferred → loaded (rule 3)
  WebFetch https://example.com/pricing          # rendered content, prices extracted
  Edit  README.md

Rules fired: 1 (the match names the tool before the route is chosen), 2 (listed wins
over curl), 3 (deferred means available), 5 (never reached — no ask needed).

## Trace 2 — False "no tool for X" vs one batched deferred-schema load

Task ends with: "...and deliver the requirement summary as summary.pdf; we'll also want
a .docx for legal later." The main tool list has no document tool, but the DEFERRED list
names `mcp__docs__render_pdf` and `mcp__docs__render_docx`.

BAD (variant A — false unavailability)
  (final message) "I can't generate PDFs in this environment — here's summary.md; you
  can convert it with pandoc."                  # rule 4 violated: availability claim
                                                # with no inventory check; rule 3
                                                # violated: deferred list never scanned

BAD (variant B — one error demotes)
  mcp__docs__render_pdf ...                     # InputValidationError — schema not loaded
  Bash  pandoc summary.md -o summary.pdf        # improvised fallback; rule 2's corollary
                                                # violated: the error meant "load and
                                                # retry", not "tool broken"

GOOD
  (rule 1 sweep read the deferred list; match: deliverable formats "pdf" + "docx"
   → both render tools; both anticipated, so ONE batched load)
  ToolSearch "select:mcp__docs__render_pdf,mcp__docs__render_docx"
  mcp__docs__render_pdf ...                     # summary.pdf written
  Bash  file summary.pdf                        # "PDF document" — evidence per the
                                                # CLAUDE.md §1 claim audit

Rules fired: 3 (deferred means available; one batched discovery call, schema loaded
before invoke), 4 (no unavailability claim without checking the deferred list).

## Trace 3 — Late format pivot: renamed CSV vs a rule 6 re-match

Task: a long code task; after all tests pass, the prompt's final requirement activates:
"export the checklist as checklist.xlsx". The installed-skills list has named an xlsx
skill since session start — unused and unneeded through the whole build phase.

BAD
  Bash  cp checklist.csv checklist.xlsx         # renamed CSV — not a workbook; any
                                                # consumer that unzips it fails
  (final message) "Exported checklist.xlsx."    # claim with no format evidence

GOOD
  (rule 6: new deliverable format surfaced → re-match this ONE feature, not the full
   sweep; match: "xlsx" → installed xlsx skill)
  Skill xlsx                                    # produces a real workbook
  Bash  unzip -l checklist.xlsx                 # xl/worksheets/sheet1.xml listed —
                                                # decisive output for the §1 audit

Rules fired: 6 (the feature event, not a call count, triggers the re-match), 2 (the
purpose-built skill beats the rename/convert improvisation). Evidence standards for the
"exported" claim are `verifying-before-claiming`'s and CLAUDE.md §1's — shown here only
as the proving command.
