#!/bin/sh
# Run the full unittest suite for this project.
# -W ignore keeps runner output identical across Python versions.
cd "$(dirname "$0")" || exit 1
exec python3 -W ignore -m unittest discover -s tests -t . -v "$@"
