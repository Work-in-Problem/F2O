# textutil

Small pure-string helpers for the docs pipeline: `slugify`,
`collapse_whitespace`, `word_count`, `capitalize_words`. Python stdlib
only — no dependencies to install.

## Layout

- `textutil.py` — the library (pure functions only).
- `tests/` — unittest suite.

## Running the tests

From the repo root:

```
python3 -m unittest discover -s tests -t . -p 'unit_*.py'
```

Exit code 0 means the suite is green.

## Conventions

- Keep functions pure: no I/O, no module-level state.
- Every public function gets at least one test.
