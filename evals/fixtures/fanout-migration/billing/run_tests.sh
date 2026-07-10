#!/bin/sh
# Run the billing test suite (this package only).
cd "$(dirname "$0")/.." || exit 1
exec python3 -m unittest discover -s billing/tests -t . -v
