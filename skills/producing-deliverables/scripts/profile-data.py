#!/usr/bin/env python3
#
# profile-data.py — one-shot data profile before any computation
# (producing-deliverables rule 2).
#
# Usage: profile-data.py <file> [--key COL[,COL]] [--sheet NAME]
#
#   <file>    csv / tsv / xlsx / xlsm / json (records or json-lines)
#   --key     column(s) expected to uniquely identify a row; reports duplicate keys
#   --sheet   xlsx only: profile this sheet (default: every sheet)
#
# Prints, as a quotable table per sheet: row count, duplicate full rows, and per
# column — dtype, null count, distinct count, min/max (lexicographic for strings, so a
# date column stored as text exposes its own sort trap: "Apr..." < "Aug..." < "Dec...").
# Then a FINDINGS list of parse-based facts only (no judgment thresholds — those are
# the model's call, per constants.md): object columns that fully parse as dates or as
# numbers, mixed-type object columns, fully-null columns, duplicate keys/rows.
#
# The script replaces only the mechanical profiling pass. Deciding what a finding MEANS
# (drop? coerce? ask?) is rule 3's logged decision, never this script's.
#
# Exit status: 0 profiled, 2 usage error, 3 read/parse failure.

import sys
import warnings

try:
    import pandas  # noqa: F401 -- fail fast with a friendly message
except ImportError:
    sys.exit("profile-data.py requires pandas: python3 -m pip install pandas")


def die(msg, code):
    print("profile-data.py: %s" % msg, file=sys.stderr)
    sys.exit(code)


def parse_args(argv):
    path, keys, sheet = None, [], None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--key":
            i += 1
            if i >= len(argv):
                die("--key needs a value", 2)
            keys = [k.strip() for k in argv[i].split(",") if k.strip()]
        elif a == "--sheet":
            i += 1
            if i >= len(argv):
                die("--sheet needs a value", 2)
            sheet = argv[i]
        elif a.startswith("--"):
            die("unknown option: %s" % a, 2)
        elif path is None:
            path = a
        else:
            die("unexpected argument: %s" % a, 2)
        i += 1
    if path is None:
        die("usage: profile-data.py <file> [--key COL[,COL]] [--sheet NAME]", 2)
    return path, keys, sheet


def load_frames(path, sheet):
    """Return list of (label, DataFrame)."""
    low = path.lower()
    try:
        if low.endswith((".xlsx", ".xlsm", ".xls")):
            import pandas as pd
            sheets = pd.read_excel(path, sheet_name=sheet)  # None -> dict of all
            if isinstance(sheets, dict):
                return [("sheet: %s" % name, df) for name, df in sheets.items()]
            return [("sheet: %s" % sheet, sheets)]
        if low.endswith(".json") or low.endswith(".jsonl") or low.endswith(".ndjson"):
            import pandas as pd
            try:
                return [("json", pd.read_json(path))]
            except ValueError:
                return [("json-lines", pd.read_json(path, lines=True))]
        # csv / tsv / anything else: delimiter-sniffed text table
        import pandas as pd
        sep = "\t" if low.endswith((".tsv", ".tab")) else None
        return [("csv", pd.read_csv(path, sep=sep, engine="python"))]
    except ImportError as e:
        die("missing dependency: %s (pip install pandas openpyxl)" % e, 3)
    except FileNotFoundError:
        die("no such file: %s" % path, 3)
    except Exception as e:
        die("failed to read %s: %s: %s" % (path, type(e).__name__, e), 3)


def fmt_val(v, is_str):
    s = str(v)
    if len(s) > 26:
        s = s[:23] + "..."
    return '"%s"' % s if is_str else s


def profile(label, df, keys, path):
    import pandas as pd

    n = len(df)
    print("== profile: %s (%s) ==" % (path, label))
    dup_rows = int(df.duplicated().sum()) if n else 0
    print("rows: %d   columns: %d   duplicate full rows: %d" % (n, df.shape[1], dup_rows))
    print()

    headers = ["column", "dtype", "nulls", "distinct", "min", "max"]
    table, findings = [], []

    for col in df.columns:
        s = df[col]
        nulls = int(s.isna().sum())
        nn = s.dropna()
        distinct = int(nn.nunique())
        is_str = s.dtype == object
        if len(nn) == 0:
            mn = mx = "-"
            findings.append("%s: 100%% null (%d/%d) — dead column" % (col, nulls, n))
        else:
            try:
                mn, mx = fmt_val(nn.min(), is_str), fmt_val(nn.max(), is_str)
            except TypeError:  # unorderable mixed types
                mn = mx = "(mixed types)"
        table.append([str(col), str(s.dtype), str(nulls), str(distinct), str(mn), str(mx)])

        if is_str and len(nn) > 0:
            types = set(type(v).__name__ for v in nn)
            if len(types) > 1:
                findings.append("%s: mixed value types in one column: %s"
                                % (col, ", ".join(sorted(types))))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                as_dt = pd.to_datetime(nn.astype(str), errors="coerce")
                as_num = pd.to_numeric(nn.astype(str).str.replace(",", "", regex=False),
                                       errors="coerce")
            if as_dt.notna().all():
                findings.append(
                    "%s: all %d non-null values parse as dates but dtype is object — "
                    "dates stored as STRINGS (sorts lexicographically: min/max above "
                    "are alphabetical, not chronological)" % (col, len(nn)))
            elif as_num.notna().all():
                findings.append(
                    "%s: all %d non-null values parse as numbers but dtype is object — "
                    "numbers stored as strings (aggregation will concatenate or fail)"
                    % (col, len(nn)))

    widths = [max(len(r[i]) for r in [headers] + table) for i in range(len(headers))]
    for row in [headers] + table:
        print("  ".join(v.ljust(w) for v, w in zip(row, widths)).rstrip())
    print()

    if keys:
        missing = [k for k in keys if k not in df.columns]
        if missing:
            findings.append("key check SKIPPED — column(s) not found here: %s "
                            "(have: %s)" % (", ".join(missing),
                                            ", ".join(map(str, df.columns))))
        else:
            distinct_keys = len(df.drop_duplicates(subset=keys))
            dup_keys = n - distinct_keys
            print("key check (%s): %d rows, %d distinct keys -> %d duplicate-key rows"
                  % (",".join(keys), n, distinct_keys, dup_keys))
            if dup_keys > 0:
                findings.append("key (%s): %d duplicate-key rows — dedupe is a rule 3 "
                                "logged decision, not a default"
                                % (",".join(keys), dup_keys))
            print()

    if dup_rows > 0:
        findings.append("%d fully duplicated rows" % dup_rows)

    if findings:
        print("FINDINGS (resolve or route through rule 3 — never chart through them):")
        for f in findings:
            print("- %s" % f)
    else:
        print("FINDINGS: none flagged (parse-based checks only; plausibility of the "
              "min/max values above is still your judgment)")
    print()


def main():
    path, keys, sheet = parse_args(sys.argv[1:])
    for label, df in load_frames(path, sheet):
        profile(label, df, keys, path)


if __name__ == "__main__":
    main()
