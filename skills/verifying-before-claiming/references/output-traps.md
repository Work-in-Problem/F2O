# Output traps: runs that look green but prove nothing

CLAUDE.md §1 sets the standard (output must affirmatively show success; exit 0 proves
nothing). This catalog lists the concrete ways a run fakes green. Scan every passing run
against it before quoting the output in a VERIFIED entry — especially when the green came
suspiciously easily.

## 1. Zero tests collected / ran

```
----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK
```

`python -m unittest discover` with a wrong pattern prints `OK` and exits 0 having run
nothing. Same family:

```
ok      example.com/pkg    0.002s [no test files]
```

`go test` exits 0 when a package has no test files. Jest/vitest with
`--passWithNoTests` print `No tests found, exiting with code 0`. Pytest exits 5 on
`collected 0 items`, but Makefile targets ending in `|| true` and permissive CI wrappers
swallow that.

Repair: a run that executed nothing proves nothing. Fix collection (file naming, path,
glob, venv, missing `__init__.py`) and re-run until the collected count matches
expectation.

## 2. Everything skipped

```
======================== 12 skipped in 0.34s =========================
```

Exit 0, zero assertions executed. Usually an env-gated marker (`@skipUnless(DATABASE_URL)`)
skipping the whole module. Compare the skip count against expectation; an unexpected skip
is a failure to investigate, not a pass.

## 3. Glob matched zero files

```
$ shellcheck scripts/*.zsh
$ echo $?
0
```

No matching files → some tools succeed silently doing nothing. Same trap in Make:
`$(wildcard test/unit/*.py)` expanding empty makes the target "pass" instantly.
Symptom: instant success with no per-file output. Repair: list the files the pattern
matches before trusting the run.

## 4. Exit-0 curl / pipeline-masked grep

```
$ curl -s http://localhost:3000/api/health; echo "exit=$?"
{"error":"Internal Server Error"}
exit=0
```

curl exits 0 for HTTP 500 — it only fails on transport errors. Use `curl -sf` or read
`-w '%{http_code}'`. Related:

```
$ grep -r "TODO" src/ | wc -l
0
```

Exit status comes from `wc`, not `grep`; an empty result reads as success. Read the count
or check `grep`'s own exit status — and remember an empty grep/curl body affirms nothing.

## 5. Stale hot-reload / stale process

You edited the handler at 14:02, but the dev server log shows no rebuild line after
13:55 — the response you just verified came from the old code. Watch for the absence of
`hmr update`, `Compiled successfully`, or a restart banner newer than your edit. Repair:
fresh-state rule (SKILL.md rule 5) — restart, confirm a startup line that postdates the
edit, then verify.

## 6. Wrong env / config banner

```
warning: DATABASE_URL not set — falling back to sqlite://:memory:
Using settings: config/production.yaml
```

Green against the wrong backend or wrong config proves nothing about the real one. Read
the banner/header lines of every run, not just the tail summary — the lie is usually in
the first five lines.

## 7. Implausibly fast green run

```
ok      example.com/pkg    (cached)
>>> FULL TURBO — replaying logs from cache
```

A "2-minute" suite finishing in a second means cache replay or the wrong target, not a
verification of your edit. Go: rerun with `-count=1`; turbo/nx: `--force`; jest:
`--clearCache` if timestamps look wrong. A green run's duration should be plausible for
the work it claims to have done — if it is not, treat it as unverified.

## Rule of thumb

Before quoting any passing output: state which trap classes you checked it against. If a
green run surprised you, that surprise is a trigger — either find the mechanism that made
it pass or treat it as trap candidate #1.
