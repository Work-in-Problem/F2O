# Worked examples — one good-vs-bad pair per trap

Each pair shows the transcript shape that ships the bug (BAD), the shape the skill
requires (GOOD), which rule fires, and the tool call that satisfies it. Tool calls are
abbreviated; rule numbers refer to `../SKILL.md`.

## Trap 1 — Stale library API (training-era syntax in a newer-major repo)

Task: "Add input validation for the /signup route." Repo pins zod v4; training data is
full of v3 idioms.

BAD
  Write src/routes/signup.ts      # z.string().nonempty(...) — v3 idiom, from memory
  Bash  tsc --noEmit              # error: method renamed in v4; backtrack, re-edit

GOOD
  Read  package.json              # "zod": "^4.1.0" — installed major resolved from disk
  Grep  "from ['\"]zod" src/      # how THIS repo already uses it
  Read  src/routes/login.ts       # nearest existing usage — mirror its idioms
  Write src/routes/signup.ts
  Bash  tsc --noEmit              # green on the first pass

Rules fired: 1 (volatile-fact gate — an external-library API shape is never written from
memory) and 6 (environment-first — the manifest names the installed major before import).

## Trap 2 — Hidden second call site in scripts/

Task: "Add a currency parameter to formatPrice()."

BAD
  Read  src/lib/price.ts (offset 40, limit 30)   # keyhole view of the function
  Edit  src/lib/price.ts                         # signature changed
  Edit  src/components/Cart.tsx                  # the one caller already known
  Bash  pnpm test                                # green — but scripts/monthly-report.ts
                                                 # is untyped and now crashes at runtime

GOOD
  Read  src/lib/price.ts                         # whole file (rule 2a)
  Bash  scripts/impact-scan.sh formatPrice .     # caller: 3, test: 1 —
                                                 # scripts/monthly-report.ts surfaces
  Read  scripts/monthly-report.ts                # confirms it passes a bare number
  Edit  all three callers + the pinning test; then run the suite

Rule fired: 2 (pre-edit checklist — repo-wide grep of the exact symbol before the first
Edit; the classic misses are scripts/, jobs/, and the test pinning the old signature).

## Trap 3 — AUTO-GENERATED decoy file

Bug report: "Requests send the wrong auth header."

BAD
  Grep  "authorization" src/         # hit #1: src/gen/apiClient.ts
  Edit  src/gen/apiClient.ts         # fix lands in a file the build step overwrites
                                     # next build regenerates it; the bug returns

GOOD
  Grep  "authorization" src/         # 2 hits: src/gen/apiClient.ts, src/api/client.ts
  Read  src/gen/apiClient.ts (head)  # header: "AUTO-GENERATED — DO NOT EDIT"
                                     # discard hit #1; declare src/api/client.ts
                                     # authoritative
  Read  src/api/client.ts
  Edit  src/api/client.ts
  Bash  npm run build && npm test    # fix survives regeneration

Rule fired: 4 (grep-triage — never act on hit #1; a file headed AUTO-GENERATED is never
the edit target).

## Trap 4 — Wrong-test-framework convention miss

Task: "Write tests for utils/slugify." Vitest monorepo, @app/* path aliases, runner is
`pnpm vitest run`.

BAD
  Write utils/slugify.test.ts        # jest globals, jest.mock, relative imports — priors
  Bash  npm test                     # no such script; wrong framework AND wrong command,
                                     # both guessed

GOOD
  Glob  **/*.test.ts                              # find the nearest test of the same kind
  Read  utils/__tests__/formatDate.test.ts        # vitest imports, @app/* aliases,
                                                  # shared renderWithProviders helper
  Read  package.json                              # scripts.test → "vitest run"
  Write utils/__tests__/slugify.test.ts           # mirrors the sampled file
  Bash  pnpm vitest run utils/__tests__/slugify.test.ts   # green

Rules fired: 5 (convention sampling — never author a new-kind file from priors) and
6 (environment-first — read the scripts section before guessing the command).

## Trap 5 — Deleted load-bearing workaround

Task: "This sleep(250) before the retry looks like leftover debug code — clean it up."

BAD
  Read  src/net/retry.ts
  Edit  src/net/retry.ts             # sleep deleted; looks harmless
  Bash  npm test                     # green today — the reintroduced upstream race is
                                     # flaky, not deterministic, so the suite lies

GOOD
  Bash  git log -S "sleep(250)" --oneline -- src/net/retry.ts
        # a1b2c3d "workaround for upstream race, see #142;
        #          removing reintroduces flaky 502s"
  Bash  git blame -L 41,44 src/net/retry.ts      # the line belongs to that commit
  # decision: preserve behavior and cite a1b2c3d/#142; replace only knowingly,
  # with a test that pins the race

Rule fired: 8 (Chesterton's fence — history before deletion; one green run is not
evidence against a documented race, cf. `verifying-before-claiming` rule 4).
