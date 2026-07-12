import os
import tempfile
import unittest

from utils import csvkit, jsonkit, lockfile, textio


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def path(self, name, content=None):
        p = os.path.join(self.dir, name)
        if content is not None:
            with open(p, "w") as fh:
                fh.write(content)
        return p


class TestTextio(TempDirTest):
    def test_write_then_read(self):
        p = os.path.join(self.dir, "note.txt")
        textio.write_text(p, "hello\n")
        self.assertEqual(textio.read_text(p), "hello\n")

    def test_concat_files(self):
        a = self.path("a.txt", "one\n")
        b = self.path("b.txt", "two\n")
        out = os.path.join(self.dir, "all.txt")
        textio.concat_files([a, b], out)
        self.assertEqual(textio.read_text(out), "one\ntwo\n")

    def test_head(self):
        p = self.path("x.txt", "1\n2\n3\n")
        self.assertEqual(textio.head(p, limit=2), ["1", "2"])


class TestCsvkit(TempDirTest):
    CSV = "id,kind\n1,alert\n2,deploy\n"

    def test_read_csv(self):
        p = self.path("e.csv", self.CSV)
        rows = csvkit.read_csv(p)
        self.assertEqual(len(rows), 2)
        self.assertEqual(dict(rows[0]), {"id": "1", "kind": "alert"})

    def test_column(self):
        p = self.path("e.csv", self.CSV)
        self.assertEqual(csvkit.column(p, "kind"), ["alert", "deploy"])

    def test_write_csv_rows(self):
        p = os.path.join(self.dir, "out.csv")
        csvkit.write_csv_rows(p, ["id"], [{"id": "9"}])
        with open(p, newline="") as fh:
            self.assertEqual(fh.read(), "id\r\n9\r\n")


class TestJsonkit(TempDirTest):
    def test_roundtrip(self):
        p = os.path.join(self.dir, "doc.json")
        jsonkit.dump_json({"b": 2, "a": 1}, p)
        self.assertEqual(jsonkit.load_json(p), {"a": 1, "b": 2})
        with open(p) as fh:
            text = fh.read()
        self.assertTrue(text.startswith('{\n  "a": 1'))
        self.assertTrue(text.endswith("\n"))

    def test_load_jsonl(self):
        p = self.path("d.jsonl", '{"a": 1}\n\n{"a": 2}\n')
        self.assertEqual(jsonkit.load_jsonl(p), [{"a": 1}, {"a": 2}])


class TestLockfile(TempDirTest):
    def test_acquire_release(self):
        p = os.path.join(self.dir, "job.lock")
        self.assertTrue(lockfile.acquire(p, "worker-1"))
        self.assertFalse(lockfile.acquire(p, "worker-2"))
        self.assertEqual(lockfile.holder(p), "worker-1")
        self.assertTrue(lockfile.release(p))
        self.assertFalse(lockfile.release(p))
        self.assertIsNone(lockfile.holder(p))


if __name__ == "__main__":
    unittest.main()
