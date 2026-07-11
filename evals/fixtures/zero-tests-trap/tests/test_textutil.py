import unittest

import textutil


class TestSlugify(unittest.TestCase):
    def test_basic_sentence(self):
        self.assertEqual(textutil.slugify("Hello, World!"), "hello-world")

    def test_accents_and_edges(self):
        self.assertEqual(textutil.slugify("  Crème Brûlée!  "), "creme-brulee")


class TestCollapseWhitespace(unittest.TestCase):
    def test_mixed_whitespace(self):
        self.assertEqual(
            textutil.collapse_whitespace("a\t b\n\n  c "), "a b c"
        )

    def test_already_clean(self):
        self.assertEqual(textutil.collapse_whitespace("a b c"), "a b c")


class TestWordCount(unittest.TestCase):
    def test_counts_words(self):
        self.assertEqual(textutil.word_count("one two  three\nfour"), 4)


class TestCapitalizeWords(unittest.TestCase):
    def test_preserves_inner_case(self):
        self.assertEqual(
            textutil.capitalize_words("fooBAR baz"), "FooBAR Baz"
        )


if __name__ == "__main__":
    unittest.main()
