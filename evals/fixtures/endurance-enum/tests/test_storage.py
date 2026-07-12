import os
import tempfile
import unittest

from storage import archive, cache, catalog, journal


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


class TestCache(TempDirTest):
    def test_set_then_get(self):
        cache.set(self.dir, "greeting", "hello\nworld\n")
        self.assertEqual(cache.get(self.dir, "greeting"), "hello\nworld\n")

    def test_get_default(self):
        self.assertEqual(cache.get(self.dir, "absent", default="x"), "x")

    def test_peek(self):
        cache.set(self.dir, "greeting", "hello\nworld\n")
        self.assertEqual(cache.peek(self.dir, "greeting"), "hello")
        self.assertIsNone(cache.peek(self.dir, "absent"))


class TestArchive(TempDirTest):
    def test_pack_unpack_roundtrip(self):
        a = self.path("a.txt", "alpha\n")
        b = self.path("b.txt", "beta\ngamma\n")
        bundle = os.path.join(self.dir, "run.bundle")
        archive.pack([b, a], bundle)
        entries = archive.unpack(bundle)
        self.assertEqual(list(entries), ["a.txt", "b.txt"])
        self.assertEqual(entries["b.txt"], "beta\ngamma\n")


class TestCatalog(TempDirTest):
    def test_roundtrip(self):
        p = os.path.join(self.dir, "index.json")
        catalog.save_index({"run1": "a.bundle"}, p)
        self.assertEqual(catalog.load_index(p), {"run1": "a.bundle"})

    def test_missing_index(self):
        p = os.path.join(self.dir, "absent.json")
        self.assertEqual(catalog.load_index(p), {})
        self.assertEqual(catalog.entry_count(p), 0)

    def test_entry_count(self):
        p = os.path.join(self.dir, "index.json")
        catalog.save_index({"a": "1", "b": "2"}, p)
        self.assertEqual(catalog.entry_count(p), 2)


class TestJournal(TempDirTest):
    def test_writer_then_reader(self):
        p = os.path.join(self.dir, "run.journal")
        writer = journal.JournalWriter(p)
        writer.record("started")
        writer.record("finished")
        reader = journal.JournalReader(p)
        self.assertEqual(reader.entries(), ["started", "finished"])

    def test_replay(self):
        p = self.path("run.journal", "one\n\ntwo\n")
        self.assertEqual(journal.replay(p), ["one", "two"])


if __name__ == "__main__":
    unittest.main()
