"""Timestamp helpers for the notify package.

``parse_when`` is the legacy lenient parser. It predates the monorepo and
has been copy-pasted into every service that needed it. Deprecated:
MIGRATION.md at the repo root specifies its strict replacement.
"""

from datetime import datetime

# Formats the lenient parser tolerates, tried in order.
_WHEN_FORMATS = (
    "%Y-%m-%d %H:%M:%S",  # "2024-03-05 14:30:00"
    "%Y-%m-%dT%H:%M:%S",  # "2024-03-05T14:30:00"
    "%d/%m/%Y %H:%M",     # "05/03/2024 14:30"
)


def parse_when(text):
    """Parse a timestamp in any tolerated format.

    Lenient by design: surrounding whitespace is ignored, and unparseable
    input (including None or empty strings) yields None so callers can fall
    back to their own defaults.
    """
    if not text:
        return None
    cleaned = str(text).strip()
    for fmt in _WHEN_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None
