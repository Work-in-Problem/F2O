# Spec extraction and reading selection — worked traces

One task followed from message to mid-task reconcile, then two reading-selection
traces at the end. Open this only when unsure how SKILL.md rules 2, 3, 5, 6, or 9–10
apply to a concrete case.

Fixture: `reportgen`, a small Python CLI (argparse) that renders YAML report files;
`--json` currently switches output from plain text to JSON.

## The request, verbatim

> Add a `--format` option to reportgen that accepts `json` or `table`. It should also
> be settable in `.reportgen.toml` as `format = "..."`, with the command-line flag
> winning when both are given. Update `--help` accordingly. Keep the existing `--json`
> flag working as a deprecated alias for `--format json`, with a deprecation notice on
> stderr. Update the usage section of the README and add a CHANGELOG entry. Whatever
> you do, exit codes must not change — two downstream cron jobs parse them.

Six sentences → eight explicit items: sentences 2 and 5 each carry two clauses (config
key + precedence; README + CHANGELOG). Rule 2's counting check passes: 6 sentences vs
8 items is a plausible clause split. 6 sentences vs 3 items would be the re-read signal.

## Extracted checklist (rule 2)

The task meets constants.md C3 (multi-component: CLI, config, renderer, tests, docs),
so the checklist lives in `WORKING_NOTES.md ## Plan` per finishing-the-turn rule 5 —
one list, shown here with rule 5's completion criteria already attached:

| # | Item | Completion criterion (as first written) | Source |
|---|---|---|---|
| 1 | `--format {json,table}` accepted | `reportgen --format json fixtures/basic.yml` exits 0 and stdout begins `{`; `--format table` prints the table header row | S1 |
| 2 | `format = "..."` honored from `.reportgen.toml` | new test `test_config_format_table` passes | S2, clause a |
| 3 | CLI flag beats config value | new test `test_flag_overrides_config` passes | S2, clause b |
| 4 | `--help` documents `--format` | `reportgen --help` output contains `--format {json,table}` | S3 |
| 5 | `--json` kept as deprecated alias | same fixture: `--json` stdout byte-identical to `--format json` stdout; stderr contains `deprecated` | S4 |
| 6 | README usage section updated | `grep -n -- '--format' README.md` hits inside the Usage section | S5, clause a |
| 7 | CHANGELOG entry added | top section of CHANGELOG.md mentions `--format` | S5, clause b |
| 8 | Exit codes unchanged | post-change exit-code matrix identical to the recorded baseline | S6 |
| 9 | Existing suite still green | `make test`: every pre-existing test passes (baseline reproduced) | implied |
| 10 | New behavior tested | items 2/3/5 criteria are themselves new tests, plus a unit test for an invalid `--format` value | implied |
| 11 | Lint green | `make lint` exits 0 | implied |
| 12 | Closure audit | every item above mapped to a tool result — SKILL.md rule 7, CLAUDE.md §1 | fixed final item |

Item 1's criterion is deliberately shown as first written — the reconcile below exposes
it as too weak and strengthens it.

## Unknowns triage (rule 3)

