import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import storage


class SQLiteStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.data = root / "data"
        self.logs = root / "logs"
        self.data.mkdir()
        self.logs.mkdir()
        self.patches = [
            patch.object(storage, "DATA_DIR", self.data),
            patch.object(storage, "LOG_DIR", self.logs),
        ]
        for item in self.patches:
            item.start()
        self.addCleanup(self.cleanup)

    def cleanup(self):
        for item in reversed(self.patches):
            item.stop()
        self.temp.cleanup()

    def test_initialize_imports_json_once_and_sqlite_becomes_canonical(self):
        legacy = {"events": [{"id": "lesson-1"}], "attendance": []}
        (self.data / "learning.json").write_text(
            json.dumps(legacy), encoding="utf-8"
        )

        storage.initialize()
        self.assertTrue(storage.database_path().is_file())
        self.assertEqual(storage.read_json("learning.json"), legacy)

        updated = {"events": [{"id": "lesson-2"}], "attendance": [{"id": "a1"}]}
        storage.write_json("learning.json", updated)
        storage.initialize()
        self.assertEqual(storage.read_json("learning.json"), updated)
        self.assertEqual(json.loads((self.data / "learning.json").read_text()), legacy)

        connection = sqlite3.connect(storage.database_path())
        try:
            payload = connection.execute(
                "SELECT payload FROM documents WHERE name='learning.json'"
            ).fetchone()[0]
            attendance_id = connection.execute(
                """SELECT record_id FROM learning_records
                   WHERE collection='attendance'"""
            ).fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(json.loads(payload), updated)
        self.assertEqual(attendance_id, "a1")

    def test_atomic_transaction_rolls_back_all_documents_and_audit(self):
        storage.initialize()
        storage.write_json("learning.json", {"events": []})

        with self.assertRaisesRegex(RuntimeError, "stop"):
            with storage.atomic_transaction():
                storage.write_json("learning.json", {"events": [{"id": "bad"}]})
                storage.write_json("submissions.json", {"s1": [{"id": "bad"}]})
                storage.audit("test.rollback", "teacher", "127.0.0.1")
                raise RuntimeError("stop")

        self.assertEqual(storage.read_json("learning.json"), {"events": []})
        self.assertEqual(storage.read_json("submissions.json"), {})
        connection = sqlite3.connect(storage.database_path())
        try:
            count = connection.execute(
                "SELECT count(*) FROM audit_events WHERE event='test.rollback'"
            ).fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(count, 0)

    def test_committed_audit_is_queryable_and_has_jsonl_compatibility_copy(self):
        storage.initialize()
        storage.audit("attendance.updated", "teacher", "10.0.0.1", {"event_id": "e1"})

        connection = sqlite3.connect(storage.database_path())
        try:
            row = connection.execute(
                "SELECT actor, details FROM audit_events WHERE event='attendance.updated'"
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(row[0], "teacher")
        self.assertEqual(json.loads(row[1]), {"event_id": "e1"})
        line = json.loads((self.logs / "audit.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(line["event"], "attendance.updated")


if __name__ == "__main__":
    unittest.main()
