# Developer entry points for relaybox.

PYTHON ?= python3

.PHONY: check schema

# Run the project's test suite.
check:
	$(PYTHON) -m unittest discover -s checks -t . -p "check_*.py" -v

# Regenerate machine-written modules under generated/ from relay/spec.py.
schema:
	$(PYTHON) tools/gen_schema.py
