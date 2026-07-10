#!/usr/bin/env python3
"""
Fable2Opus Layer 2 — Stop-hook enforcement ("claim gate"). Python 3 stdlib only.

Two deterministic checks on every Stop event. Both are conservative by design:
false negatives are acceptable, false positives are not — when in doubt, allow.

  1. PROMISE SCAN — the closing message must not END on an unexecuted
     future-tense work commitment ("I'll now ...", "Next, let me ...").
     Enforced literally: the matched promise must sit in the message's FINAL
     sentence/line; "let me know ..." requests and sentences that hand the
     action to the user ("... is your call") do not count. Prose owner:
     finishing-the-turn rule 3. This hook only enforces; it adds no policy
     of its own.
  2. CLAIM GATE — a completion claim (the CLAUDE.md §1 word list: done, fixed,
     works, passes, verified, complete) is blocked when the transcript shows an
     Edit/Write/NotebookEdit on a product file AFTER the last plausibly-
     verifying Bash run. Prose owner: CLAUDE.md §1 ("an edit voids every
     earlier passing check").

Hook contract (verified against https://code.claude.com/docs/en/hooks and
https://code.claude.com/docs/en/hooks-guide on 2026-07-10):
  stdin : JSON with session_id, transcript_path, cwd, hook_event_name,
          stop_hook_active, and (Stop/SubagentStop) last_assistant_message.
  block : print {"decision": "block", "reason": "..."} to stdout, exit 0.
  allow : print nothing, exit 0.
  loops : stop_hook_active is true while Claude is already continuing because
          a Stop hook blocked; exiting 0 immediately in that state means this
          hook blocks at most once per stop chain. (Claude Code additionally
          hard-caps consecutive Stop-hook blocks at 8.)

Safety valves (all mandatory, in order):
  - env FABLE2OPUS_HOOKS_OFF=1        -> allow (operator kill switch)
  - stop_hook_active is true          -> allow (no double-block loops)
  - unparseable stdin / wrong event   -> allow
  - missing/garbage/huge transcript   -> allow (never brick a session)
  - reason text capped at REASON_CAP characters
This script must never exit non-zero and must never write to stderr.
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------- constants
# Implementation tuning values, not curriculum thresholds: curriculum numbers
# live in constants.md; nothing below is model-facing prose.
REASON_CAP = 700              # max chars fed back to the model on block
TAIL_CHARS = 300              # "tail region" scanned for promises
NEG_WINDOW = 32               # chars before a claim word scanned for negation
SNIPPET_CAP = 140             # quoted claim-line length in the reason
PROMISE_QUOTE_CAP = 160       # quoted promise length in the reason
MAX_TRANSCRIPT_BYTES = 64 * 1024 * 1024
TRANSCRIPT_TAIL_BYTES = 16 * 1024 * 1024

# The exact CLAUDE.md §1 word list — do not extend without updating §1 first.
CLAIM_RE = re.compile(r"\b(done|fixed|works|passes|verified|complete)\b", re.I)

# Words in the window immediately before a claim word that mean it is NOT an
# affirmative completion claim (negation, futurity, conditionality, buckets).
# Every entry here only ADDS false negatives, which is the safe direction.
NEG_RE = re.compile(
    r"(?:n[’']t\b|\bnot\b|\bno\b|\bnever\b|\bnothing\b|\bnone\b|\bcannot\b"
    r"|\bwithout\b|\byet to\b|\bto be\b|\bbe\b|\bremains?\b|\bremaining\b"
    r"|\bstill\b|\buntil\b|\bunless\b|\bonce\b|\bwhen\b|\bif\b|\bwhether\b"
    r"|\bhow\b|\bbefore\b|\bwill\b|\bwould\b|\bshould\b|\bmust\b"
    r"|\bneeds?\b|\bassum\w*\b|\bunverified\b|\bspeculative\b|\bincomplete\b)",
    re.I,
)

# Future-tense work commitments — the finishing-the-turn rule 3 phrase set.
# The "let me" arms exclude "let me know": that is a user-facing request, not
# a work commitment. The lookahead only removes matches — the safe direction.
PROMISE_RE = re.compile(
    r"(?:\bI[’']ll now\b|\bI will now\b|\bNext,?\s+let me\b(?!\s+know\b)"
    r"|\bNext,?\s+I[’']ll\b|\bThe next step is to\b|\bNow I need to\b"
    r"|\bLet me now\b(?!\s+know\b))",
    re.I,
)

# A second-person marker after the promise phrase, inside its sentence, marks
# a hand-off to the user ("The next step is to deploy, which is your call"),
# not a self-commitment. Skipping only removes matches — the safe direction.
SECOND_PERSON_RE = re.compile(r"\byou(?:rs?)?\b", re.I)

# "Plausibly verifying" Bash commands. Deliberately broad: over-matching here
# makes the gate MORE lenient (an edit is more likely to appear pre-verify),
# which is the safe direction.
VERIFY_RE = re.compile(
    r"(?:\bpytest\b|\bunittest\b|\btests?\b|\bmake\s|\bnpm\s|\bpnpm\s|\byarn\s"
    r"|\bgo\s+test\b|\bcargo\s|\bbuild\b|\bcheck\b|\blint\b|\btsc\b"
    r"|run_tests|repeat-run)",
    re.I,
)

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


# ------------------------------------------------------------------ helpers
def strip_noise(text):
    """Remove spans where claim/promise words don't count: fenced code,
    inline code, blockquote lines, short double-quoted spans."""
    # Drop a trailing unterminated code fence (odd fence count) entirely.
    parts = text.split("```")
    if len(parts) % 2 == 0:
        text = "```".join(parts[:-1])
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"~~~.*?~~~", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"(?m)^\s*>.*$", " ", text)
    text = re.sub(r"\"[^\"\n]{0,120}\"", " ", text)
    text = re.sub(r"“[^”\n]{0,120}”", " ", text)
    return text


def find_promise(cleaned):
    """Return the quoted promise iff the message ENDS on it: the last
    PROMISE_RE match must sit in the final sentence/line — nothing but
    whitespace may follow that sentence's end. A promise followed by more
    prose (e.g. its past-tense evidence) is not a turn-ending commitment,
    and a sentence handing the action to the user is not a self-commitment.
    Both guards only remove matches — the safe direction."""
    tail = cleaned.rstrip()[-TAIL_CHARS:]
    match = None
    for m in PROMISE_RE.finditer(tail):
        match = m  # keep the last occurrence in the tail
    if match is None:
        return None
    rest = tail[match.start():]
    end = len(rest)
    nl = rest.find("\n")
    if nl != -1:
        end = min(end, nl)
    sentence = re.search(r"[.!?](?:\s|$)", rest)
    if sentence:
        end = min(end, sentence.end())
    if rest[end:].strip():
        return None  # promise sentence is not the message's final sentence
    if SECOND_PERSON_RE.search(rest[match.end() - match.start():end]):
        return None  # hand-off to the user, not a work commitment
    return rest[:end].strip()[:PROMISE_QUOTE_CAP]


def find_claim(cleaned):
    """Return (word, line-snippet) for the first unnegated completion claim."""
    for m in CLAIM_RE.finditer(cleaned):
        line_start = cleaned.rfind("\n", 0, m.start()) + 1
        window = cleaned[max(line_start, m.start() - NEG_WINDOW):m.start()]
        if NEG_RE.search(window):
            continue
        line_end = cleaned.find("\n", m.end())
        if line_end == -1:
            line_end = len(cleaned)
        snippet = " ".join(cleaned[line_start:line_end].split())[:SNIPPET_CAP]
        return m.group(0), snippet
    return None


def load_transcript_entries(path):
    """Parse the .jsonl transcript, tolerating any garbage line. On a huge
    file, read only the tail (both scanned events are 'last X', so the tail
    is what matters)."""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        if size > MAX_TRANSCRIPT_BYTES:
            f.seek(-TRANSCRIPT_TAIL_BYTES, os.SEEK_END)
            data = f.read()
            data = data.split(b"\n", 1)[1] if b"\n" in data else b""
        else:
            data = f.read()
    entries = []
    for raw in data.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        if isinstance(obj, dict):
            entries.append(obj)
    return entries


def iter_main_tool_uses(entries):
    """Yield tool_use items from main-chain assistant lines, in issue order."""
    for obj in entries:
        if obj.get("type") != "assistant" or obj.get("isSidechain") is True:
            continue
        msg = obj.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                yield item


def is_notes_or_infra(path):
    """Paths whose edits never void verification: the one notes file
    (CLAUDE.md §3), hook/skill infra, eval result logs, and markdown
    documentation. Markdown is excluded because docs have no runtime surface
    (verifying-before-claiming rule 2's bottom rung) and rarely have a
    hook-detectable verification command — arming on them produced false
    blocks on wrap-up messages after status-doc updates (observed 2026-07-10
    when this hook blocked its own author's summary after PLAN.md edits).
    Accepted false negative per the design contract: a docs-only task
    claiming done without a re-read slips through."""
    if not path:
        return True  # unknown target -> don't count it (conservative)
    p = path.replace("\\", "/")
    if p.rsplit("/", 1)[-1] == "WORKING_NOTES.md":
        return True
    if "/.claude/" in p or p.startswith(".claude/"):
        return True
    if "/evals/results/" in p or p.startswith("evals/results/"):
        return True
    if p.lower().endswith((".md", ".markdown", ".rst", ".txt")):
        return True
    # Session-temp / scratchpad working files are never product code. Location-
    # based on purpose: a .html in the REPO may be product code and must still
    # arm the gate, but the same file authored in a temp dir is a working
    # artifact (observed 2026-07-10: a PDF-source HTML edited in the session
    # scratchpad re-armed the gate although the render was visually verified
    # after the edit — the verify-command regex cannot see render-and-look
    # verification, so location is the reliable signal here).
    if p.startswith(("/private/tmp/", "/tmp/", "/var/folders/")) or "/scratchpad/" in p:
        return True
    # Extensionless repo bookkeeping files (third observed false positive,
    # 2026-07-10: a .gitignore written between a verification run and the
    # summary armed the gate). Same rationale as the .md exclusion: no runtime
    # surface, no hook-detectable verification command.
    if p.rsplit("/", 1)[-1] in (".gitignore", ".gitattributes", "LICENSE", "NOTICE", "CODEOWNERS"):
        return True
    return False


def edit_after_last_verification(entries):
    """Return (edited_path, verify_cmd) if a product-file edit occurred after
    the last plausibly-verifying Bash run; None otherwise. No verifying Bash
    at all -> None (verification may have happened via a non-Bash channel, or
    the change may have no runtime surface — allowing is the conservative
    call)."""
    seq = 0
    last_verify_seq = -1
    last_verify_cmd = None
    last_edit_seq = -1
    last_edit_path = None
    for item in iter_main_tool_uses(entries):
        seq += 1
        name = item.get("name") or ""
        inp = item.get("input")
        if not isinstance(inp, dict):
            inp = {}
        if name == "Bash":
            cmd = inp.get("command")
            if isinstance(cmd, str) and VERIFY_RE.search(cmd):
                last_verify_seq = seq
                last_verify_cmd = cmd
        elif name in EDIT_TOOLS:
            path = inp.get("file_path") or inp.get("notebook_path") or ""
            if isinstance(path, str) and not is_notes_or_infra(path):
                last_edit_seq = seq
                last_edit_path = path
    if last_verify_seq != -1 and last_edit_seq > last_verify_seq:
        return last_edit_path, last_verify_cmd
    return None


def last_assistant_text(entries):
    """Fallback when the input JSON has no last_assistant_message. Stops at
    the NEWEST main-chain assistant entry that has any content: if that
    entry has no non-empty text (e.g. it is tool_use-only), returns "" —
    scanning further back would judge an EARLIER message whose promises the
    later tool calls plausibly executed (a false-positive block on a
    correctly finished turn). Returning "" only allows — the safe
    direction."""
    for obj in reversed(entries):
        if obj.get("type") != "assistant" or obj.get("isSidechain") is True:
            continue
        msg = obj.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        texts = []
        has_content = False
        if isinstance(content, str):
            has_content = bool(content.strip())
            texts = [content]
        elif isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                has_content = True
                if (item.get("type") == "text"
                        and isinstance(item.get("text"), str)):
                    texts.append(item["text"])
        if not has_content:
            continue
        return "\n".join(t for t in texts if t.strip())
    return ""


# --------------------------------------------------------------------- main
def main():
    if os.environ.get("FABLE2OPUS_HOOKS_OFF") == "1":
        return

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(payload, dict):
        return
    if payload.get("stop_hook_active") is True:
        return
    event = payload.get("hook_event_name")
    if event is not None and event not in ("Stop", "SubagentStop"):
        return

    entries = []
    transcript_path = payload.get("transcript_path")
    if isinstance(transcript_path, str) and transcript_path:
        try:
            if os.path.isfile(transcript_path):
                entries = load_transcript_entries(transcript_path)
        except Exception:
            entries = []

    text = payload.get("last_assistant_message")
    if not (isinstance(text, str) and text.strip()):
        text = last_assistant_text(entries)
    if not text.strip():
        return

    cleaned = strip_noise(text)
    reasons = []

    promise = find_promise(cleaned)
    if promise:
        reasons.append(
            'Stop blocked (claim_gate / promise scan): the closing message '
            'ends on an unexecuted commitment: "%s". Perform that action now '
            'with your tools, then close per finishing-the-turn rule 3 '
            '(past-tense claims with evidence only, plus at most one parked '
            'Class B/C block).' % promise
        )

    claim = find_claim(cleaned)
    if claim and entries:
        stale = edit_after_last_verification(entries)
        if stale:
            edited_path, verify_cmd = stale
            cmd_quote = (" ".join((verify_cmd or "").split()))[:80]
            reasons.append(
                'Stop blocked (claim_gate / claim audit): per CLAUDE.md §1 an '
                'edit voids every earlier passing check on the edited code — '
                're-run the relevant verification, confirm affirmative '
                'output, then re-send. Trigger: completion claim ("%s") with '
                '%s edited AFTER the last verification run (`%s`).'
                % (claim[1], edited_path, cmd_quote)
            )

    if not reasons:
        return

    reason = "\n\n".join(reasons)
    if len(reason) > REASON_CAP:
        reason = reason[:REASON_CAP - 1].rstrip() + "…"
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        pass
    sys.exit(0)
