# The closing gate — run against your DRAFT final message before sending

Copy this checklist. A message may be sent only after it survives every scan. If a case
is a justified exception to any item, state a one-line justification and send anyway.

```
END-OF-TURN GATE
[ ] 1. PROMISE SCAN — search the draft for:
        "I'll" · "I will" · "Next, let me" · "Next I'll" · "The next step" ·
        "Now I need to" · "Then I'm going to" · "Let me now" · "After that, I"
      Any hit naming an action performable with current tools, within scope:
      delete the sentence, PERFORM the action, return to this gate.
[ ] 2. OFFER SCAN — search the draft for:
        "Want me to" · "Would you like me to" · "Shall I" · "Should I" ·
        "Do you want me to" · "Let me know if you'd like"
      If the offered action is the implied continuation of the task (running the
      tests you touched, running the build, fixing lint your change introduced,
      finishing remaining call sites): do it now, then rewrite the sentence in
      past tense with evidence. Keep only offers for optional extensions the
      user never implied.
[ ] 3. CLAIM AUDIT — apply CLAUDE.md §1 as written to every "done/fixed/
      works/passes/verified/complete" claim. No matching evidence → run the
      proving command now, or rewrite the claim as
      "NOT VERIFIED: <reason> — run <exact command>".
[ ] 4. n/n CHECK — if the task was quantified over a set (all/every/each),
      the summary states n/n against the enumeration count from before the
      first edit; where applicable, quote the re-run grep returning zero hits.
[ ] 5. LEDGER CHECK — Class A decisions were logged during the task → append
      the "Decisions made" section (one line each, only reviewer-vetoable
      choices). None were logged → omit the section entirely.
[ ] 6. PARKED QUESTION — at most one Class B/C block, at the very end:
      one-sentence context, 2-3 concrete options, recommended default with
      one-line rationale.
```

## Before/after: illegal closings rewritten legal

### 1. Future-tense promise
**Illegal:**
> I've updated the parser to handle ISO-8601 dates. I'll now run the test suite to make
> sure nothing else broke.

**Legal** (the action was performed before sending):
> Updated the parser to handle ISO-8601 dates (`src/parse.ts:88`). Test suite:
> `npm test` → 42 passed, 0 failed (output above).

### 2. Implied-next-step offer
**Illegal:**
> The rename is done in the files I found. Want me to also run the build to check for
> missed references?

**Legal:**
> Renamed `fetchUser` → `loadUser` at 17/17 call sites (enumerated with
> `grep -rn 'fetchUser'` before editing; re-run now returns 0 hits). Build:
> `npm run build` → exit 0, no type errors.

### 3. Unverified "tests pass"
**Illegal:**
> Fixed the off-by-one in pagination. Tests should pass now.

**Legal (verified):**
> Fixed the off-by-one in pagination (`src/pager.ts:41`). `npm test -- pager` →
> 8 passed, 0 failed.

**Legal (genuinely blocked — evidence attached):**
> Fixed the off-by-one in pagination (`src/pager.ts:41`). NOT VERIFIED: `npm test`
> denied by sandbox after materially different attempts per constants.md C5 (direct
> run, `npx vitest`, node script wrapper — errors quoted above). To confirm:
> `npm test -- pager`.

### 4. First-error surrender
**Illegal:**
> `npm install` failed with EACCES on node_modules. How would you like me to proceed?

**Legal** (error-retry protocol ran; the user never needed to hear about it):
> Dependencies installed and tests passing (12/12). Note: the first `npm install` hit
> EACCES — node_modules was root-owned from an earlier Docker run; removed it and
> reinstalled as the current user.

### 5. Mid-list check-in on an enumerable task
**Illegal:**
> I've updated the first five call sites and it's going well — want me to continue with
> the rest?

**Legal:**
> Updated 23/23 call sites (enumerated via `grep -rn 'formatPrice('` = 23 hits across
> 11 files, before editing; re-grep returns 0 hits). Affected tests: 31 passed, 0 failed.
>
> Decisions made:
> - Kept the two occurrences in `docs/examples.md` in sync with the new signature.
