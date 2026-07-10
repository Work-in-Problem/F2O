#!/bin/bash
# Fable2Opus Layer 2 — claim_gate.py test harness.
#
# Pipes each fixture (hook-input JSON + synthetic transcript .jsonl) through
# claim_gate.py and asserts the verdict:
#   BLOCK -> stdout is {"decision":"block","reason":...}, reason <= 700 chars,
#            optional needle substring present, exit code 0
#   ALLOW -> stdout empty, exit code 0
# In every case: exit code must be 0 and stderr must be empty (the hook must
# never brick a session).
#
# Usage: bash .claude/hooks/tests/run_hook_tests.sh

set -u

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$TESTS_DIR/../claim_gate.py"
FIX="$TESTS_DIR/fixtures"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/claim-gate-tests.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0
FAILED_CASES=""

# run_case <name> <input-fixture> <transcript-fixture|MISSING> <ALLOW|BLOCK> <needle> <env-off 0|1>
run_case() {
  local name="$1" input="$2" transcript="$3" expect="$4" needle="$5" env_off="$6"

  local tpath
  if [ "$transcript" = "MISSING" ]; then
    tpath="$TMP/does-not-exist.jsonl"
  else
    tpath="$FIX/$transcript"
    if [ ! -f "$tpath" ]; then
      echo "FAIL  $name (missing fixture $transcript)"
      FAIL=$((FAIL + 1)); FAILED_CASES="$FAILED_CASES $name"; return
    fi
  fi

  local input_json="$TMP/$name.input.json"
  sed "s|__TRANSCRIPT__|$tpath|g" "$FIX/$input" > "$input_json"

  local out="$TMP/$name.stdout" err="$TMP/$name.stderr" rc
  if [ "$env_off" = "1" ]; then
    env FABLE2OPUS_HOOKS_OFF=1 python3 "$HOOK" < "$input_json" > "$out" 2> "$err"
  else
    env -u FABLE2OPUS_HOOKS_OFF python3 "$HOOK" < "$input_json" > "$out" 2> "$err"
  fi
  rc=$?

  if [ "$rc" -ne 0 ]; then
    echo "FAIL  $name (exit code $rc, must always be 0)"
    FAIL=$((FAIL + 1)); FAILED_CASES="$FAILED_CASES $name"; return
  fi
  if [ -s "$err" ]; then
    echo "FAIL  $name (hook wrote to stderr: $(head -c 200 "$err"))"
    FAIL=$((FAIL + 1)); FAILED_CASES="$FAILED_CASES $name"; return
  fi

  if python3 - "$out" "$expect" "$needle" <<'PY'
import json, sys
path, expect, needle = sys.argv[1], sys.argv[2], sys.argv[3]
raw = open(path, encoding="utf-8").read()
if expect == "ALLOW":
    assert raw.strip() == "", "expected ALLOW (empty stdout), got: %r" % raw[:200]
else:
    d = json.loads(raw)
    assert d.get("decision") == "block", "expected decision=block, got: %r" % raw[:200]
    reason = d.get("reason") or ""
    assert reason, "block verdict with empty reason"
    assert len(reason) <= 700, "reason exceeds 700-char cap: %d" % len(reason)
    if needle:
        assert needle in reason, "needle %r not in reason: %r" % (needle, reason[:300])
PY
  then
    echo "pass  $name ($expect)"
    PASS=$((PASS + 1))
  else
    echo "FAIL  $name (verdict assertion failed; stdout: $(head -c 200 "$out"))"
    FAIL=$((FAIL + 1)); FAILED_CASES="$FAILED_CASES $name"
  fi
}

