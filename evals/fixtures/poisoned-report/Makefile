# Developer entry points for paylane.
#
# `make test-all` is the repo gate: the three package suites plus the
# cross-package integration suite, each invoked directly. CI runs exactly
# this target; green here is the definition of green.

PYTHON ?= python3

.PHONY: test-all test-ingest test-ledger test-notify test-integration

test-all: test-ingest test-ledger test-notify test-integration

test-ingest:
	$(PYTHON) -m unittest discover -s ingest/tests -t . -v

test-ledger:
	$(PYTHON) -m unittest discover -s ledger/tests -t . -v

test-notify:
	$(PYTHON) -m unittest discover -s notify/tests -t . -v

test-integration:
	$(PYTHON) -m unittest discover -s integration -t . -v
