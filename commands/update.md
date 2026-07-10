---
description: Check for a newer F2O version (one on-demand request to GitHub — no automatic phone-home) and show update/rollback commands
disable-model-invocation: true
allowed-tools: Bash(curl:*), Bash(cat:*)
---
Installed version: !`cat "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin).get('version','unknown'))" 2>/dev/null || echo unknown`
Latest on GitHub: !`curl -fsS --max-time 8 https://raw.githubusercontent.com/Work-in-Problem/F2O/main/.claude-plugin/plugin.json 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin).get('version','unknown'))" 2>/dev/null || echo "unreachable (offline?)"`

Compare the two version strings above and tell the user, in their language:
- If they match: F2O is up to date (state the version).
- If GitHub is newer: a new version is available — update with:
  `claude plugin marketplace update f2o` then `claude plugin update f2o@f2o`,
  then /reload-plugins (or a new session). Changelog:
  https://github.com/Work-in-Problem/F2O/blob/main/CHANGELOG.md
- If unreachable: say the check could not reach GitHub and to try again later.
- Always append one line: rollback to any previous version is possible via
  `claude plugin marketplace add Work-in-Problem/F2O@<tag>` (tags on GitHub Releases).
