# Triage worked examples — situation → class → action

These illustrate the Class A/B/C triage defined in CLAUDE.md §2 (the table itself lives
there; if this file ever disagrees with it, §2 wins). Class A = decide silently + one
ledger line if reviewer-vetoable; B/C = park at turn end with options and a default.

1. New helper could live in `utils/` or `lib/` (both exist) → **A** → follow the
   directory the nearest similar helper uses; ledger line.
2. Two assertion libraries installed (chai and node:assert); new test needs one → **A**
   → match the convention of the touched package's existing tests; ledger line.
3. Missing devDependency blocks the test run (e.g., `@types/node`) → **A** → install it,
   retry; ledger line. (Dev-only: never ships to users, `git checkout` + uninstall undoes it.)
4. Adding a **runtime** dependency that ships in the production bundle → **borderline C**
   → park: it changes what users download; options: add the dep / hand-roll the ~20-line
   helper / different lib — with a recommended default. Implement behind the default meanwhile.
5. Running the repo's configured formatter on files you touched → **A** → run it; too
   trivial for the ledger.
6. Repo-wide reformat (formatter config change touching hundreds of untouched files)
   → **C** → park: it drowns the review diff and exceeds the stated task.
7. Renaming a private helper inside the module you are editing → **A** → rename; ledger
   line only if the name is visible in the module's review surface.
8. Renaming an **exported** symbol consumed outside the package → **C** → park: public
   API beyond the request — unless the rename IS the request, in which case enumerate
   then exhaust (SKILL.md rule 6).
9. Adding a regression test for the bug you just fixed → **A** → not even a decision:
   it is an implied item on the done-checklist (SKILL.md rule 5). Do it.
10. Deleting a flaky test that keeps failing → **C** → park: it removes a safety net.
    Options: quarantine/skip with issue link (usually the default) / fix it / delete.
    Note: calling it "flaky" first requires re-run evidence per constants.md C1.
11. `git push --force` to a shared branch to clean up history → **B** → always ask;
    never do it parked-or-not without an answer.
12. Deleting rows from a shared staging database to reset test state → **B** → always ask.
13. Table-driven test vs one-case-per-test for the new suite → **A** → match neighboring
    tests; continue, no ledger (structural trivia).
14. Public name of a new CLI flag (`--dry-run` vs `--preview`) → **A if** sibling flags
    establish a convention (follow it; ledger line); **C if** genuinely novel and
    user-visible: implement behind your recommended name, park the naming question.
15. "Update all call sites" and the grep returns 300+ hits, many in generated code
    → **C scoping moment** → report the true count first, process the unambiguous
    non-generated sites in checkpointed batches (SKILL.md rule 6), park the scoping
    question about generated code with a default.
16. Command failed once with ENOENT because of wrong cwd → **not a question at all** →
    error-retry protocol (SKILL.md rule 7): fix the path, retry; escalation only per
    constants.md C5.
17. Dev server port already occupied → **A / environmental** → pick another port, note
    it in the summary; asking would be a first-error surrender.
