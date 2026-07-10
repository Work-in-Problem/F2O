# Workstream table examples

Table format (SKILL.md rule 1): `stream | files/dirs touched | read-only or write |
depends-on`. A stream is write-disjoint-independent iff its write set intersects no
other stream's write set AND its depends-on column is empty or names only finished
streams. Three worked partitions follow: a clean fan-out, a shared-file seam with the
three legal resolutions, and an entangled refactor correctly kept serial.

## Example 1 — clean 5-package fan-out (verdict: fan out)

Task: "Migrate all packages to the new formatMoney API; all tests must pass." Monorepo
at `/Users/dev/acme`; the new signature already landed in `shared/money.ts` in an
earlier commit, so nothing depends on an unfinished stream.

| stream | files/dirs touched | read-only or write | depends-on |
|---|---|---|---|
| S1 billing | /Users/dev/acme/packages/billing/ | write | — |
| S2 catalog | /Users/dev/acme/packages/catalog/ | write | — |
| S3 auth | /Users/dev/acme/packages/auth/ | write | — |
| S4 email | /Users/dev/acme/packages/email/ | write | — |
| S5 reports | /Users/dev/acme/packages/reports/ | write | — |
| S0 orchestrator | repo-level integration tests (run only) | read-only | S1–S5 |

Classification: S1–S5 are write-disjoint-independent — five separate directories, each
one module with its own test suite, each a coherent deliverable at the C4 per-stream
floor. C4 is met. Decision: dispatch S1–S5 in one burst (SKILL.md rule 7); while they
run, the orchestrator prepares the union-level verification commands (repo build +
integration suite) it will run itself at the rule 9 gate.

## Example 2 — two features sharing a utility file (verdict: fan out, after a seam decision)

Task: feature A (rate limiting in `/Users/dev/acme/src/api/`) and feature B (retry
logic in `/Users/dev/acme/src/worker/`), and BOTH need a new backoff helper that does
not exist yet. The naive partition:

| stream | files/dirs touched | read-only or write | depends-on |
|---|---|---|---|
| A rate-limit | src/api/, **src/shared/utils/backoff.ts** | write | — |
| B retry | src/worker/, **src/shared/utils/backoff.ts** | write | — |

Illegal: both streams write `backoff.ts` — two concurrent writers on one file (rule 5),
and each agent would invent its own backoff API. Three legal resolutions:

- **Merge** — one sub-agent owns both features plus the helper. Legal, but only if the
  combined work still fits the sub-task sizing band; here it likely exceeds it, and all
  parallelism is lost.
- **Retain** (recommended default here) — the orchestrator writes `backoff.ts` FIRST,
  then dispatches A and B in parallel with the helper's final signature pasted into
  both prompts (rule 6c). Both streams become write-disjoint; parallelism preserved;
  the shared convention is single-sourced.
- **Sequence** — agent A lands `backoff.ts` + feature A; agent B is dispatched
  afterward with A's landed helper signature pasted in. Legal, keeps each prompt small,
  but A→B parallelism is lost.

Fixed table under "retain":

| stream | files/dirs touched | read-only or write | depends-on |
|---|---|---|---|
| S0 orchestrator | src/shared/utils/backoff.ts | write | — |
| A rate-limit | src/api/ | write | S0 |
| B retry | src/worker/ | write | S0 |

S0 completes, then A and B dispatch in one burst.

## Example 3 — entangled refactor (verdict: do NOT fan out — keep it serial)

Task: rename the domain concept `Order` to `Purchase` — the core type, the DB column
mapping, serializers, API DTOs, and every consumer across `/Users/dev/acme/src/`.
Candidate per-layer partition:

| stream | files/dirs touched | read-only or write | depends-on |
|---|---|---|---|
| T1 core type | src/domain/types.ts | write | — |
| T2 persistence | src/db/, src/domain/types.ts (imports change) | write | T1 |
| T3 serializers | src/serializers/, src/domain/types.ts | write | T1 |
| T4 API DTOs | src/api/dto/, src/serializers/ | write | T1, T3 |

Classification: entangled. Every stream depends on T1's unfinished type change; T2–T4
overlap on write sets; nothing compiles until the chain lands. Zero write-disjoint
pairs exist at the C4 floor — so C4 is NOT met, even though the rename touches 40+
files. 40 files is not 40 workstreams, for the same reason 3 files is not 3 workstreams
(rule 1). And even a formally disjoint split would hit the seam risk from SKILL.md's
Do-not-over-apply: parallel agents would have to co-invent the new naming/type shape
mid-flight. Decision: execute serially, compiler-guided — change the core type first
and let the type errors enumerate the remaining work.
