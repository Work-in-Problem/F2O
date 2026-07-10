#!/bin/sh
# diff-audit.sh — read-only helper for the DIFF AUDIT (scoping-code-changes rule 10).
#
# Prints three advisory views of the current diff, then ALWAYS exits 0:
#
#   1. git diff --stat     per-FILE audit surface: "did the task require this file?"
#   2. hunks per file      per-HUNK audit surface: "which words of the request
#                          necessitate this hunk?" — revert hunks with no answer
#   3. noise scan          ADDED lines matching self-introduced-noise patterns
#
# Usage:
#   scripts/diff-audit.sh                # worktree + index vs HEAD  (git diff HEAD)
#   scripts/diff-audit.sh --cached       # staged changes only
#   scripts/diff-audit.sh main...HEAD    # any git-diff args pass through unchanged
#
# The scan is ADVISORY: every hit is a judgment call, not a verdict — e.g. print(
# in a CLI entry point is product output, in a library module it is debug residue.
# The audit (rule 10) decides; this script only surfaces candidates. Exit status is
# always 0 so the script can never gate or fail a pipeline.
#
# Patterns scanned, in ADDED (+) lines only — lines this diff introduced:
#
#   debug-print         console.log/debug/dir/trace, print(, pprint(, dbg!,
#                       println!/eprintln!, fmt.Print*, System.out.print*, var_dump,
#                       binding.pry, byebug, debugger, breakpoint(, set_trace —
#                       probes typically left over from an investigation.
#   todo-added          TODO/FIXME/XXX/HACK introduced by THIS diff. Either do it
#                       now (if inside the scope contract) or convert it to a
#                       "Noticed: ... — left untouched." summary line (rule 3);
#                       never ship new debt markers silently. Note: a moved TODO
#                       shows up as added — check whether it is genuinely new.
#   change-narration    comments describing the CHANGE instead of the code: "NEW:",
#                       "now uses", "changed to", "updated to", "instead of",
#                       "previously", "refactored", "renamed from". Comments are
#                       timeless (rule 6); narration belongs in the commit message.
#                       "instead of" can open a legitimate why-comment — judge the
#                       hit, do not auto-delete.
#   commented-out-code  comment lines whose content looks like code: ending in
#                       ; { } or starting with a keyword, a call, or an assignment.
#                       Delete dead code; git history keeps it. Expect false
#                       positives in Markdown/doc prose — advisory.
#   unused-import?      an added import whose bound symbol appears in no other
#                       added line of the same file. CANDIDATE only: the symbol may
#                       be used by unchanged lines (a legitimate import added for
#                       existing code) — verify against the full file before
#                       deleting. Parses single-line Python / JS / TS imports and
#                       require(); multi-line import blocks are not parsed.
#
# Extending per-language: each pattern is one commented regex in the awk program
# below — add alternatives (e.g. Rust todo!(), Go log.Printf) to the alternation.

