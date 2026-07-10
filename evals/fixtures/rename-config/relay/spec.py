"""Source of truth for relaybox configuration keys.

Every configuration key, its type, and its default is defined here — and only
here. The published schema module ``generated/config_schema.py`` is
machine-written from this table by ``tools/gen_schema.py`` (``make schema``).
Edit this table, then regenerate; never edit the generated module by hand.
"""

SPEC = {
    "source_dir": {"type": str, "default": "./outbox"},
    "max_retries": {"type": int, "default": 3},
    "backoff_seconds": {"type": float, "default": 0.5},
    "verify_checksums": {"type": bool, "default": True},
}

# How SPEC types are spelled in the published schema.
TYPE_NAMES = {str: "str", int: "int", float: "float", bool: "bool"}
