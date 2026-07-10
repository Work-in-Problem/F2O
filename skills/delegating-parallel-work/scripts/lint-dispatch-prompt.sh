#!/usr/bin/env bash
# lint-dispatch-prompt.sh — machine-check a sub-agent dispatch prompt before dispatch.
#
# Checks rule 6 items b/c/d/f of delegating-parallel-work:
#   c: no banned deictic phrases (session context must be pasted inline)
#   b: at least one absolute path
#   d: an explicit 'Do not touch' list
#   f: a 'Report:' return contract
# Items a (one-sentence objective) and e (runnable done-condition + expected output)
# cannot be machine-checked — verify them by eye.
#
# Usage: lint-dispatch-prompt.sh <prompt-file>
# Exit codes: 0 clean; 1 violations (listed on stdout); 2 usage error.

set -u

if [ "$#" -ne 1 ]; then
  echo "usage: $(basename "$0") <prompt-file>" >&2
  exit 2
fi

file="$1"
if [ ! -f "$file" ]; then
  echo "error: no such file: $file" >&2
  exit 2
fi

violations=0
fail() {
  violations=$((violations + 1))
  printf 'VIOLATION %d: %s\n' "$violations" "$1"
}

# --- item c: banned deictic phrases (case-insensitive) -----------------------
banned_phrases=(
  "as discussed"
  "from before"
  "the bug we"
  "like earlier"
  "the pattern from"
)
for phrase in "${banned_phrases[@]}"; do
  if grep -qiF -- "$phrase" "$file"; then
    hit="$(grep -inF -- "$phrase" "$file" | head -n 1)"
    fail "banned deictic phrase \"$phrase\" at line ${hit%%:*} (item c — the sub-agent cannot see this conversation; paste the actual content inline)"
  fi
done

# --- item b: at least one absolute path --------------------------------------
# A '/' starting a multi-segment path, not preceded by an alnum char, ':' or '/'
# (screens out URLs like https://host/path).
if ! grep -qE '(^|[^[:alnum:]:/])/[[:alnum:]_.-]+(/[[:alnum:]_.-]+)+' "$file"; then
  fail "no absolute path found (item b — give exact absolute file paths)"
fi

# --- item d: explicit do-not-touch boundary -----------------------------------
if ! grep -qF "Do not touch" "$file"; then
  fail "missing 'Do not touch' list (item d — name the files/dirs the agent must leave alone)"
fi

# --- item f: return contract ---------------------------------------------------
if ! grep -qF "Report:" "$file"; then
  fail "missing 'Report:' return contract (item f — files changed / commands run with exit codes / open issues)"
fi

if [ "$violations" -gt 0 ]; then
  echo "RESULT: $violations violation(s) in $file — do not dispatch this prompt."
  exit 1
fi

echo "RESULT: clean — $file passes machine checks (items b, c, d, f). Verify items a and e by eye."
exit 0
