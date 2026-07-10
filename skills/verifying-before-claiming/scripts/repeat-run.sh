#!/bin/sh
# repeat-run.sh — run a command N times; print a pass/fail tally and the first
# failing output.
#
# Usage:
#   repeat-run.sh [N] -- <command> [args...]
#
#   N defaults to 10 — the flake re-run count from constants.md C1. Use 30 when
#   the observed failure rate is under ~20% (also C1); for "fixed" claims on
#   nondeterministic bugs the run count comes from constants.md C2.
#
# Notes:
#   - The command is executed directly (no shell interpretation). For pipes or
#     shell constructs, wrap them: repeat-run.sh 10 -- sh -c 'cmd1 | cmd2'
#   - Exit status: 0 if all runs passed, 1 if any run failed, 2 on usage error.
#   - All N runs always execute (no early stop), so before/after tallies from
#     identical invocations are directly comparable.

set -u

usage() {
    echo "usage: repeat-run.sh [N] -- <command> [args...]" >&2
    exit 2
}

N=10
if [ $# -ge 1 ] && [ "$1" != "--" ]; then
    case "$1" in
        *[!0-9]*|'') usage ;;      # first arg is neither a count nor "--"
        *) N=$1; shift ;;
    esac
fi

[ "${1:-}" = "--" ] || usage
shift
[ $# -ge 1 ] || usage
[ "$N" -ge 1 ] || usage

out=$(mktemp) || exit 2
first_fail=$(mktemp) || exit 2
trap 'rm -f "$out" "$first_fail"' EXIT INT TERM

pass=0
fail=0
first_fail_run=0

i=1
while [ "$i" -le "$N" ]; do
    if "$@" >"$out" 2>&1; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        if [ "$fail" -eq 1 ]; then
            first_fail_run=$i
            cp "$out" "$first_fail"
        fi
    fi
    i=$((i + 1))
done

echo "repeat-run: $pass/$N passed, $fail/$N failed -- command: $*"

if [ "$fail" -gt 0 ]; then
    echo "--- first failing output (run $first_fail_run) ---"
    cat "$first_fail"
    exit 1
fi
exit 0
