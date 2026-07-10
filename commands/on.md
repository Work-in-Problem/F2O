---
description: Re-enable F2O after /f2o:off — hooks resume (claim gate immediately, Layer-0 injection from the next session)
disable-model-invocation: true
allowed-tools: Bash(rm:*), Bash(ls:*)
---
Executed just now: !`rm -f ~/.claude/f2o.disabled && (ls ~/.claude/f2o.disabled 2>&1 || echo STATE_FILE_REMOVED)`

Based on the result above, confirm to the user in their language: F2O is back ON —
the claim gate enforces again immediately; Layer-0 injection returns from the NEXT
session. (If the plugin itself was hard-disabled, also run: `claude plugin enable f2o@f2o`.)
If the result shows an error instead, report it honestly.
