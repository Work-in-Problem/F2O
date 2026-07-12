"""Configuration handling: read stockroom.cfg from the working directory."""

import configparser
import os

CONFIG_NAME = "stockroom.cfg"
DEFAULT_DATA_FILE = "inventory.json"


def load_config(directory=None):
    """Return a ConfigParser loaded from stockroom.cfg in `directory`.

    A missing config file yields an empty parser — callers rely on
    fallbacks for every key.
    """
    parser = configparser.ConfigParser()
    parser.read(os.path.join(directory or os.getcwd(), CONFIG_NAME))
    return parser


def data_file(parser):
    """Path of the JSON data file (relative paths resolve against the cwd)."""
    return parser.get("store", "file", fallback=DEFAULT_DATA_FILE)
