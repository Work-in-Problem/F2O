import unittest

from tests import ProjectDirTestCase, run_cli


class TestList(ProjectDirTestCase):
    def test_list_prints_items_sorted_by_name(self):
        self.write_data({"washer": 95, "bolt-m3": 240})
        code, out, _ = run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "bolt-m3: 240\nwasher: 95\n")

    def test_list_empty_inventory_prints_nothing(self):
        self.write_data({})
        code, out, _ = run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")


class TestReport(ProjectDirTestCase):
    def test_report_counts_and_totals(self):
        self.write_data({"washer": 95, "bolt-m3": 240, "hex-nut": 180})
        code, out, _ = run_cli(["report"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "items: 3\ntotal: 515\n")

    def test_report_empty_inventory(self):
        self.write_data({})
        code, out, _ = run_cli(["report"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "items: 0\ntotal: 0\n")


class TestDataFileErrors(ProjectDirTestCase):
    def test_missing_data_file_exits_2(self):
        code, _, err = run_cli(["list"])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: cannot read"))

    def test_invalid_json_exits_2(self):
        with open("inventory.json", "w", encoding="utf-8") as handle:
            handle.write("not json{")
        code, _, err = run_cli(["list"])
        self.assertEqual(code, 2)
        self.assertIn("not valid JSON", err)

    def test_unrecognized_shape_exits_2(self):
        with open("inventory.json", "w", encoding="utf-8") as handle:
            handle.write('["just", "a", "list"]\n')
        code, _, err = run_cli(["list"])
        self.assertEqual(code, 2)
        self.assertIn("unrecognized", err)


if __name__ == "__main__":
    unittest.main()
