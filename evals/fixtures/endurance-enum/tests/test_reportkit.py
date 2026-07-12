import os
import tempfile
import unittest

from reportkit import charts, render, summary, tables, templates


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


class TestRender(TempDirTest):
    def test_render_page(self):
        p = self.path("report.txt")
        render.render_page([("Totals", "alert: 2\n")], p)
        with open(p) as fh:
            text = fh.read()
        self.assertTrue(text.startswith("RUNLOG REPORT\n"))
        self.assertIn("== Totals ==\nalert: 2\n\n", text)

    def test_append_sections(self):
        p = self.path("report.txt", "existing\n")
        render.append_sections([("Notes", "fine")], p)
        with open(p) as fh:
            self.assertEqual(fh.read(), "existing\n== Notes ==\nfine\n\n")


class TestSummary(TempDirTest):
    def test_load_totals(self):
        p = self.path("s.tsv", "alert\t2\n\ndeploy\t3\n")
        self.assertEqual(summary.load_totals(p), {"alert": 2, "deploy": 3})

    def test_merge_sections(self):
        a = self.path("a.tsv", "alert\t2\ndeploy\t1\n")
        b = self.path("b.tsv", "alert\t1\naudit\t4\n")
        merged = summary.merge_sections([a, b])
        self.assertEqual(merged, {"alert": 3, "deploy": 1, "audit": 4})


class TestTables(TempDirTest):
    def test_read_rows(self):
        p = self.path("t.tsv", "a\tb\n\n1\t2\n")
        self.assertEqual(tables.read_rows(p), [["a", "b"], ["1", "2"]])

    def test_read_table(self):
        p = self.path("t.tsv", "kind\tcount\nalert\t2\n")
        header, rows = tables.read_table(p)
        self.assertEqual(header, ["kind", "count"])
        self.assertEqual(rows, [["alert", "2"]])

    def test_format_table(self):
        text = tables.format_table(["kind", "n"], [["alert", "2"]])
        self.assertEqual(text, "kind   n\nalert  2")

    def test_write_table(self):
        p = self.path("t.txt")
        tables.write_table(["k"], [["v"]], p)
        with open(p) as fh:
            self.assertEqual(fh.read(), "k\nv\n")


class TestCharts(TempDirTest):
    def test_load_series(self):
        p = self.path("s.tsv", "alert\t2\n\ndeploy\t4\n")
        self.assertEqual(
            charts.load_series(p), [("alert", 2.0), ("deploy", 4.0)]
        )

    def test_bar_chart(self):
        chart = charts.bar_chart([("a", 1.0), ("b", 2.0)], width=4)
        self.assertEqual(chart, "a            ##\nb            ####")

    def test_bar_chart_empty(self):
        self.assertEqual(charts.bar_chart([]), "")


class TestTemplates(TempDirTest):
    def test_load_template(self):
        p = self.path("t.tmpl", "hello $name\n")
        tmpl = templates.load_template(p)
        self.assertEqual(tmpl.substitute(name="run"), "hello run\n")

    def test_load_partial(self):
        p = self.path("t.tmpl", "$greeting $name\n")
        self.assertEqual(
            templates.load_partial(p, {"greeting": "hi"}), "hi $name\n"
        )

    def test_render_template(self):
        p = self.path("t.tmpl", "run $run_id\n")
        self.assertEqual(
            templates.render_template(p, {"run_id": "7"}), "run 7\n"
        )


if __name__ == "__main__":
    unittest.main()
