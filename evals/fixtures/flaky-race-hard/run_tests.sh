#!/bin/sh
# Run the full unittest suite for this project: ./run_tests.sh
cd "$(dirname "$0")" || exit 1
exec python3 -m unittest discover -s tests -t . -v
