import unittest

from tests import ProjectDirTestCase, run_cli


class TestAdd(ProjectDirTestCase):
    def test_add_existing_item_increments(self):
        self.write_data({"bolt-m3": 40})
        code, out, _ = run_cli(["add", "bolt-m3", "12"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "added 12 bolt-m3 (now 52)\n")

    def test_add_new_item_starts_from_zero(self):
        self.write_data({"bolt-m3": 40})
        code, out, _ = run_cli(["add", "washer", "5"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "added 5 washer (now 5)\n")

    def test_add_persists_to_data_file(self):
        self.write_data({"bolt-m3": 40})
        run_cli(["add", "bolt-m3", "12"])
        code, out, _ = run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertIn("bolt-m3: 52", out)

    def test_add_rejects_non_positive_quantity(self):
        self.write_data({"bolt-m3": 40})
        code, _, err = run_cli(["add", "bolt-m3", "0"])
        self.assertEqual(code, 2)
        self.assertIn("positive", err)

    def test_add_rejects_non_integer_quantity(self):
        self.write_data({"bolt-m3": 40})
        code, _, _ = run_cli(["add", "bolt-m3", "many"])
        self.assertEqual(code, 2)


class TestRemove(ProjectDirTestCase):
    def test_remove_decrements(self):
        self.write_data({"bolt-m3": 40})
        code, out, _ = run_cli(["remove", "bolt-m3", "15"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "removed 15 bolt-m3 (now 25)\n")

    def test_remove_persists_to_data_file(self):
        self.write_data({"bolt-m3": 40})
        run_cli(["remove", "bolt-m3", "15"])
        code, out, _ = run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertIn("bolt-m3: 25", out)

    def test_remove_unknown_item_fails(self):
        self.write_data({"bolt-m3": 40})
        code, _, err = run_cli(["remove", "ghost", "1"])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith("error: unknown item: ghost"))


if __name__ == "__main__":
    unittest.main()
