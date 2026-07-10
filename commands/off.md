---
description: Soft-disable F2O — hooks go silent (claim gate immediately, Layer-0 injection from the next session); skills and shortcuts stay usable. Undo with /f2o:on.
disable-model-invocation: true
allowed-tools: Bash(touch:*), Bash(ls:*)
---
1. Run: `touch ~/.claude/f2o.disabled`
2. Verify it exists: `ls -la ~/.claude/f2o.disabled`
3. Confirm to the user, in their language: F2O is now SOFT-OFF — the claim-gate Stop
   hook stops enforcing immediately; Layer-0 context injection stops from the NEXT
   session; all 13 skills and the /f2o:* shortcuts remain fully usable on demand.
   Re-enable anytime with /f2o:on. For a HARD off (remove skills/hooks entirely):
   `claude plugin disable f2o@f2o` (takes effect next session or after /reload-plugins).