| Question | Class | Resolution |
|---|---|---|
| Which arg parser is in use? | workspace | `Read src/reportgen/cli.py` → argparse; `--json` is `store_true`, dest `json_output` |
| Does a config loader exist? | workspace | `Grep -rn toml src/` → `config.py: load_config()` already parses `.reportgen.toml`; line 41 REJECTS unknown keys with exit 1 — item 2 must extend the allowlist |
| Test framework and runner? | workspace | `Read pyproject.toml` + `Makefile` → pytest via `make test` |
| Existing deprecation-warning pattern? | workspace | `Grep -rin deprecat src/` → zero hits (receipt per search-first-context rule 7); mirror cli.py's existing stderr warnings instead |
| Current exit codes (item 8's baseline)? | workspace | answered by the rule 4 baseline runs below, before any edit |
| Which CHANGELOG heading style? (file mixes two) | workspace → Class A | mirror the most recent entries (search-first-context rule 5); one Decisions-ledger line, no question |
| Also expose the internal csv renderer (`export.py`) as a third `--format` value? | user-blocking | Class C — public API beyond the request. Parked in the single turn-end block per finishing-the-turn rule 2: (a) no, ship `json\|table` as asked — recommended; (b) add csv now. No checklist item depends on the answer, so nothing blocks. |

Five questions died to a read, a grep, or a run. One would-be question collapsed into a
Class A convention call. Exactly one survived as genuinely user-blocking — batched,
parked, non-gating.

## Discovery batch (rule 4)

One parallel batch, all before the first Edit:

- **Reads:** `cli.py`, `config.py`, `render.py`, `tests/test_cli.py`, `README.md`,
  `CHANGELOG.md`, `pyproject.toml`, `Makefile` — each under the constants.md C14
  cutoff, so whole files.
- **Greps:** `json_output` → 2 hits: `cli.py:60` (assigned into a local named
  `machine`) and `render.py:12` (renderer selection); plus the `toml` and `deprecat`
  greps from the triage table.
- **Baseline runs, recorded verbatim in `WORKING_NOTES.md ## State`:** `make test` →
  `47 passed in 4.1s`; exit-code matrix: plain run → 0, `--json` → 0, unknown flag → 2.

The transcript shows no Edit above this batch — SKILL.md rule 4's invariant, checkable.

## Risk-first order (rule 5)

| Pos | Item(s) | Why here |
|---|---|---|
| 1 | 1 (spike) | Highest uncertainty: whether `--format json` can share the `--json` render path decides the shape of items 2/3/5 — a wrong assumption must fail while nothing is built on it |
| 2 | 2 | Next-riskiest integration point: `load_config`'s unknown-key rejection (triage table) must accept the new key; unlocks 3 |
| 3 | 3 | Depends on 1 + 2; pins the precedence contract the tests will encode |
| 4 | 5 | Alias maps onto the now-proven `--format` path; its conflict semantics inherit item 3's contract |
| 5 | 8 | Verification gate: re-run the recorded exit-code matrix after all behavior edits, before docs — a regression is still only one edit deep. No destructive step exists in this plan, so rule 5's gate-before-destructive slot is empty — stated, not silently skipped |
| 6 | 9, 10, 11 | Tests are written red-first alongside items 1–5 (verifying-before-claiming rule 3); these items check off via the full `make test` + `make lint` pass after position 5 |
| 7 | 4, 6, 7 | Mechanical and zero-risk; written after behavior freezes so they are written once, not rewritten |
| 8 | 12 | The SKILL.md rule 7 walk |

## Mid-task reconcile (rule 6)

At item 3's checkoff the re-read of remaining items fires. Item 3's test runs produced
`--format json` output that looked subtly different from the legacy `--json` snapshot
read during discovery; because remaining item 5 claims byte-identity, the re-read
escalates the oddity into a probe diff before anything builds on the assumption. The
diff shows the legacy `--json` run also SUPPRESSES a two-line summary footer. Cause:
`cli.py:60` copies `args.json_output` into a local `machine`, and `cli.py:141` gates
the footer on `machine` — one hop past the `json_output` grep, so discovery listed the
assignment but the spike wired only `render.py:12`. Two plan consequences:

- Item 5 as written would fail honestly — but worse, item 1 is exposed as WRONGLY
  DONE: its criterion ("stdout begins `{`") passed while the footer made stdout
  unparseable, because the footer prints after the JSON body.
- The tempting local patch: special-case footer suppression inside the `--json` alias
  branch. That turns item 5 green while leaving `--format json` emitting broken JSON —
  a half-migrated state that items 4/6/7 would then document. Rejected per rule 6.

Plan update, made in the artifact before any further edit, with a one-line note in
`## Plan` recording the reopen and why:

1. Item 1 REOPENED; criterion strengthened to "`reportgen --format json
   fixtures/basic.yml | python -m json.tool` exits 0" — parseable, not `{`-prefixed.
2. Item 5's criterion clarified: byte-identical stdout AND the stderr notice present.
3. The fix goes at the shared seam: footer suppression moves into renderer selection so
   both spellings inherit it — one mechanism, not two.
4. Remaining items re-read once more: item 8's matrix is unaffected (the footer never
   touched exit codes); items 4/6/7 unaffected. No further invalidation. Resume at the
   reopened item 1.

Compressed lesson: the omission was caught only because items carried criteria
(rule 5), the re-read ran at a checkoff boundary instead of from memory (rule 6), and
the repair was a plan edit at the seam — never a patch around the invalidated
assumption.

---

# Reading selection — two traces (SKILL.md rules 9–10)

## Trace A — fake ambiguity, dissolved by one grep (rule 9 never runs)

Request: "Add caching to the products API." Two readings seem to exist — (a) HTTP
response caching in the route layer; (b) caching the product query at the data layer.
Rule 3's workspace-answerable arm runs first (search-first-context rule 11):
`grep -rin "cache" src/` → `src/lib/redisCache.ts` exports a wired `cached()`
wrapper, and `src/api/categories.ts` — the products route's sibling — already wraps
its query in `cached(..., ttl=300)`. The lookup RETURNED a settling fact: the repo
has one established caching mechanism and a sibling precedent at the query layer.
This was a missing grep, not a missing answer — rule 9's trigger never fires.
Implementation mirrors `categories.ts` (search-first-context rule 5); one
Decisions-ledger line (finishing-the-turn rule 10): "cached products query via
existing cached() helper, mirroring categories.ts". No enumeration table, no parked
question, no question to the user.

## Trace B — genuine Class A ambiguity: select, declare, one reading (rules 9–10)

Request: "Add a way to turn off colored output" in the `mycli` repo. Lookups first:
`grep -rin "color\|ansi\|chalk" src/ docs/ README.md` → `src/format.ts` applies ANSI
styling unconditionally; no existing disable path, nothing in the docs. A second
grep — receipt per search-first-context rule 7 — shows zero env-var or config-key
toggles anywhere in `src/`. The lookups returned and settled nothing → genuine
ambiguity. Enumerated readings (rule 9 step 1), written before evaluating any:

| Reading | Deliverable looks like |
|---|---|
| CLI flag | global `--no-color`, help-text entry, guard in `format.ts` |
| Env var | `NO_COLOR` honored in `format.ts`, README note |
| Config key | `color: false` in `.mycli.json`, loader change + README note |

Selection (step 2): repo evidence — the repo's only existing opt-out is
`--no-update-check`, a global CLI flag (and the receipted grep shows no env/config
toggles exist). The flag reading is corroborated; the env var carries an ecosystem
prior (`NO_COLOR` is a common convention), but step 2(a) ranks repo corroboration
above priors about what users usually mean, and the config reading would introduce a
first-of-its-kind mechanism. Reversibility and narrowness also favor the flag: no
loader change, no new config surface. Divergence test (step 3): all three readings
are additive, none removes behavior or needs a Class B step, and the shared core —
the guard in `format.ts` — is most of the deliverable, so a wrong guess reverts a
contained slice. Class A → select silently, no park.

Declaration (step 4), written at selection time, not in the closing draft:

- Scope-contract sentence (scoping-code-changes rule 1): "Running any command with
  `--no-color` produces zero ANSI escape codes on stdout, the flag appears in
  `--help`, and existing tests pass."
- Decisions-ledger entry (content per rule 9; mechanics finishing-the-turn rule 10):
  "'a way to turn off colored output' → global `--no-color` flag, mirroring the
  repo's only opt-out `--no-update-check` (grep receipt: no env/config toggles
  exist); runner-up rejected: honoring the `NO_COLOR` env var."

Rule 10 polices the diff: exactly ONE disable mechanism. Shipping the flag AND the
env var "to be safe" is the union hedge — untraceable hunks per scoping-code-changes
rule 1. Shipping only the `format.ts` guard and closing with "want me to wire a flag
or an env var?" is the intersection-plus-offer finishing-the-turn rule 4 forbids.
And had a later read surfaced a doc line promising `NO_COLOR` support, that
contradiction is a rule 6 reconcile — re-run rule 9's selection with the new
evidence; deleting the doc line to fit the guess is forbidden
(verifying-before-claiming rule 10).
