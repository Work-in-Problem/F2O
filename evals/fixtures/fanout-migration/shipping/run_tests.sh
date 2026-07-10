#!/bin/sh
# Run the shipping test suite (this package only).
cd "$(dirname "$0")/.." || exit 1
exec python3 -m unittest discover -s shipping/tests -t . -v
