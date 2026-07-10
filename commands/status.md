---
description: Report F2O state — soft-off state file, what is currently active
disable-model-invocation: true
allowed-tools: Bash(ls:*)
---
State probe (exit 0 line = soft-off engaged; "No such file" = ON):
!`ls -la ~/.claude/f2o.disabled 2>&1 || echo "ON (no state file)"`

Report to the user in their language, based on the probe above:
- State: ON (default) or SOFT-OFF (state file present).
- ON means: Layer-0 core rules injected each session + claim-gate Stop hook enforcing
  + 13 skills auto-loading by situation.
- SOFT-OFF means: hooks silent, but all 13 skills and /f2o:* shortcuts still work on demand.
- Toggles: /f2o:off · /f2o:on · hard off: `claude plugin disable f2o@f2o`.
