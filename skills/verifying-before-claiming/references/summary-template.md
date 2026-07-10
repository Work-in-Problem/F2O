# Summary template: VERIFIED / NOT VERIFIED / ASSUMED

The three buckets are defined by the Layer 0 claim audit (CLAUDE.md §1). This file shows
how to fill them in. Every item from the acceptance checklist (SKILL.md rule 1) must land
in exactly one bucket — an item in no bucket was silently dropped.

## Bucket rules

**VERIFIED** — one line per claim: the claim, the command you ran, and the decisive output
line quoted verbatim. The decisive line is the single line that proves the claim — a
pass-count summary, an HTTP status, the asserted value — not a paraphrase and not the
whole log. If several lines matter, pick the most specific one. The command must have run
AFTER your last edit to the code it covers (CLAUDE.md §1).

**NOT VERIFIED** — one line per claim: the claim, the factual blocker, and an exact
command the user can copy-paste to verify it themselves (include env vars, cwd, or flags
they need). State what is missing, not how confident you feel — no softening adjectives,
no substitute phrasings; the bucket label carries the information.

**ASSUMED** — the assumption and why it was safe to proceed on it. Assumptions are things
you decided not to verify, not things you failed to verify (those are NOT VERIFIED).

## Worked example 1 — feature task

Task: "Add GET /users/:id/preferences returning the stored preferences; 404 on unknown
id; update the API docs."

```
**VERIFIED**
- Endpoint returns stored preferences — restarted the dev server (startup log shows the
  new route), then `curl -s localhost:3000/users/42/preferences` →
  `{"theme":"dark","locale":"en"}` with HTTP 200.
- 404 on unknown id — `curl -s -o /dev/null -w '%{http_code}' \
  localhost:3000/users/9999/preferences` → `404`.
- Existing suite still green after my last edit — `npm test` →
  `Tests: 47 passed, 47 total`.

**NOT VERIFIED**
- API docs render correctly on the docs site — the docs build needs the private
  `docs-theme` package not installed here. Run: `cd docs && npm ci && npm run build`.

**ASSUMED**
- The preferences JSON shape matches what the mobile client expects — inferred from
  `types/preferences.ts`; the spec did not include the client contract.
```

Note the NOT VERIFIED entry: blocker stated as a fact, command copy-pasteable, no
editorializing about how likely it is to pass.

## Worked example 2 — bug-fix task

Task: "`test_upload_retry` fails intermittently in CI — fix it."

```
**VERIFIED**
- Reproduced the flake before editing —
  `bash scripts/repeat-run.sh 10 -- pytest tests/test_upload.py::test_upload_retry` →
  `repeat-run: 6/10 passed, 4/10 failed`; first failing output:
  `AssertionError: assert 2 == 3` (retry counter read before the last attempt finished).
- Fix verified per constants.md C1/C2 — same command post-fix →
  `repeat-run: 10/10 passed, 0/10 failed`. Mechanism: the assertion raced the background
  retry thread; the fix joins the worker before asserting.
- Full suite green after the final edit — `pytest` →
  `128 passed, 2 skipped in 41.3s` (both skips are pre-existing
  `@skip(reason="needs S3")` markers, unrelated to this change).

**NOT VERIFIED**
- Behavior under CI's parallelism (`-n 8`) — pytest-xdist is not installed locally and
  CI uses a different worker count. Verify by pushing this branch and running:
  `gh run watch`.

**ASSUMED**
- None.
```

Notes on this example:

- The pre-fix red run is itself a VERIFIED claim — reproduction is evidence, quote it.
- The flake counts follow constants.md C1/C2 and are reported as
  "pre-fix k/N, post-fix 0/M", never "it passes now".
- The skip count is explained, not ignored — an unexplained skip belongs in the trap
  catalog (`references/output-traps.md`), not in a VERIFIED entry.
