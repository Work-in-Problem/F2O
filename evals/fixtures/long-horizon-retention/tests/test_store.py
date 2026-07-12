import contextlib
import io
import json
import unittest

from stockroom import store
from tests import ProjectDirTestCase


class TestRoundTrip(ProjectDirTestCase):
    def test_save_then_load_round_trips(self):
        path = self.write_data({"bolt-m3": 240, "washer": 95})
        items = store.load(path)
        store.save("copy.json", items)
        self.assertEqual(store.load("copy.json"), items)

    def test_save_is_deterministic(self):
        path = self.write_data({"washer": 95, "bolt-m3": 240})
        items = store.load(path)
        store.save("a.json", items)
        store.save("b.json", items)
        with open("a.json", encoding="utf-8") as first:
            with open("b.json", encoding="utf-8") as second:
                self.assertEqual(first.read(), second.read())

    def test_save_writes_canonical_json(self):
        path = self.write_data({"washer": 95, "bolt-m3": 240})
        store.save("out.json", store.load(path))
        with open("out.json", encoding="utf-8") as handle:
            text = handle.read()
        self.assertEqual(
            text, json.dumps(json.loads(text), indent=2, sort_keys=True) + "\n"
        )
        self.assertFalse(text.endswith("\n\n"))


class TestLoadErrors(ProjectDirTestCase):
    def test_load_missing_file_exits_2(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as ctx:
                store.load("nope.json")
        self.assertEqual(ctx.exception.code, 2)
        self.assertTrue(stderr.getvalue().startswith("error:"))

    def test_load_rejects_non_object_payload(self):
        with open("bad.json", "w", encoding="utf-8") as handle:
            handle.write("[1, 2, 3]\n")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as ctx:
                store.load("bad.json")
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("unrecognized", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
