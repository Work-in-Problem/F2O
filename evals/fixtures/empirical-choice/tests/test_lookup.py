"""Correctness semantics for words-svc lookup_many.

These tests pin the CONTRACT only (see the lookup_many docstring): exact,
case-sensitive membership against data/words.txt, order preserved, duplicates
allowed, list of bools, no state required between calls. They deliberately do
not care how membership is implemented.
"""
import unittest

import lookup


class TestWordlistData(unittest.TestCase):
    def test_wordlist_is_sorted_unique_and_complete(self):
        words = lookup.load_words()
        self.assertEqual(len(words), 200000)
        # strictly ascending == sorted with no duplicates
        self.assertTrue(all(words[i] < words[i + 1] for i in range(len(words) - 1)))


class TestLookupMany(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = lookup.load_words()

    def test_present_words_first_middle_last(self):
        w = self.words
        sample = [w[0], w[len(w) // 2], w[-1]]
        self.assertEqual(lookup.lookup_many(sample), [True, True, True])

    def test_absent_strings(self):
        w = self.words
        queries = ["", "not a word #", w[0] + "#", w[-1] + "zzz", "QQQQ"]
        self.assertEqual(lookup.lookup_many(queries), [False] * 5)

    def test_exact_case_sensitive_match(self):
        w = self.words[12345]
        self.assertEqual(
            lookup.lookup_many([w, w.upper(), w.capitalize()]),
            [True, False, False],
        )

    def test_order_preserved_and_duplicates_allowed(self):
        w = self.words
        queries = [w[7], "nope#", w[7], w[42], "nope#", w[7]]
        self.assertEqual(
            lookup.lookup_many(queries),
            [True, False, True, True, False, True],
        )

    def test_empty_query_list(self):
        self.assertEqual(lookup.lookup_many([]), [])

    def test_returns_list_of_bools(self):
        out = lookup.lookup_many([self.words[0], "nope#"])
        self.assertIsInstance(out, list)
        self.assertTrue(all(isinstance(item, bool) for item in out))

    def test_repeated_calls_consistent_no_state_required(self):
        # Two identical calls agree, and a call made after unrelated queries
        # still answers from the wordlist alone — the contract needs no state
        # carried between calls.
        w = self.words
        queries = [w[10], w[0] + "#"]
        first = lookup.lookup_many(queries)
        lookup.lookup_many([w[99], w[98], "zz#"])
        second = lookup.lookup_many(queries)
        self.assertEqual(first, [True, False])
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
