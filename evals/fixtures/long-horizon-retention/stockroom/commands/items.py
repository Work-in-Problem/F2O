"""Subcommands that change the inventory: add and remove."""

from stockroom import store


def cmd_add(args, data_path):
    items = store.load(data_path)
    new_qty = items.get(args.item, 0) + args.qty
    items[args.item] = new_qty
    store.save(data_path, items)
    print("added {} {} (now {})".format(args.qty, args.item, new_qty))
    return 0


def cmd_remove(args, data_path):
    items = store.load(data_path)
    if args.item not in items:
        store.fail("unknown item: {}".format(args.item))
    new_qty = items[args.item] - args.qty
    items[args.item] = new_qty
    store.save(data_path, items)
    print("removed {} {} (now {})".format(args.qty, args.item, new_qty))
    return 0
