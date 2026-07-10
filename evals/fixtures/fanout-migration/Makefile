# Developer entry points for the ordercore monorepo.

.PHONY: test-all test-billing test-catalog test-shipping test-notify

# Run every package's suite; stops on the first red suite.
test-all: test-billing test-catalog test-shipping test-notify

test-billing:
	./billing/run_tests.sh

test-catalog:
	./catalog/run_tests.sh

test-shipping:
	./shipping/run_tests.sh

test-notify:
	./notify/run_tests.sh
