"""Command-line interface for stockroom."""

import argparse

from stockroom import config
from stockroom.commands import items as item_commands
from stockroom.commands import views as view_commands


def positive_int(value):
    """argparse type: a strictly positive integer quantity."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("{!r} is not an integer".format(value))
    if number <= 0:
        raise argparse.ArgumentTypeError("quantity must be a positive integer")
    return number


def build_parser():
    parser = argparse.ArgumentParser(
        prog="stockroom",
        description="Small command-line inventory tracker.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    p_add = subparsers.add_parser("add", help="Add a quantity of an item.")
    p_add.add_argument("item")
    p_add.add_argument("qty", type=positive_int)
    p_add.set_defaults(func=item_commands.cmd_add)

    p_remove = subparsers.add_parser(
        "remove", help="Remove a quantity of an item."
    )
    p_remove.add_argument("item")
    p_remove.add_argument("qty", type=positive_int)
    p_remove.set_defaults(func=item_commands.cmd_remove)

    p_list = subparsers.add_parser(
        "list", help="Print each item and its quantity."
    )
    p_list.set_defaults(func=view_commands.cmd_list)

    p_report = subparsers.add_parser(
        "report", help="Print the item count and total quantity."
    )
    p_report.set_defaults(func=view_commands.cmd_report)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = config.load_config()
    data_path = config.data_file(cfg)
    return args.func(args, data_path)
