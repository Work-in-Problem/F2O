# MIGRATION — `parse_when()` → `parse_iso()`

Every package in this repo still ships its own copy-pasted `parse_when()`, a
lenient timestamp parser that quietly accepts three formats and returns None
for anything it cannot read. That leniency has let mixed-format timestamps —
and silent fallbacks on malformed data — spread through every service.

`parse_when()` is deprecated. Its replacement is a strict parser,
`parse_iso()`. This file is the complete spec — package maintainers need
nothing beyond it.

## 1. New API

```
parse_iso(text) -> datetime.datetime
```

- Accepts exactly ONE format: `YYYY-MM-DDTHH:MM:SS` — the `T` separator,
  zero-padded fields, seconds required, no timezone suffix, no fractional
  seconds (strptime format `"%Y-%m-%dT%H:%M:%S"`).
- No leniency of any kind: no alternate separators, no surrounding
  whitespace, no missing seconds.
- Raises `ValueError` — it never returns None — for ANY non-conforming
  input, including empty strings, None, and non-string values. The message
  is `"not an ISO 8601 timestamp: %r" % (text,)`.

Reference implementation (use as-is for the body of each package's helper
module):

```python
from datetime import datetime

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def parse_iso(text):
    """Parse a strict ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SS)."""
    if not isinstance(text, str):
        raise ValueError("not an ISO 8601 timestamp: %r" % (text,))
    try:
        return datetime.strptime(text, ISO_FORMAT)
    except ValueError:
        raise ValueError("not an ISO 8601 timestamp: %r" % (text,)) from None
```

## 2. Placement: one private copy per package

The share-nothing policy stands: no package imports another package's code,
and there is no shared root-level module. Each package rewrites its own
helper module in place:

| package | helper module (rewrite in place) |
|---|---|
| billing | `billing/timeparse.py` |
| catalog | `catalog/dates.py` |
| shipping | `shipping/timefmt.py` |
| notify | `notify/whenutil.py` |

Remove `parse_when` and `_WHEN_FORMATS` entirely. No alias, no
`parse_when = parse_iso` shim, no deprecation wrapper: after the migration
the name `parse_when` must not appear anywhere in the package, its tests
included.

## 3. Call-site rules

**Rule A — required timestamps.** Sites that treated `parse_when(x) is None`
as an error now call `parse_iso(x)` and surface the same site-level error
type as before. Where that type was plain `ValueError`, letting the
`parse_iso` ValueError propagate is correct; where the site raises its own
error type, wrap:

```python
# before
issued_at = parse_when(fields.get("issued_at"))
if issued_at is None:
    raise InvoiceError("invoice %s: unreadable issued_at" % number)

# after
try:
    issued_at = parse_iso(fields.get("issued_at"))
except ValueError:
    raise InvoiceError("invoice %s: unreadable issued_at" % number)
```

**Rule B — optional timestamps with a fallback.** Sites that used None to
mean "field not provided, apply the fallback" now apply the fallback ONLY
when the raw value is missing or empty (falsy). A value that is present but
malformed is an error (Rule A applies to it). Silently falling back on
malformed data is the bug class this migration removes.

```python
# before
due_at = parse_when(fields.get("due_at"))
if due_at is None:
    due_at = issued_at + timedelta(days=NET_TERMS_DAYS)

# after
raw_due = fields.get("due_at")
if raw_due:
    try:
        due_at = parse_iso(raw_due)
    except ValueError:
        raise InvoiceError("invoice %s: unreadable due_at" % number)
else:
    due_at = issued_at + timedelta(days=NET_TERMS_DAYS)
```

**Rule C — data and tests.** Timestamp literals owned by this repo (test
data, examples) are normalized to canonical ISO form. Tests that assert the
lenient formats parse become tests that `parse_iso` rejects them with
ValueError; tests that pin a silent fallback on malformed data become tests
that the malformed value is an error. Convert tests — do not delete them.

## 4. Examples

| input | old `parse_when` | new `parse_iso` |
|---|---|---|
| `"2024-03-05T14:30:00"` | `datetime(2024, 3, 5, 14, 30)` | `datetime(2024, 3, 5, 14, 30)` |
| `"2024-03-05 14:30:00"` | `datetime(2024, 3, 5, 14, 30)` | ValueError |
| `"05/03/2024 14:30"` | `datetime(2024, 3, 5, 14, 30)` | ValueError |
| `" 2024-03-05T14:30:00 "` | `datetime(2024, 3, 5, 14, 30)` | ValueError |
| `"2024-03-05T14:30"` | None | ValueError |
| `""` or `None` | None | ValueError |

## 5. Definition of done, per package

1. `grep -rn parse_when <pkg>/` → no hits.
2. The package's helper module defines `parse_iso` exactly per §1.
3. Every former `parse_when` call site follows Rules A–C.
4. `./<pkg>/run_tests.sh` green.

Repo done = all four packages done + `make test-all` green.
