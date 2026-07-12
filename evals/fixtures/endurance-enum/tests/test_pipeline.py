import json
import os
import tempfile
import unittest

from pipeline import checkpoint, dedupe, ingest, transform, validate


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


class TestIngest(TempDirTest):
    CSV = "kind,id,message\ndeploy, 1 ,go\nalert,2,cpu\n"

    def test_load_events(self):
        p = self.path("events.csv", self.CSV)
        events = ingest.load_events(p)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0], {"kind": "deploy", "id": "1", "message": "go"})

    def test_read_header(self):
        p = self.path("events.csv", self.CSV)
        self.assertEqual(ingest.read_header(p), ["kind", "id", "message"])

    def test_load_batches(self):
        a = self.path("a.jsonl", '{"id": 1}\n\n{"id": 2}\n')
        b = self.path("b.jsonl", '{"id": 3}\n')
        batches = ingest.load_batches([b, a])
        self.assertEqual(batches, [[{"id": 1}, {"id": 2}], [{"id": 3}]])

    def test_count_lines(self):
        p = self.path("x.txt", "one\n\ntwo\n\n")
        self.assertEqual(ingest.count_lines(p), 2)


class TestTransform(TempDirTest):
    def test_load_rules(self):
        p = self.path(
            "rules.jsonl",
            '{"field": "kind", "match": "alert", "replace": "warning"}\n\n',
        )
        rules = transform.load_rules(p)
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]["replace"], "warning")

    def test_apply_rules(self):
        rules = [{"field": "kind", "match": "alert", "replace": "warning"}]
        out = transform.apply_rules([{"kind": "alert"}, {"kind": "deploy"}], rules)
        self.assertEqual([e["kind"] for e in out], ["warning", "deploy"])

    def test_apply_rules_file(self):
        events = self.path("events.jsonl", '{"kind": "alert"}\n{"kind": "audit"}\n')
        rules = self.path(
            "rules.jsonl",
            '{"field": "kind", "match": "audit", "replace": "review"}\n',
        )
        out = transform.apply_rules_file(events, rules)
        self.assertEqual([e["kind"] for e in out], ["alert", "review"])


class TestValidate(TempDirTest):
    def test_load_schema(self):
        p = self.path("schema.json", '{"required": ["id", "kind"]}')
        self.assertEqual(validate.load_schema(p), {"required": ["id", "kind"]})

    def test_validate_file_clean(self):
        p = self.path("events.jsonl", '{"id": 1, "kind": "a"}\n')
        self.assertEqual(validate.validate_file(p, {"required": ["id", "kind"]}), [])

    def test_validate_file_problems(self):
        p = self.path("events.jsonl", '{"id": 1}\n\n{"kind": "a"}\n')
        problems = validate.validate_file(p, {"required": ["id"]})
        self.assertEqual(problems, ["line 3: missing id"])


class TestCheckpoint(TempDirTest):
    def test_roundtrip(self):
        p = self.path("state.json")
        checkpoint.save_checkpoint({"offset": 42, "run": "r1"}, p)
        self.assertEqual(
            checkpoint.load_checkpoint(p), {"offset": 42, "run": "r1"}
        )

    def test_missing_returns_fresh_state(self):
        p = os.path.join(self.dir, "absent.json")
        self.assertEqual(checkpoint.load_checkpoint(p), {"offset": 0})

    def test_save_is_stable_json(self):
        p = self.path("state.json")
        checkpoint.save_checkpoint({"b": 2, "a": 1}, p)
        with open(p) as fh:
            self.assertEqual(fh.read(), json.dumps({"a": 1, "b": 2}, sort_keys=True))


class TestDedupe(TempDirTest):
    def test_load_seen(self):
        p = self.path("seen.txt", "1\n\n2\n")
        self.assertEqual(dedupe.load_seen(p), {"1", "2"})

    def test_dedupe(self):
        events = [{"id": "1"}, {"id": "2"}, {"id": ""}]
        fresh = dedupe.dedupe(events, {"1"})
        self.assertEqual(fresh, [{"id": "2"}, {"id": ""}])


if __name__ == "__main__":
    unittest.main()
