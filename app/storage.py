"""SQLite-backed persistence with automatic import of the legacy JSON store.

The public ``read_json``/``write_json`` API is intentionally retained so the
application services can migrate without a flag day. JSON files in ``data``
are read only as one-time migration sources; SQLite is canonical afterwards.
"""
from __future__ import annotations

import copy
import functools
import json
import logging
import os
import sqlite3
import tempfile
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import DATA_DIR, LOG_DIR

_LOCK = threading.RLock()
_LOCAL = threading.local()
_SCHEMA_READY: set[str] = set()
_CACHE: dict[tuple[str, str], Any] = {}
logger = logging.getLogger(__name__)

DATABASE_FILENAME = "lms.sqlite3"
SCHEMA_VERSION = 2


def database_path() -> Path:
    """Return the database for the active runtime data directory."""
    return DATA_DIR / DATABASE_FILENAME


def _cache_key(name: str) -> tuple[str, str]:
    return (str(database_path().resolve()), name)


def _journal_path() -> Path:
    # Kept only to recover transactions created by releases before SQLite.
    return DATA_DIR / ".transaction.json"


def _path(name: str) -> Path:
    if name.endswith(".jsonl"):
        return LOG_DIR / name
    return DATA_DIR / name


def _validate_document_name(name: str) -> None:
    if Path(name).name != name or not name.endswith(".json"):
        raise ValueError("Invalid storage document name")


def _json_payload(value: Any, *, pretty: bool = False) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
    )


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = database_path()
    path_key = str(path.resolve())
    new_database = not path.exists()
    if new_database:
        _SCHEMA_READY.discard(path_key)
    connection = sqlite3.connect(path, timeout=30, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 30000")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA synchronous = FULL")
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if version > SCHEMA_VERSION:
        connection.close()
        raise RuntimeError(
            f"Cơ sở dữ liệu dùng schema mới hơn ({version}); phần mềm chỉ hỗ trợ {SCHEMA_VERSION}."
        )
    if path_key not in _SCHEMA_READY or version != SCHEMA_VERSION:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.executescript(
            """
        CREATE TABLE IF NOT EXISTS storage_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS documents (
            name TEXT PRIMARY KEY,
            payload TEXT NOT NULL CHECK (json_valid(payload)),
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            occurred_at TEXT NOT NULL,
            event TEXT NOT NULL,
            actor TEXT,
            ip TEXT,
            details TEXT NOT NULL CHECK (json_valid(details))
        );
        CREATE INDEX IF NOT EXISTS idx_audit_events_occurred_at
            ON audit_events(occurred_at);
        CREATE INDEX IF NOT EXISTS idx_audit_events_event
            ON audit_events(event);
        CREATE VIEW IF NOT EXISTS learning_records AS
            SELECT collections.key AS collection,
                   CAST(items.key AS INTEGER) AS position,
                   json_extract(items.value, '$.id') AS record_id,
                   items.value AS payload
            FROM documents AS document,
                 json_each(document.payload) AS collections,
                 json_each(collections.value) AS items
            WHERE document.name = 'learning.json'
              AND json_type(collections.value) = 'array';
        CREATE VIEW IF NOT EXISTS exam_problem_records AS
            SELECT json_extract(exams.value, '$.id') AS exam_id,
                   CAST(problems.key AS INTEGER) AS problem_index,
                   json_extract(problems.value, '$.title') AS title,
                   problems.value AS payload
            FROM documents AS document,
                 json_each(document.payload) AS exams,
                 json_each(exams.value, '$.programming.problems') AS problems
            WHERE document.name = 'exam_catalog.json';
        CREATE VIEW IF NOT EXISTS programming_submission_records AS
            SELECT CAST(items.key AS INTEGER) AS position,
                   json_extract(items.value, '$.id') AS submission_id,
                   json_extract(items.value, '$.student_id') AS student_id,
                   items.value AS payload
            FROM documents AS document,
                 json_each(document.payload) AS items
            WHERE document.name = 'programming_submissions.json';
        CREATE VIEW IF NOT EXISTS file_submission_records AS
            SELECT students.key AS student_id,
                   CAST(attempts.key AS INTEGER) AS attempt_index,
                   json_extract(attempts.value, '$.id') AS submission_id,
                   attempts.value AS payload
            FROM documents AS document,
                 json_each(document.payload) AS students,
                 json_each(students.value) AS attempts
            WHERE document.name = 'submissions.json';
            """
        )
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        _SCHEMA_READY.add(path_key)
    return connection


