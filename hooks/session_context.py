#!/usr/bin/env python3
"""Fable2Opus Layer 2 — SessionStart hook: inject the Layer-0 core rules.

Reads core/CLAUDE-core.md + core/constants.md and emits them as SessionStart
additionalContext, so every session in which the F2O plugin is enabled gets the
always-on core (claim audit, autonomy triage, notes convention, constants,
skill router) without copying anything into the project's CLAUDE.md.

Contract (verified against https://code.claude.com/docs/en/hooks 2026-07-10):
  stdin : SessionStart hook input JSON (tolerated if absent/garbage)
  stdout: {"hookSpecificOutput": {"hookEventName": "SessionStart",
           "additionalContext": "<text>"}}   on success
  exit 0 always — any failure exits silently; this hook must never brick a
  session. FABLE2OPUS_HOOKS_OFF=1 disables it (same escape as claim_gate.py).

Core-file lookup order:
  1. $CLAUDE_PLUGIN_ROOT/core/   (installed as a plugin)
  2. <script_dir>/../core/       (running from a checkout / manual install)

Skip condition: if the session's cwd already contains a CLAUDE.md carrying the
Layer-0 marker, injection is skipped to avoid double context (e.g. inside the
F2O repo itself or a project that pasted the core manually).
"""

import json
import os
import sys

MARKER = "Fable2Opus — Layer 0 Core"
MAX_CHARS = 1950  # Claude Code persists ~2KB of SessionStart context (measured 2026-07-10); inject a digest + file pointers, never the full core


def main():
    if os.environ.get("FABLE2OPUS_HOOKS_OFF") == "1":
        return

    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    # Skip when the project already carries Layer 0 in its own CLAUDE.md.
    cwd = payload.get("cwd") or os.getcwd()
    try:
        with open(os.path.join(cwd, "CLAUDE.md"), encoding="utf-8") as f:
            if MARKER in f.read():
                return
    except Exception:
        pass

    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = []
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        candidates.append(os.path.join(plugin_root, "core"))
    candidates.append(os.path.normpath(os.path.join(script_dir, "..", "core")))

    compact = base_used = None
    for base in candidates:
        try:
            with open(os.path.join(base, "CORE-compact.md"), encoding="utf-8") as f:
                compact = f.read()
            base_used = base
            break
        except Exception:
            continue
    if not compact:
        return  # nothing to inject; never fail the session

    # Rules first, resolved path as an optional footer: the persisted budget is
    # ~2KB and user path lengths vary by machine — if the footer would overflow
    # the budget, drop the footer, never the rules. Hard truncation remains only
    # as a regression guard for an oversized digest file.
    text = compact.strip()
    footer = "\nFull core files: %s (CLAUDE-core.md, constants.md)" % base_used
    if len(text) + len(footer) <= MAX_CHARS:
        text += footer
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n[...truncated: MAX_CHARS guard]"

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": text,
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
