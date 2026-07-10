---
description: Re-enable F2O after /f2o:off — hooks resume (claim gate immediately, Layer-0 injection from the next session)
disable-model-invocation: true
allowed-tools: Bash(rm:*), Bash(ls:*)
---
1. Run: `rm -f ~/.claude/f2o.disabled`
2. Verify it is gone: `ls ~/.claude/f2o.disabled` should fail with "No such file".
3. Confirm to the user, in their language: F2O is back ON — the claim gate enforces
   again immediately; Layer-0 injection returns from the NEXT session. (If the plugin
   itself was hard-disabled, also run: `claude plugin enable f2o@f2o`.)
