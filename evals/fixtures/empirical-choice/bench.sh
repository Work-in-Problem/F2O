#!/bin/sh
# Reference workload benchmark for words-svc. Times the delivered
# lookup.lookup_many implementation; prints median of 5 timed runs.
cd "$(dirname "$0")" || exit 1
exec python3 bench.py "$@"
