# Diff examples — one bad/good pair per gate

Paired diffs for `scoping-code-changes`. Read the pair for the gate that just fired.
Every BAD diff satisfies the literal request; what makes it bad is countable in the
diff itself. Examples are Python/JS for compactness — the gates are language-agnostic.

1. [Guards: defensive bloat vs trust-boundary guard](#1-guards) — rule 4
2. [Abstraction: premature base class vs concrete duplication](#2-abstraction) — rule 5
3. [Comments: noise and narration vs a single why-comment](#3-comments) — rule 6
4. [Rewrite vs targeted edit](#4-rewrite-vs-edit) — rule 7
5. [Adjacent issue: silent fix vs `Noticed:` line](#5-adjacent-issue) — rule 3
6. [Under-delivery vs the always-in-scope floor](#6-floor) — rule 1

## 1. Guards

Task: "Add `compute_prorated_amount(days: int, rate: Decimal)`, called from
`billing.close()`." One internal caller, non-nullable typed params, no failure mode
named in the request.

**BAD — guards on states the types and caller contract already exclude (rule 4):**

```diff
+def compute_prorated_amount(days: int, rate: Decimal) -> Decimal:
+    if days is None or rate is None:
+        return Decimal("0")
+    if not isinstance(days, int):
+        raise TypeError("days must be an int")
+    try:
+        return (Decimal(days) / Decimal(30)) * rate
+    except ArithmeticError:
+        logger.warning("proration failed; defaulting to 0")
+        return Decimal("0")
```

Nothing crosses a trust boundary; the fallback turns a loud bug into a silently wrong
invoice.

**GOOD — the internal function stays bare:**

```diff
+def compute_prorated_amount(days: int, rate: Decimal) -> Decimal:
+    return (Decimal(days) / Decimal(30)) * rate
```

For contrast, a guard that PASSES rule 4 — from a different task whose request named
the failure mode ("reject non-numeric BILLING_DAYS"); the env var is a trust boundary:

```diff
 def load_billing_config() -> BillingConfig:
-    days = int(os.environ["BILLING_DAYS"])
+    raw = os.environ["BILLING_DAYS"]
+    if not raw.isdigit():
+        raise ConfigError(f"BILLING_DAYS must be an integer, got {raw!r}")
+    days = int(raw)
```

Validate once, where the untrusted data enters — never again downstream.

## 2. Abstraction

Task: "Add a CSV exporter with the same behavior as the JSON exporter." That makes two
exporters total — below the rule 5 usage bar.

**BAD — abstraction at the second occurrence (rule 5):**

```diff
+class ExporterBase(ABC):
+    @abstractmethod
+    def serialize(self, rows: list[dict]) -> str: ...
+    def export(self, rows: list[dict], path: Path) -> None:
+        path.write_text(self.serialize(rows))
+
+class JsonExporter(ExporterBase):
+    def serialize(self, rows):
+        return json.dumps(rows, indent=2)
+
+class CsvExporter(ExporterBase):
+    def serialize(self, rows):
+        return _csv_dump(rows)
+
+EXPORTERS = {"json": JsonExporter, "csv": CsvExporter}
```

Two usages bought an abstract class, a registry, and an indirection layer the request
never mentioned — and rewrote the working JSON exporter (also a rule 7 violation).

**GOOD — concrete duplication, existing exporter untouched:**

```diff
+def export_csv(rows: list[dict], path: Path) -> None:
+    with path.open("w", newline="") as f:
+        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
+        writer.writeheader()
+        writer.writerows(rows)
```

Mirrors `export_json`'s signature and shape; no apologizing comment about the
duplication. A third exporter request is the moment extraction becomes legal.

## 3. Comments

Task: "Retry with exponential backoff instead of the fixed 1s sleep."

**BAD — change narration and a what-comment (rule 6):**

```diff
+# Changed to use exponential backoff instead of a fixed delay
 for attempt in range(MAX_RETRIES):
-    time.sleep(1)
+    # sleep for 2^attempt seconds
+    time.sleep(2 ** attempt)  # NEW: exponential
```

One changelog comment, one restatement of the code, one `NEW:` marker — all three are
deleted in the diff audit (the audit script flags them).

**GOOD — one why-comment carrying a non-obvious constraint, timeless tense:**

```diff
 for attempt in range(MAX_RETRIES):
-    time.sleep(1)
+    # payment API rate-limits bursts closer than 4s apart (VEND-231)
+    time.sleep(2 ** attempt)
```

If siblings carry no comments and the constraint were obvious, even this line would
go; a genuinely non-obvious invariant like this one earns rule 6's stated exception.

## 4. Rewrite vs edit

Task: "Fix the bug where `get_items` returns N-1 items."

**BAD — full-body replacement for a one-character bug (rule 7):**

```diff
-def get_items(page, size):
-    start = page * size
-    end = start + size - 1
-    items = load_items()
-    if items is None:
-        return []
-    return items[start:end]
+def get_items(page: int, size: int) -> list[Item]:
+    """Return one page of items."""
+    items = load_items() or []
+    offset = page * size
+    return items[offset : offset + size]
```

Unrequested riders: type annotations and a docstring siblings lack, `start` renamed to
`offset`, the explicit None-guard restructured. Review surface = the whole function;
git blame gone.

**GOOD — the smallest textual edit:**

```diff
 def get_items(page, size):
     start = page * size
-    end = start + size - 1
+    end = start + size
     items = load_items()
```

One hunk, one changed line, every other line byte-identical.

## 5. Adjacent issue

Task: the same pagination fix; two functions down, `format_date()` visibly renders
months 0-indexed — an unrelated, real bug.

**BAD — silent adjacent fix smuggled into the diff (rule 3):**

```diff
 def get_items(page, size):
-    end = start + size - 1
+    end = start + size

 def format_date(ts):
-    return f"{ts.month - 1}/{ts.day}"
+    return f"{ts.month}/{ts.day}"
```

The second hunk maps to no words of the request: an unreviewed, untested behavior
change riding inside a pagination fix. Equally wrong: seeing the bug and saying nothing.

**GOOD — pure diff plus the owned line format in the final summary:**

```diff
 def get_items(page, size):
-    end = start + size - 1
+    end = start + size
```

> Noticed: format_date() in src/dates.py renders months 0-indexed — left untouched.

Only if the adjacent bug blocked the requested change would fixing its minimum be
allowed — declared explicitly in the summary (rule 3's sole exception).

## 6. Floor

Task: "Change the default page size from 20 to 50." One existing test asserts 20; one
doc line states it.

**BAD — over-literal minimalism, floor items offered instead of done (rule 1):**

```diff
-DEFAULT_PAGE_SIZE = 20
+DEFAULT_PAGE_SIZE = 50
```

> Done — note test_pagination.py still asserts 20. Want me to update it and the docs?

The asserting test and the doc line are ALWAYS-IN-SCOPE floor items: same turn, no
permission question. The closing offer also violates finishing-the-turn rule 4.

**GOOD — exactly three sites, same turn, nothing else:**

```diff
 config.py
-DEFAULT_PAGE_SIZE = 20
+DEFAULT_PAGE_SIZE = 50
```

```diff
 tests/test_pagination.py
-    assert resp.page_size == 20
+    assert resp.page_size == 50
```

```diff
 docs/api.md
-Defaults to 20 items per page.
+Defaults to 50 items per page.
```

The floor closes the request; the contract's edge stops anything more.