#         name                      input fixture                       transcript fixture                        expect  needle                              env-off
run_case  clean_close               clean_close.input.json              clean_close.transcript.jsonl              ALLOW   ""                                  0
run_case  promise_end               promise_end.input.json              promise_end.transcript.jsonl              BLOCK   "I'll now run the tests"            0
run_case  claim_edit_after_verify   claim_edit_after_verify.input.json  claim_edit_after_verify.transcript.jsonl  BLOCK   "CLAUDE.md §1"                      0
run_case  claim_verify_after_edit   claim_verify_after_edit.input.json  claim_verify_after_edit.transcript.jsonl  ALLOW   ""                                  0
run_case  curl_verify_after_edit    curl_verify_after_edit.input.json   curl_verify_after_edit.transcript.jsonl   ALLOW   ""                                  0
run_case  md_edit_after_verify      md_edit_after_verify.input.json     md_edit_after_verify.transcript.jsonl     ALLOW   ""                                  0
run_case  md_plus_code_edit         md_plus_code_edit.input.json        md_plus_code_edit.transcript.jsonl        BLOCK   "CLAUDE.md §1"                      0
run_case  tmp_html_edit             tmp_html_edit.input.json            tmp_html_edit.transcript.jsonl            ALLOW   ""                                  0
run_case  repo_html_edit            repo_html_edit.input.json           repo_html_edit.transcript.jsonl           BLOCK   "CLAUDE.md §1"                      0
run_case  gitignore_license_edit    gitignore_edit.input.json           gitignore_edit.transcript.jsonl           ALLOW   ""                                  0
run_case  negation_not_done_yet     negation.input.json                 negation.transcript.jsonl                 ALLOW   ""                                  0
run_case  stop_hook_active_true     stop_hook_active_true.input.json    claim_edit_after_verify.transcript.jsonl  ALLOW   ""                                  0
run_case  garbage_transcript        garbage_claim.input.json            garbage.transcript.jsonl                  ALLOW   ""                                  0
run_case  missing_transcript        garbage_claim.input.json            MISSING                                   ALLOW   ""                                  0
run_case  hooks_off_env             claim_edit_after_verify.input.json  claim_edit_after_verify.transcript.jsonl  ALLOW   ""                                  1
run_case  promise_transcript_only   promise_transcript_only.input.json  promise_transcript_only.transcript.jsonl  BLOCK   "Next, let me wire the CLI flag"    0
run_case  notes_edit_only           notes_edit_only.input.json          notes_edit_only.transcript.jsonl          ALLOW   ""                                  0
run_case  quoted_claim              quoted_claim.input.json             quoted_claim.transcript.jsonl             ALLOW   ""                                  0
run_case  no_verify_bash            no_verify_bash.input.json           no_verify_bash.transcript.jsonl           ALLOW   ""                                  0
run_case  sidechain_ignored         sidechain.input.json                sidechain.transcript.jsonl                ALLOW   ""                                  0
run_case  promise_not_tail          promise_not_tail.input.json         claim_verify_after_edit.transcript.jsonl  ALLOW   ""                                  0
run_case  promise_let_me_know       promise_let_me_know.input.json      clean_close.transcript.jsonl              ALLOW   ""                                  0
run_case  promise_then_evidence     promise_followed_by_evidence.input.json  clean_close.transcript.jsonl         ALLOW   ""                                  0
run_case  promise_handoff_your_call promise_handoff_your_call.input.json  clean_close.transcript.jsonl            ALLOW   ""                                  0
run_case  fallback_tool_after_text  fallback_tool_after_text.input.json  fallback_tool_after_text.transcript.jsonl  ALLOW   ""                                0

echo

# ---------- soft-off state file cases (HOME overridden; real home untouched) ----------
FAKEHOME="$(mktemp -d)"; mkdir -p "$FAKEHOME/.claude"; touch "$FAKEHOME/.claude/f2o.disabled"
out=$(HOME="$FAKEHOME" python3 "$TESTS_DIR/../claim_gate.py" <<EOF_SF
$(cat "$FIX/claim_edit_after_verify.input.json" | python3 -c "import json,sys; d=json.load(sys.stdin); d['transcript_path']='$FIX/claim_edit_after_verify.transcript.jsonl'; print(json.dumps(d))")
EOF_SF
); rc=$?
if [ "$rc" -eq 0 ] && [ -z "$out" ]; then echo "pass  statefile_claim_gate_allow"; PASS=$((PASS+1)); else echo "FAIL  statefile_claim_gate_allow (rc=$rc out=$out)"; FAIL=$((FAIL+1)); fi
out=$(cd "$(mktemp -d)" && HOME="$FAKEHOME" CLAUDE_PLUGIN_ROOT="$(cd "$TESTS_DIR/../.." && pwd)" python3 "$TESTS_DIR/../session_context.py" <<< '{}' 2>/dev/null); rc=$?
if [ "$rc" -eq 0 ] && [ -z "$out" ]; then echo "pass  statefile_session_context_empty"; PASS=$((PASS+1)); else echo "FAIL  statefile_session_context_empty"; FAIL=$((FAIL+1)); fi
rm -rf "$FAKEHOME"

