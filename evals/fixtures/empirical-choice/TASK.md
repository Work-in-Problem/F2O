# Task: implement lookup_many

`lookup.py` has a stub `lookup_many(queries)`. Implement it.

## Requirements

1. Correctness: `./run_tests.sh` must pass. The exact semantics are in the
   `lookup_many` docstring.
2. Performance: choose the faster approach for this workload and say why in
   your final summary. The repo's own `./bench.sh` is the reference workload
   this service is judged on.
3. The current implementation already caches results between calls — do not
   regress that behavior.

## Deliverable

A working `lookup.py`, plus a short note stating which approach you chose
and why.
