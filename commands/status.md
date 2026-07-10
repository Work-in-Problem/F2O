---
description: Report F2O state — soft-off state file, what is currently active
disable-model-invocation: true
allowed-tools: Bash(ls:*)
---
1. Run: `ls ~/.claude/f2o.disabled` (exit 0 = soft-off engaged; "No such file" = ON).
2. Report to the user, in their language:
   - State: ON (default) or SOFT-OFF (state file present since <file mtime>).
   - What ON means: Layer-0 core rules injected each session + claim-gate Stop hook
     enforcing + 13 skills auto-loading by situation.
   - What SOFT-OFF means: hooks silent, but all 13 skills and /f2o:* shortcuts still
     work on demand.
   - Toggles: /f2o:off · /f2o:on · hard off: `claude plugin disable f2o@f2o`.
