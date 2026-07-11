"""textutil — small pure-string helpers used by the docs pipeline.

Python stdlib only. Every function is pure: no I/O, no state.
"""

import re
import unicodedata


def slugify(text):
    """Lowercase ASCII slug: letters/digits kept, runs of anything else -> '-'.

    Accents are stripped (NFKD), leading/trailing dashes trimmed.
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower())
    return text.strip("-")


def collapse_whitespace(text):
    """Collapse every run of whitespace to a single space and strip ends."""
    return re.sub(r"\s+", " ", text).strip()


def word_count(text):
    """Number of whitespace-separated words in text."""
    return len(text.split())


def capitalize_words(text):
    """Capitalize the first letter of each whitespace-separated word.

    Other letters are left untouched (so 'fooBAR baz' -> 'FooBAR Baz').
    """
    return " ".join(w[:1].upper() + w[1:] for w in text.split())