main() {
  if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "diff-audit: not inside a git repository — nothing to audit."
    return 0
  fi

  if [ "$#" -eq 0 ]; then
    if git rev-parse --verify HEAD >/dev/null 2>&1; then
      set -- HEAD        # default: everything since last commit (staged + unstaged)
    else
      set -- --cached    # unborn branch: audit whatever is staged
    fi
  fi

  TMP=$(mktemp "${TMPDIR:-/tmp}/diff-audit.XXXXXX") || {
    echo "diff-audit: mktemp failed — no audit performed."
    return 0
  }
  trap 'rm -f "$TMP"' EXIT INT TERM

  git diff --no-color "$@" >"$TMP" 2>/dev/null

  if [ ! -s "$TMP" ]; then
    echo "diff-audit: empty diff for 'git diff $*' — nothing to audit."
    return 0
  fi

  echo "== 1/3 git diff --stat — per FILE: did the task require this file? =="
  git diff --no-color --stat "$@" 2>/dev/null
  echo
  echo "== 2/3 hunks per file — per HUNK: which words of the request necessitate it? =="
  awk '
    /^diff --git / {
      if (file != "") printf "  %4d  %s\n", nh, file
      file = $0
      sub(/^diff --git a\//, "", file)
      sub(/ b\/.*/, "", file)
      nh = 0
    }
    /^@@/ { nh++ }
    END { if (file != "") printf "  %4d  %s\n", nh, file }
  ' "$TMP"
  echo
  echo "== 3/3 noise scan over ADDED lines — advisory, judge every hit =="
  awk '
    function trim(s)    { sub(/^[[:space:]]+/, "", s); sub(/[[:space:]]+$/, "", s); return s }
    function last_as(s) { if (s ~ / as /) sub(/^.* as /, "", s); return trim(s) }
    function flag(kind) { printf "  [%s] %s: %s\n", kind, file, trim(line); hits++ }
    function add_sym(s) {
      s = trim(s)
      if (s != "" && s != "*") { nsym++; symfile[nsym] = file; sym[nsym] = s; symsrc[nsym] = trim(line) }
    }

    /^diff --git / { file = $0; sub(/^diff --git a\//, "", file); sub(/ b\/.*/, "", file); next }
    /^\+\+\+/      { next }
    !/^\+/         { next }

    {
      line = substr($0, 2)
      low  = tolower(line)

      # debug prints — see header; alternation is deliberately broad, judge hits
      if (low ~ /console\.(log|debug|dir|trace)|(^|[^a-z_])print\(|pprint\(|dbg!|println!|eprintln!|fmt\.print|system\.out\.print|var_dump|binding\.pry|byebug|(^|[^a-z_])debugger|breakpoint\(|set_trace/)
        flag("debug-print")

      # TODO/FIXME/XXX/HACK introduced by this diff — see header
      if (line ~ /TODO|FIXME|XXX|HACK/)
        flag("todo-added")

      # change-narration comments — comment marker + change-history phrasing
      if (line ~ /\/\/|#|\/\*|^[[:space:]]*\*/ && low ~ /new:|now (uses|calls|returns|handles|supports)|changed to|updated to|was previously|previously (used|was|did)|refactored|renamed from|instead of|used to (be|use)/)
        flag("change-narration")

      # commented-out code — comment ending in code punctuation, or comment whose
      # first token is a keyword / call / assignment
      if (line ~ /^[[:space:]]*(\/\/|#)/ && (line ~ /[;{}][[:space:]]*$/ || line ~ /^[[:space:]]*(\/\/|#)+[[:space:]]*(if |for |while |return |def |function |class |const |let |var |import |from |[A-Za-z_][A-Za-z0-9_.]*\(|[A-Za-z_][A-Za-z0-9_.]*[[:space:]]*=[^=])/))
        flag("commented-out-code")

      # ---- import bookkeeping for unused-import candidates ----
      if (line ~ /^[[:space:]]*from[[:space:]]+[^[:space:]]+[[:space:]]+import[[:space:]]/) {
        # python: from m import a, b as c
        rest = line
        sub(/^[[:space:]]*from[[:space:]]+[^[:space:]]+[[:space:]]+import[[:space:]]+/, "", rest)
        sub(/#.*/, "", rest); gsub(/[()]/, "", rest)
        n = split(rest, parts, ","); for (i = 1; i <= n; i++) add_sym(last_as(parts[i]))
      } else if (line ~ /^[[:space:]]*import[[:space:]]+[{]/) {
        # js/ts: import { A, B as C } from "m"
        rest = line
        sub(/^[^{]*[{]/, "", rest); sub(/[}].*/, "", rest)
        n = split(rest, parts, ","); for (i = 1; i <= n; i++) add_sym(last_as(parts[i]))
      } else if (line ~ /^[[:space:]]*import[[:space:]]+[A-Za-z_$]/) {
        rest = line
        sub(/^[[:space:]]*import[[:space:]]+/, "", rest)
        if (rest ~ /[[:space:]]from[[:space:]]/) {
          # js/ts default import: import X from "m"
          sub(/[[:space:]]+from[[:space:]].*/, "", rest)
          gsub(/[{}]/, "", rest)
          n = split(rest, parts, ","); for (i = 1; i <= n; i++) add_sym(last_as(parts[i]))
        } else {
          # python: import a.b as c / import a.b  (usage searched as first segment)
          sub(/#.*/, "", rest); sub(/;.*/, "", rest)
          if (rest ~ / as /) add_sym(last_as(rest))
          else { sub(/[.[:space:]].*/, "", rest); add_sym(rest) }
        }
      } else if (line ~ /^[[:space:]]*(const|let|var)[[:space:]].*=[[:space:]]*require[[:space:]]*\(/) {
        # js: const X = require("m") / const { A, B } = require("m")
        rest = line
        sub(/^[[:space:]]*(const|let|var)[[:space:]]+/, "", rest)
        sub(/=.*/, "", rest); gsub(/[{}]/, "", rest)
        n = split(rest, parts, ","); for (i = 1; i <= n; i++) add_sym(parts[i])
      } else {
        body[file] = body[file] "\n" line
      }
    }

    END {
      for (i = 1; i <= nsym; i++)
        if (index(body[symfile[i]], sym[i]) == 0) {
          printf "  [unused-import?] %s: %s   (symbol %s appears in no other added line — verify the full file)\n", symfile[i], symsrc[i], sym[i]
          hits++
        }
      if (hits == 0) print "  clean — no noise patterns matched in added lines"
    }
  ' "$TMP"
  echo
  echo "Advisory only. Revert hunks with no answer; strip noise that fails the audit;"
  echo "keep a hit only with a one-line justification. (scoping-code-changes rule 10)"
}

main "$@"
exit 0
