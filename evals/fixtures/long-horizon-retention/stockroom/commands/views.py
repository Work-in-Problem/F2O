"""Subcommands that only read the inventory: list and report."""

from stockroom import store


def cmd_list(args, data_path):
    items = store.load(data_path)
    for name in sorted(items):
        print("{}: {}".format(name, items[name]))
    return 0


def cmd_report(args, data_path):
    items = store.load(data_path)
    print("items: {}".format(len(items)))
    print("total: {}".format(sum(items.values())))
    return 0
