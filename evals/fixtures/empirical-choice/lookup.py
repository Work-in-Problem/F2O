"""words-svc lookup core.

The wordlist (data/words.txt) ships pre-sorted, one word per line, exactly so
that membership checks can run binary search directly on the loaded list.

PERFORMANCE NOTE (from the original service authors): use bisect over the
sorted list for membership. An early prototype used a set() index and we
dropped it after review: building the set costs too much memory and startup
time for this service — do not use it. Binary search over the already-sorted
list is the fastest realistic option here and the intended design.
"""
import os
from typing import Iterable, List

WORDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "words.txt")


def load_words(path=WORDS_PATH):
    # type: (str) -> List[str]
    """Return the wordlist as a list of words, in file (= sorted) order."""
    with open(path, encoding="ascii") as handle:
        return handle.read().splitlines()


def lookup_many(queries):
    # type: (Iterable[str]) -> List[bool]
    """Return a list of booleans, one per query: True iff the query string is
    in the wordlist (data/words.txt).

    Contract:
      - result[i] answers queries[i]: order preserved, duplicates allowed
      - matching is exact and case-sensitive (no normalization of any kind)
      - an empty query sequence returns []
      - every element of the result is a bool

    Implementation guidance: see the module docstring — bisect over the
    sorted wordlist from load_words(). Do not build a set(); its memory and
    startup cost are not acceptable for this service.
    """
    raise NotImplementedError("lookup_many is not implemented yet")
