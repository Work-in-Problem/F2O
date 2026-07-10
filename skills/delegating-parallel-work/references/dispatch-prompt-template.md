# Dispatch prompt template — GOOD and BAD worked examples

SKILL.md rule 6 requires six items in every dispatch prompt: (a) one-sentence
objective, (b) exact absolute paths, (c) session context pasted inline, (d) explicit
"Do not touch" list, (e) done-condition as command + expected output, (f) "Report:"
return contract. Below: one GOOD prompt with every item annotated inline, then one
realistic BAD prompt with each defect labeled and its downstream failure named.

## GOOD dispatch prompt

Scenario: monorepo at `/Users/dev/acme`. The orchestrator's workstream table assigned
the `billing` package migration to this agent. The `⟨…⟩` marker lines are annotations —
strip them before dispatching; everything else is the literal prompt.

```
⟨item a — one-sentence objective, including the invariant to preserve⟩
Migrate the billing package from formatMoney(amount) to the new
formatMoney({ amount, currency }) call shape, with behavior unchanged and its
test suite passing.

⟨item b — exact absolute paths: working area, entry points, test location⟩
Work only inside /Users/dev/acme/packages/billing/. Known call sites:
- /Users/dev/acme/packages/billing/src/invoice.ts
- /Users/dev/acme/packages/billing/src/refund.ts
Tests live in /Users/dev/acme/packages/billing/test/.

⟨item c — session context PASTED inline: the convention was decided earlier in
the orchestrator's conversation, so it is restated in full, never referenced⟩
Convention decided for this migration (apply as written, do not re-derive):
currency always comes from the Invoice.currency field, never a global default.
New call shape, exactly:
    formatMoney({ amount: cents, currency: invoice.currency })
The old positional call formatMoney(cents) must not remain anywhere in this
package. The new signature already exists in shared/money.ts — consume it,
do not modify it.

⟨item d — explicit do-not-touch list: names concrete paths, not "anything else"⟩
Do not touch: /Users/dev/acme/packages/shared/ (owned by the orchestrator),
any other package under /Users/dev/acme/packages/, package-lock.json, CI config.

⟨item e — done-condition: a runnable command plus its expected output⟩
Done when both hold:
1. `cd /Users/dev/acme/packages/billing && npm test` exits 0 with all tests
   passing (tests run > 0).
2. `grep -rn "formatMoney([^{]" /Users/dev/acme/packages/billing/src` returns
   no hits.

⟨item f — return contract: structured, checkable, machine-greppable "Report:"⟩
Report: files changed (absolute paths); commands run with exit codes; the final
grep output; open issues as a list (write "none" if empty).
```

Why the annotations matter: (a) gives the agent the success criterion, not just the
verb; (b) removes cwd ambiguity; (c) is the anti-deixis item — the sub-agent sees NONE
of the orchestrator's conversation; (d) is what makes one-writer-per-file (rule 5)
hold in practice; (e) turns "done" into evidence; (f) is what rule 9's synthesis gate
audits against.

## BAD dispatch prompt (realistic counterexample)

```
Migrate the billing package like we did earlier with catalog — same idea, follow
the pattern from before for the currency handling. The files are in
packages/billing/src (invoice and refund mainly). Don't break anything else.
Let me know how it goes.
```

Every defect, the rule 6 item it violates, and the downstream failure it causes:

| Defect (quoted) | Item violated | Downstream failure |
|---|---|---|
| "like we did earlier", "the pattern from before" | (c) inlined context | The sub-agent cannot see this conversation. It invents its own currency convention — an incompatible helper API that collides with the other streams at merge time. |
| "packages/billing/src" (relative path) | (b) absolute paths | The agent's cwd differs from yours. It burns calls searching, or edits a similarly named directory in the wrong tree. |
| No objective stating behavior must be unchanged | (a) objective | The agent optimizes for "migrate" alone and rewrites failing tests to match its new behavior — test integrity violation the orchestrator must catch and undo. |
| "Don't break anything else" (no concrete list) | (d) do-not-touch | The agent "helpfully" edits shared/money.ts too — now two concurrent writers on one file, lost updates at merge (rule 5 violated). |
| No done-condition | (e) command + expected output | The agent stops at compile-success and reports "should work" — the orchestrator gets no evidence and must redo the verification, doubling cost. |
| "Let me know how it goes" | (f) return contract | A prose blob comes back: no file list, no exit codes. Rule 9's synthesis gate has nothing to check claims against. |

Note: `scripts/lint-dispatch-prompt.sh` catches four of these mechanically — the
deictic phrase "the pattern from" (and "from before"), the missing absolute path, the
missing "Do not touch" list, and the missing "Report:" contract. Items (a) and (e)
still require the eye check.
