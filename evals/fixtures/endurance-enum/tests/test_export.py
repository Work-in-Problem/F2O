import os
import tempfile
import unittest

from pipeline import export


class TestExport(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_write_csv(self):
        p = os.path.join(self.dir, "out.csv")
        export.write_csv(
            [{"id": "1", "kind": "alert"}, {"id": "2"}], p, ["id", "kind"]
        )
        with open(p, newline="") as fh:
            self.assertEqual(fh.read(), "id,kind\r\n1,alert\r\n2,\r\n")

    def test_write_summary(self):
        p = os.path.join(self.dir, "sum.tsv")
        export.write_summary({"b": 2, "a": 1}, p)
        with open(p) as fh:
            self.assertEqual(fh.read(), "a\t1\nb\t2\n")

    def test_export_partitions(self):
        groups = {
            "alert": [{"id": "3", "msg": "cpu"}],
            "deploy": [{"id": "1", "msg": "go"}, {"id": "2", "msg": "done"}],
        }
        written = export.export_partitions(groups, self.dir)
        self.assertEqual(
            [os.path.basename(w) for w in written], ["alert.tsv", "deploy.tsv"]
        )
        with open(written[1]) as fh:
            self.assertEqual(fh.read(), "1\tgo\n2\tdone\n")

    def test_write_manifest(self):
        p = os.path.join(self.dir, "manifest.txt")
        export.write_manifest(["b.tsv", "a.tsv"], p)
        with open(p) as fh:
            self.assertEqual(fh.read(), "a.tsv\nb.tsv\n")


if __name__ == "__main__":
    unittest.main()
