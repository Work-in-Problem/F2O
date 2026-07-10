---
description: Soft-disable F2O — hooks go silent (claim gate immediately, Layer-0 injection from the next session); skills and shortcuts stay usable. Undo with /f2o:on.
disable-model-invocation: true
allowed-tools: Bash(touch:*), Bash(ls:*)
---
Executed just now: !`touch ~/.claude/f2o.disabled && ls -la ~/.claude/f2o.disabled && echo STATE_FILE_CREATED`

Based on the result above, confirm to the user in their language: F2O is now SOFT-OFF —
the claim-gate Stop hook stops enforcing immediately; Layer-0 context injection stops
from the NEXT session; all 13 skills and the /f2o:* shortcuts remain fully usable.
Re-enable anytime with /f2o:on. Hard off (removes skills/hooks entirely, next session):
`claude plugin disable f2o@f2o`. If the result shows an error instead, report it honestly.
