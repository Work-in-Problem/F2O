#!/usr/bin/env python3
"""Nightly re-delivery sweep (cron entry point).

Standalone by design: cron runs this file directly with a bare PYTHONPATH,
so it reads config.json itself instead of importing the relay package.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config.json")


def main():
    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        raw = json.load(handle)

    budget = raw["max_retries"]
    source_dir = raw.get("source_dir", "./outbox")

    print("nightly re-delivery sweep (dry run)")
    print("retry budget per stuck delivery: {}".format(budget))

    outbox = os.path.join(ROOT, source_dir)
    stuck = 0
    if os.path.isdir(outbox):
        stuck = len([name for name in os.listdir(outbox) if name.endswith(".json")])
    print("stuck deliveries found: {}".format(stuck))
    print("nothing sent (dry run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
