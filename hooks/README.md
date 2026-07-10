# Fable2Opus Layer 2 — enforcement hooks (operator doc)

Layer 0/1 are prose, and prose adherence decays as context grows. This layer is a
deterministic backstop: a single Stop hook, `claim_gate.py` (Python 3, stdlib only),
wired in `.claude/settings.json`, that runs every time the model tries to end its turn.
It enforces two already-owned rules — it defines **no policy of its own**:

| Check | What it blocks | Prose owner |
|---|---|---|
| **Promise scan** | A closing message that ENDS on a future-tense work commitment ("I'll now …", "I will now …", "Next, let me …", "Next I'll …", "The next step is to …", "Now I need to …", "Let me now …"): the matched promise must sit in the message's final sentence/line — nothing but whitespace after its sentence ends. "let me know …" requests and sentences that hand the action to the user (a second-person marker after the phrase, e.g. "… is your call") do not count. The block reason quotes the promise and instructs: perform the action now, then close per `finishing-the-turn` rule 3. | `finishing-the-turn` rule 3 |
| **Claim gate** | A completion claim (the CLAUDE.md §1 word list: done, fixed, works, passes, verified, complete — word-boundary, case-insensitive, negations and quoted/code spans excluded) when the transcript shows an Edit/Write/NotebookEdit on a product file AFTER the last plausibly-verifying Bash run (test/pytest/make/npm/pnpm/yarn/go test/cargo/build/check/lint/tsc/run_tests/repeat-run). The block reason instructs: re-run the relevant verification, then re-send. | CLAUDE.md §1 (an edit voids every earlier passing check) |

Excluded from "product file": `WORKING_NOTES.md` (the one notes file, CLAUDE.md §3),
anything under `.claude/`, and `evals/results/`.

On block, the hook prints `{"decision": "block", "reason": "…"}` to stdout and exits 0
— the documented Stop-hook contract (verified against code.claude.com/docs/en/hooks and
/hooks-guide, 2026-07-10). On allow it prints nothing and exits 0. It never exits
non-zero and never writes stderr.

## Deliberate false-negative bias

False negatives are acceptable; false positives are not. Known allow-paths, all
intentional:

- No plausibly-verifying Bash anywhere in the transcript → allow (verification may have
  happened through a non-Bash channel, or the change has no runtime surface — e.g. a
  docs-only edit).
- Negated or hedged claims ("not done", "not verified", "incomplete", "to be done",
  "ASSUMED: …") → not counted as claims.
- Claim words inside fenced/inline code, blockquotes, or short double-quoted spans →
  stripped before scanning.
- Non-English closing messages → the phrase lists are English; no match, no block.
- A generous verification matcher (any `npm …`/`make …`/`check`/`build` command counts)
  → treats borderline runs as verification, i.e. leans allow.
- A promise phrase followed by more prose (its sentence is not the message's final
  sentence — e.g. past-tense evidence on the next line) → not counted; only a promise
  the message literally ends on blocks.
- "Next, let me know …" / "Let me now know …" → excluded by lookahead (a user-facing
  request, not a work commitment); a second-person marker after the phrase inside its
  sentence ("… which is your call") also skips the match as a hand-off.
- Transcript-fallback text (no `last_assistant_message` in the input): only the NEWEST
  content-bearing main-chain assistant entry is scanned; if it is tool_use-only, the
  hook allows rather than judging an earlier message whose promises those later tool
  calls plausibly executed.
- Residual false-positive risk, accepted (each costs exactly one acknowledge-and-resend
  cycle — see safety valves):
  - the transcript file is written asynchronously and can lag; in the rare case the
    final verification run is not yet on disk when Stop fires, the claim gate can block
    a genuinely verified close;
  - a promise phrase and its past-tense retraction fused into ONE final sentence
    ("Now I need to confirm nothing else broke — and I did: …") still blocks: the
    promise does sit in the final sentence, and a regex cannot parse the retraction.
    Splitting the evidence into its own sentence/line passes.

## Safety valves

- **`FABLE2OPUS_HOOKS_OFF=1`** — the operator escape hatch: the hook exits 0
  immediately. Set it in the environment of any session where enforcement must be off.
- **`stop_hook_active`** — when true (Claude is already continuing because a Stop hook
  blocked), the hook exits 0 immediately. Net effect: at most one block per stop chain;
  a false positive costs one extra round-trip, never a loop. Claude Code additionally
  hard-caps consecutive Stop-hook blocks at 8 (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`).
- **Any parse error, missing transcript, or unknown format** — exit 0 silently. The
  hook must never brick a session.
- Reason text is capped (700 chars) so a block never floods the model's context.

Escape hatch (one, hook-wide): if a specific session justifies bypassing enforcement,
set `FABLE2OPUS_HOOKS_OFF=1` for that session and note why in the session — never edit
the hook or settings to skip it silently.

## How to test

Full suite (19 cases — clean close, promise endings, non-terminal and handed-off
promises, "let me know" closings, tool_use-only fallback, edit-after-verify ordering
both ways, negation, quoted spans, notes-file exclusion, sidechain exclusion,
garbage/missing transcripts, both safety valves):

```bash
bash .claude/hooks/tests/run_hook_tests.sh
```

Manual smoke test (expects a block JSON on stdout, exit 0):

```bash
printf '%s' '{"hook_event_name":"Stop","stop_hook_active":false,"transcript_path":"/dev/null","last_assistant_message":"I will now run the tests."}' \
  | python3 .claude/hooks/claim_gate.py
```

To inspect the wiring inside a live session, run `/hooks`. Settings edits are picked up
by the file watcher; restart the session if they do not appear.

## WARNING — eval arms

**Arm-A (bare) eval runs must not have these hooks active.** The hooks are part of the
treatment being measured, exactly like the skills. This is automatic under the standard
procedure: per `evals/README.md` §5, every run executes in a `$RUN_DIR` copied OUTSIDE
this repo, and project hooks in `.claude/settings.json` only apply inside this project
directory. Arm A must never run inside this repo or a child directory (evals/README.md
§3) — that rule now protects against hook leakage too, not just CLAUDE.md/skills
leakage. Whether arm B copies `.claude/settings.json` + `.claude/hooks/` into its
`$RUN_DIR` (hooks-as-treatment) is the eval owner's call; the §5 copy list currently
includes only `CLAUDE.md`, `constants.md`, and `.claude/skills/`.

## Documentation edits do not re-arm the gate (2026-07-10)

Edits to markdown/text files (`.md`, `.markdown`, `.rst`, `.txt`) are excluded from
the "edit voids verification" arming set, alongside WORKING_NOTES.md, `.claude/`,
and `evals/results/`. Rationale: docs have no runtime surface
(verifying-before-claiming rule 2's bottom rung) and no hook-detectable
verification command, so arming on them produced false blocks on wrap-up
messages sent after status-doc updates — first observed when this hook blocked
its own author's project summary after PLAN.md edits. Accepted false negative:
a docs-only task claiming done without re-reading the docs slips through.
Covered by tests `md_edit_after_verify` (allow) and `md_plus_code_edit` (block).

Second incident, same day: session-temp/scratchpad paths (`/private/tmp/`, `/tmp/`,
`/var/folders/`, any `/scratchpad/` segment) are likewise excluded from arming —
a PDF-source HTML edited in the scratchpad re-armed the gate although the render
was visually verified after the edit; render-and-look verification is invisible
to the verify-command regex, so location is the reliable signal. Repo-path
`.html` still arms (may be product code). Tests: `tmp_html_edit` (allow),
`repo_html_edit` (block).