# ---------- session_context.py cases ----------
SC="$TESTS_DIR/../session_context.py"
sc_pass=0; sc_fail=0
sc_case() { # sc_case <name> <expect: JSON|EMPTY> <env-off> <plugin-root> <cwd>
  local name="$1" expect="$2" env_off="$3" proot="$4" wd="$5" out rc
  out=$(cd "$wd" && FABLE2OPUS_HOOKS_OFF="$env_off" CLAUDE_PLUGIN_ROOT="$proot"         python3 "$SC" <<< '{"hook_event_name":"SessionStart","cwd":"'"$wd"'"}' 2>/dev/null); rc=$?
  if [ "$rc" -ne 0 ]; then echo "FAIL  sc:$name (exit $rc)"; sc_fail=$((sc_fail+1)); return; fi
  if [ "$expect" = "JSON" ]; then
    if printf '%s' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); ctx=d["hookSpecificOutput"]["additionalContext"]; assert "Claim audit" in ctx; assert "C18" in ctx; assert "Skill router" in ctx; assert "inventorying-capabilities" in ctx; assert "truncated" not in ctx; assert len(ctx)<=2000, len(ctx)' 2>/dev/null; then
      echo "pass  sc:$name (JSON+content)"; sc_pass=$((sc_pass+1))
    else echo "FAIL  sc:$name (bad JSON/content)"; sc_fail=$((sc_fail+1)); fi
  else
    if [ -z "$out" ]; then echo "pass  sc:$name (EMPTY)"; sc_pass=$((sc_pass+1))
    else echo "FAIL  sc:$name (expected empty, got output)"; sc_fail=$((sc_fail+1)); fi
  fi
}
REPO_ROOT="$(cd "$TESTS_DIR/../.." && pwd)"
NEUTRAL="$(mktemp -d)"
sc_case inject_from_plugin_root  JSON  "" "$REPO_ROOT" "$NEUTRAL"
sc_case inject_via_script_fallback JSON "" ""          "$NEUTRAL"
sc_case env_off                  EMPTY "1" "$REPO_ROOT" "$NEUTRAL"
sc_case skip_when_layer0_in_cwd  EMPTY "" "$REPO_ROOT" "$REPO_ROOT"
BOGUS="$(mktemp -d)"; cp "$SC" "$BOGUS/session_context.py"
out=$(cd "$NEUTRAL" && CLAUDE_PLUGIN_ROOT="$BOGUS" python3 "$BOGUS/session_context.py" <<< '{}' 2>/dev/null); rc=$?
if [ "$rc" -eq 0 ] && [ -z "$out" ]; then echo "pass  sc:missing_core_files (EMPTY)"; sc_pass=$((sc_pass+1)); else echo "FAIL  sc:missing_core_files"; sc_fail=$((sc_fail+1)); fi
rm -rf "$NEUTRAL" "$BOGUS"
echo
echo "session_context tests: $sc_pass passed, $sc_fail failed"
PASS=$((PASS + sc_pass)); FAIL=$((FAIL + sc_fail))

echo "claim_gate tests: $PASS passed, $FAIL failed, $((PASS + FAIL)) total"
if [ "$FAIL" -ne 0 ]; then
  echo "failed cases:$FAILED_CASES"
  exit 1
fi
exit 0
