"""Configuration loading and validation for relaybox.

``relay.spec.SPEC`` defines the keys; the published schema in
``generated/config_schema.py`` is derived from it. ``load_config`` refuses to
run when the two have drifted, so schema regeneration can never be forgotten
silently.
"""

import json

from generated import config_schema
from relay.spec import SPEC, TYPE_NAMES


class ConfigError(Exception):
    """Invalid configuration file or value."""


class SchemaDriftError(ConfigError):
    """generated/config_schema.py no longer matches relay.spec.SPEC."""


def _check_schema_in_sync():
    expected = {key: TYPE_NAMES[entry["type"]] for key, entry in SPEC.items()}
    if config_schema.FIELDS != expected:
        raise SchemaDriftError(
            "generated/config_schema.py is out of date with relay.spec.SPEC "
            "— regenerate it with: make schema"
        )


def load_config(path):
    """Read ``path`` (JSON object), validate against SPEC, fill defaults."""
    _check_schema_in_sync()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except OSError as exc:
        raise ConfigError("cannot read {}: {}".format(path, exc))
    except ValueError as exc:
        raise ConfigError("invalid JSON in {}: {}".format(path, exc))
    if not isinstance(raw, dict):
        raise ConfigError("config root must be a JSON object")

    unknown = sorted(set(raw) - set(SPEC))
    if unknown:
        raise ConfigError("unknown config key(s): {}".format(", ".join(unknown)))

    cfg = {}
    for key, entry in SPEC.items():
        if key not in raw:
            cfg[key] = entry["default"]
            continue
        value = raw[key]
        ftype = entry["type"]
        if ftype is float and isinstance(value, int) and not isinstance(value, bool):
            value = float(value)  # JSON does not distinguish 2 from 2.0
        if not isinstance(value, ftype) or (ftype is int and isinstance(value, bool)):
            raise ConfigError(
                "config key {!r} must be {}, got {!r}".format(
                    key, TYPE_NAMES[ftype], value
                )
            )
        cfg[key] = value
    return cfg