def _upsert_document(connection: sqlite3.Connection, name: str, value: Any) -> None:
    _validate_document_name(name)
    connection.execute(
        """INSERT INTO documents(name, payload, updated_at) VALUES (?, ?, ?)
           ON CONFLICT(name) DO UPDATE SET
               payload=excluded.payload, updated_at=excluded.updated_at""",
        (name, _json_payload(value), utc_now()),
    )


def _load_document(connection: sqlite3.Connection, name: str) -> Any | None:
    row = connection.execute("SELECT payload FROM documents WHERE name = ?", (name,)).fetchone()
    return None if row is None else json.loads(row["payload"])


def _recover() -> None:
    """Recover a journal left by the former JSON persistence implementation."""
    path = _journal_path()
    if not path.exists():
        return
    journal = json.loads(path.read_text(encoding="utf-8"))
    if journal.get("state") == "prepared":
        for name, previous in journal.get("before", {}).items():
            _validate_document_name(name)
            if previous["exists"]:
                atomic_write(_path(name), previous["value"])
            else:
                _path(name).unlink(missing_ok=True)
        audit_path = _path("audit.jsonl")
        if audit_path.exists():
            with audit_path.open("r+b") as output:
                output.truncate(journal.get("audit_offset", 0))
                output.flush()
                os.fsync(output.fileno())
    elif journal.get("state") != "committed":
        raise RuntimeError("Invalid legacy transaction journal state")
    path.unlink()


def _import_legacy_documents(connection: sqlite3.Connection) -> None:
    """Import each legacy JSON document once without overwriting SQLite data."""
    for path in sorted(DATA_DIR.glob("*.json")):
        if path.name.startswith("."):
            continue
        _validate_document_name(path.name)
        exists = connection.execute(
            "SELECT 1 FROM documents WHERE name = ?", (path.name,)
        ).fetchone()
        if exists:
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(
                f"Không thể nhập dữ liệu cũ {path.name} vào SQLite: {exc}"
            ) from exc
        _upsert_document(connection, path.name, value)
    connection.execute(
        """INSERT INTO storage_meta(key, value) VALUES ('legacy_json_imported_at', ?)
           ON CONFLICT(key) DO NOTHING""",
        (utc_now(),),
    )


def on_rollback(callback):
    batch = getattr(_LOCAL, "batch", None)
    if batch is not None:
        batch["rollback"].append(callback)


def after_commit(callback):
    batch = getattr(_LOCAL, "batch", None)
    if batch is None:
        callback()
    else:
        batch["commit"].append(callback)


