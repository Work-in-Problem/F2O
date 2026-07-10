#!/bin/sh
# Run the catalog test suite (this package only).
cd "$(dirname "$0")/.." || exit 1
exec python3 -m unittest discover -s catalog/tests -t . -v
