import json
import os
import subprocess
import sys
import tempfile
import unittest

import cardparse


class TestParseBasics(unittest.TestCase):
    def test_single_card_single_property(self):
        cards = cardparse.parse("BEGIN:CARD\nname:Ada\nEND:CARD\n")
        self.assertEqual(cards, [{"name": ["Ada"]}])

    def test_key_stored_lowercase(self):
        cards = cardparse.parse("BEGIN:CARD\nNAME:Ada\nEND:CARD\n")
        self.assertEqual(cards, [{"name": ["Ada"]}])

    def test_property_order_preserved(self):
        cards = cardparse.parse(
            "BEGIN:CARD\nname:Ada\nemail:ada@example.org\nEND:CARD\n"
        )
        self.assertEqual(list(cards[0].keys()), ["name", "email"])

    def test_multi_value_split_on_semicolon(self):
        cards = cardparse.parse("BEGIN:CARD\ntel:1;2;3\nEND:CARD\n")
        self.assertEqual(cards, [{"tel": ["1", "2", "3"]}])

    def test_empty_value_is_single_empty_part(self):
        cards = cardparse.parse("BEGIN:CARD\nnote:\nEND:CARD\n")
        self.assertEqual(cards, [{"note": [""]}])

    def test_two_cards_in_order(self):
        cards = cardparse.parse(
            "BEGIN:CARD\nname:A\nEND:CARD\nBEGIN:CARD\nname:B\nEND:CARD\n"
        )
        self.assertEqual(cards, [{"name": ["A"]}, {"name": ["B"]}])

    def test_blank_line_between_cards_ignored(self):
        cards = cardparse.parse(
            "BEGIN:CARD\nname:A\nEND:CARD\n\nBEGIN:CARD\nname:B\nEND:CARD\n"
        )
        self.assertEqual(cards, [{"name": ["A"]}, {"name": ["B"]}])


class TestCli(unittest.TestCase):
    def test_cli_prints_json_and_exits_zero(self):
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as handle:
            handle.write("BEGIN:CARD\nname:Ada\ntel:1;2\nEND:CARD\n")
        try:
            module = os.path.join(os.path.dirname(__file__), "..", "cardparse.py")
            proc = subprocess.run(
                [sys.executable, module, path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(
                json.loads(proc.stdout), [{"name": ["Ada"], "tel": ["1", "2"]}]
            )
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
