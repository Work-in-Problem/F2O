#!/bin/sh
# Run the notify test suite (this package only).
cd "$(dirname "$0")/.." || exit 1
exec python3 -m unittest discover -s notify/tests -t . -v