def save_payload(path: Path, content: bytes):
    """Create a payload, flush it before metadata, and clean it on rollback."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        on_rollback(lambda: path.unlink(missing_ok=True))
        output.write(content)
        output.flush()
        os.fsync(output.fileno())


def _append_audit_records(records: list[dict]) -> int:
    path = _path("audit.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    offset = path.stat().st_size if path.exists() else 0
    if records:
        with path.open("a", encoding="utf-8", newline="\n") as output:
            for record in records:
                output.write(_json_payload(record) + "\n")
            output.flush()
            os.fsync(output.fileno())
    return offset


def _truncate_audit(offset: int) -> None:
    path = _path("audit.jsonl")
    if not path.exists():
        return
    with path.open("r+b") as output:
        output.truncate(offset)
        output.flush()
        os.fsync(output.fileno())


def _commit(batch) -> None:
    writes, records = batch["writes"], batch["audit"]
    if not writes and not records:
        return
    connection = _connect()
    audit_offset = None
    try:
        connection.execute("BEGIN IMMEDIATE")
        for name, value in writes.items():
            _upsert_document(connection, name, value)
        for record in records:
            connection.execute(
                """INSERT INTO audit_events(occurred_at,event,actor,ip,details)
                   VALUES (?,?,?,?,?)""",
                (
                    record["occurred_at"], record["event"], record["actor"],
                    record["ip"], _json_payload(record["details"]),
                ),
            )
        audit_offset = _append_audit_records(records)
        connection.commit()
        for name, value in writes.items():
            _CACHE[_cache_key(name)] = copy.deepcopy(value)
    except BaseException:
        connection.rollback()
        if audit_offset is not None:
            try:
                _truncate_audit(audit_offset)
            except OSError:
                logger.exception("Could not roll back the compatibility audit log")
        raise
    finally:
        connection.close()


@contextmanager
def atomic_transaction():
    """Commit all staged documents and audit events in one SQLite transaction."""
    callbacks = []
    with _LOCK:
        existing = getattr(_LOCAL, "batch", None)
        if existing is not None:
            try:
                yield
            except BaseException:
                existing["failed"] = True
                raise
            return
        batch = {"writes": {}, "audit": [], "rollback": [], "commit": [], "failed": False}
        _LOCAL.batch = batch
        try:
            yield
            if batch["failed"]:
                raise RuntimeError("A nested storage operation failed")
            _commit(batch)
            callbacks = batch["commit"]
        except BaseException:
            for callback in reversed(batch["rollback"]):
                try:
                    callback()
                except Exception:
                    logger.exception("Could not clean a newly staged file")
            raise
        finally:
            del _LOCAL.batch
    for callback in callbacks:
        try:
            callback()
        except Exception:
            logger.exception("Post-commit task failed; persisted work can be resumed")


def mutation(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        from .learning import LOCK
        with LOCK, atomic_transaction():
            return function(*args, **kwargs)
    return wrapped


@contextmanager
def transaction():
    """Keep a read/modify/write operation atomic across request threads."""
    with _LOCK:
        yield


DEFAULTS = {
    "students.json": {},
    "admins.json": {},
    "settings.json": {
        "exam_duration_minutes": 90,
        "submission_policy": "configurable",
        "max_submissions": 1,
        "accepted_submission_extensions": [".zip"],
        "overwrite_previous": True,
        "exam_password_enabled": False,
        "exam_password_hash": None,
        "distribution_mode": "random",
        "distribution_config": {},
        "exam_released": False,
        "exam_state": "idle",
        "exam_release_id": None,
        "exam_release_at": None,
        "exam_participants": [],
        "max_upload_bytes": 52428800,
        "allow_late_submission": False,
    },
    "assignments.json": {},
    "submissions.json": {},
    "sessions.json": {},
    "login_attempts.json": {},
    "machines.json": {},
    "notifications.json": [],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def initialize() -> None:
    """Create the database and atomically import any existing JSON data."""
    with _LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        active_database = str(database_path().resolve())
        for key in [key for key in _CACHE if key[0] == active_database]:
            _CACHE.pop(key, None)
        _recover()
        connection = _connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            _import_legacy_documents(connection)
            for name, default in DEFAULTS.items():
                current = _load_document(connection, name)
                if current is None:
                    _upsert_document(connection, name, copy.deepcopy(default))
                elif name == "settings.json":
                    missing = {key: value for key, value in default.items() if key not in current}
                    if "exam_state" not in current:
                        current["exam_state"] = "started" if current.get("exam_released") else "idle"
                        missing.pop("exam_state", None)
                    if missing:
                        current.update(copy.deepcopy(missing))
                        _upsert_document(connection, name, current)
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()
        (LOG_DIR / "audit.jsonl").touch(exist_ok=True)


def atomic_write(path: Path, value: Any) -> None:
    """Write a JSON export atomically (used by backups and legacy recovery)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _json_payload(value, pretty=True)
    handle, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    tmp = Path(name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        os.replace(tmp, path)
        if os.name != "nt":
            directory = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        tmp.unlink(missing_ok=True)


def document_names() -> list[str]:
    """List canonical SQLite documents for backup and diagnostics."""
    with _LOCK:
        connection = _connect()
        try:
            return [row["name"] for row in connection.execute(
                "SELECT name FROM documents ORDER BY name"
            )]
        finally:
            connection.close()


def document_exists(name: str) -> bool:
    _validate_document_name(name)
    with _LOCK:
        connection = _connect()
        try:
            return connection.execute(
                "SELECT 1 FROM documents WHERE name = ?", (name,)
            ).fetchone() is not None
        finally:
            connection.close()


def document_signature(names: tuple[str, ...] | list[str]) -> tuple:
    """Return a cheap change token for canonical documents."""
    for name in names:
        _validate_document_name(name)
    with _LOCK:
        connection = _connect()
        try:
            rows = {
                row["name"]: row["updated_at"]
                for row in connection.execute(
                    "SELECT name, updated_at FROM documents WHERE name IN (%s)"
                    % ",".join("?" for _ in names),
                    tuple(names),
                )
            } if names else {}
            return (str(database_path().resolve()), tuple(rows.get(name) for name in names))
        finally:
            connection.close()


def read_json(name: str, default: Any = None) -> Any:
    _validate_document_name(name)
    with _LOCK:
        batch = getattr(_LOCAL, "batch", None)
        if batch is not None and name in batch["writes"]:
            return copy.deepcopy(batch["writes"][name])
        key = _cache_key(name)
        if key in _CACHE:
            return copy.deepcopy(_CACHE[key])
        connection = _connect()
        try:
            value = _load_document(connection, name)
            if value is None:
                # Supports restored environments and documents created by older tools.
                legacy = _path(name)
                if legacy.exists():
                    try:
                        value = json.loads(legacy.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError) as exc:
                        raise RuntimeError(
                            f"Không thể đọc {legacy.name}; không ghi đè dữ liệu lỗi: {exc}"
                        ) from exc
                    connection.execute("BEGIN IMMEDIATE")
                    _upsert_document(connection, name, value)
                    connection.commit()
                elif default is not None:
                    value = copy.deepcopy(default)
                else:
                    value = copy.deepcopy(DEFAULTS.get(name, {}))
            _CACHE[key] = copy.deepcopy(value)
            return copy.deepcopy(value)
        finally:
            connection.close()


def write_json(name: str, value: Any) -> None:
    _validate_document_name(name)
    with _LOCK:
        batch = getattr(_LOCAL, "batch", None)
        if batch is not None:
            batch["writes"][name] = copy.deepcopy(value)
            return
        connection = _connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            _upsert_document(connection, name, value)
            connection.commit()
            _CACHE[_cache_key(name)] = copy.deepcopy(value)
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()


def delete_document(name: str) -> None:
    """Delete one canonical document; primarily useful for reset/test tooling."""
    _validate_document_name(name)
    with _LOCK:
        connection = _connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM documents WHERE name = ?", (name,))
            connection.commit()
            _CACHE.pop(_cache_key(name), None)
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()


def update_json(name: str, mutator):
    with _LOCK:
        value = read_json(name)
        result = mutator(value)
        write_json(name, value)
        return result


def audit(event: str, actor: str | None, ip: str | None, details: dict | None = None) -> None:
    record = {
        "occurred_at": utc_now(),
        "event": event,
        "actor": actor,
        "ip": ip,
        "details": details or {},
    }
    with _LOCK:
        batch = getattr(_LOCAL, "batch", None)
        if batch is not None:
            batch["audit"].append(record)
            return
        _commit({"writes": {}, "audit": [record]})
