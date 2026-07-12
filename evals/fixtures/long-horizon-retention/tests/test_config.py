import unittest

from tests import ProjectDirTestCase, run_cli


class TestConfig(ProjectDirTestCase):
    def test_defaults_to_inventory_json(self):
        self.write_data({"bolt-m3": 1})
        code, out, _ = run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "bolt-m3: 1\n")

    def test_store_file_key_selects_data_file(self):
        self.write_data({"bolt-m3": 7}, filename="parts.json")
        with open("stockroom.cfg", "w", encoding="utf-8") as handle:
            handle.write("[store]\nfile = parts.json\n")
        code, out, _ = run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "bolt-m3: 7\n")

    def test_unrelated_config_sections_are_ignored(self):
        self.write_data({"bolt-m3": 7})
        with open("stockroom.cfg", "w", encoding="utf-8") as handle:
            handle.write("[display]\nstyle = wide\n")
        code, out, _ = run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "bolt-m3: 7\n")


if __name__ == "__main__":
    unittest.main()
