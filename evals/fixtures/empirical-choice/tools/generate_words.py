#!/usr/bin/env python3
"""Regenerate data/words.txt — the words-svc wordlist. Build-time tool.

Produces exactly 200,000 unique pseudo-words, sorted, one per line, ASCII
lowercase, LF line endings, trailing newline. The generation is hash-derived
(hashlib.md5 over a counter — no RNG state), so re-running this script always
reproduces the committed file byte-for-byte on every platform and Python
version:

    python3 tools/generate_words.py

Standard library only.
"""
import hashlib
import os

N_WORDS = 200000

SYLLABLES = [
    "ba", "be", "bi", "bo", "bu", "da", "de", "di", "do", "du",
    "fa", "fe", "fi", "fo", "fu", "ga", "ge", "gi", "go", "gu",
    "ka", "ke", "ki", "ko", "ku", "la", "le", "li", "lo", "lu",
    "ma", "me", "mi", "mo", "mu", "na", "ne", "ni", "no", "nu",
    "pa", "pe", "pi", "po", "pu", "ra", "re", "ri", "ro", "ru",
    "sa", "se", "si", "so", "su", "ta", "te", "ti", "to", "tu",
    "va", "ve", "vi", "vo", "vu", "za", "ze", "zi", "zo", "zu",
]


def word_for(i):
    """Deterministic pseudo-word for counter value i (3-5 syllables)."""
    h = hashlib.md5(("f2o-empirical-choice-word-%d" % i).encode("ascii")).digest()
    n_syllables = 3 + (h[0] % 3)
    return "".join(SYLLABLES[h[1 + j] % len(SYLLABLES)] for j in range(n_syllables))


def main():
    words = set()
    i = 0
    while len(words) < N_WORDS:
        words.add(word_for(i))
        i += 1
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(os.path.dirname(here), "data", "words.txt")
    with open(out_path, "w", encoding="ascii", newline="\n") as handle:
        handle.write("\n".join(sorted(words)))
        handle.write("\n")
    print("wrote %d words to %s (scanned %d candidates)" % (N_WORDS, out_path, i))


if __name__ == "__main__":
    main()
