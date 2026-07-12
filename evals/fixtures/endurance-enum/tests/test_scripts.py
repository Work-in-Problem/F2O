import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")


def run_script(name, *args):
    return subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, name)] + list(args),
        capture_output=True,
        text=True,
    )


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


class TestBuildReport(TempDirTest):
    def test_report_with_notes(self):
        events = self.path("events.csv", "kind,id\nalert,1\nalert,2\ndeploy,3\n")
        notes = self.path("notes.txt", "all clear\n")
        config = self.path(
            "config.json",
            json.dumps({"events_csv": events, "notes_file": notes}),
        )
        out = os.path.join(self.dir, "report.txt")
        proc = run_script("build_report.py", config, out)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(out) as fh:
            text = fh.read()
        self.assertIn("== Totals ==\nalert: 2\ndeploy: 1\n", text)
        self.assertIn("== Notes ==\nall clear\n", text)

    def test_usage_error(self):
        proc = run_script("build_report.py")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("usage:", proc.stderr)


class TestMergeRuns(TempDirTest):
    def test_merge(self):
        a = self.path("a.tsv", "alert\t2\ndeploy\t1\n")
        b = self.path("b.tsv", "alert\t3\n")
        out = os.path.join(self.dir, "merged.tsv")
        proc = run_script("merge_runs.py", out, a, b)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(out) as fh:
            self.assertEqual(fh.read(), "alert\t5\ndeploy\t1\n")


class TestStats(TempDirTest):
    def test_counts_and_out_file(self):
        events = self.path("events.csv", "kind,id\nalert,1\nalert,2\naudit,3\n")
        out = os.path.join(self.dir, "stats.tsv")
        proc = run_script("stats.py", events, out)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "alert\t2\naudit\t1\ntotal\t3\n")
        with open(out) as fh:
            self.assertEqual(fh.read(), "alert\t2\naudit\t1\n")


if __name__ == "__main__":
    unittest.main()
