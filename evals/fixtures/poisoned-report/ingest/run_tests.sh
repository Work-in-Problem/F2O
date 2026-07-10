#!/bin/sh
# Run the ingest package's test suite.
cd "$(dirname "$0")/.." || exit 1
exec python3 -m unittest discover -s ingest/tests -t . -v
