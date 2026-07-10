import json
import os
import tempfile
import unittest

from generated import config_schema
from relay import config
from relay.spec import SPEC, TYPE_NAMES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigCase(unittest.TestCase):
    def write_config(self, payload):
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        )
        self.addCleanup(os.unlink, handle.name)
        with handle:
            json.dump(payload, handle)
        return handle.name


class TestLoadConfig(ConfigCase):
    def test_defaults_fill_missing_keys(self):
        cfg = config.load_config(self.write_config({}))
        self.assertEqual(cfg["max_retries"], 3)
        self.assertEqual(cfg["source_dir"], "./outbox")
        self.assertEqual(cfg["backoff_seconds"], 0.5)
        self.assertTrue(cfg["verify_checksums"])

    def test_values_override_defaults(self):
        cfg = config.load_config(self.write_config({"max_retries": 9}))
        self.assertEqual(cfg["max_retries"], 9)

    def test_shipped_config_is_valid(self):
        cfg = config.load_config(os.path.join(ROOT, "config.json"))
        self.assertEqual(cfg["max_retries"], 4)

    def test_unknown_key_rejected(self):
        path = self.write_config({"verbose": True})
        with self.assertRaises(config.ConfigError):
            config.load_config(path)

    def test_wrong_type_rejected(self):
        path = self.write_config({"max_retries": "three"})
        with self.assertRaises(config.ConfigError):
            config.load_config(path)

    def test_bool_is_not_an_int(self):
        path = self.write_config({"max_retries": True})
        with self.assertRaises(config.ConfigError):
            config.load_config(path)


class TestSchemaSync(unittest.TestCase):
    def test_published_schema_matches_spec(self):
        expected = {
            key: TYPE_NAMES[entry["type"]] for key, entry in SPEC.items()
        }
        self.assertEqual(config_schema.FIELDS, expected)
