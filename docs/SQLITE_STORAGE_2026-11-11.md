# SQLite storage migration

The runtime metadata store is `data/lms.sqlite3`. Python's standard `sqlite3`
module is sufficient; no database server or extra package is required.

## Automatic upgrade

On startup, `app.storage.initialize()` creates the schema and imports every
existing `data/*.json` document that is not already present in SQLite. The
import and default-setting updates run in one transaction. Existing JSON files
are retained as a rollback reference, but they are not read again once the
same logical document exists in SQLite.

The application keeps the existing `read_json`/`write_json` service interface,
so accounts, courses, schedules, attendance, question/exam configuration and
submissions all use the new store without changing their HTTP contracts.

## Durability and concurrency

- WAL journal mode and `synchronous=FULL` are enabled.
- Multi-document writes use `BEGIN IMMEDIATE` and commit atomically.
- Audit events are stored in `audit_events`; `logs/audit.jsonl` remains a
  compatibility copy.
- Read-only views `learning_records`, `exam_problem_records`,
  `programming_submission_records` and `file_submission_records` expose common
  schedules, attendance, questions and submissions for direct SQL queries.
- The existing process lock and data-directory lease still enforce one server
  process per runtime directory.
- Uploaded payloads remain separate files and are flushed before their SQLite
  metadata is committed.

## Backup and restore

`python -m app.maintenance backup` exports the canonical SQLite documents as
JSON inside the verified backup. This keeps backups inspectable and allows a
restored directory to be imported automatically into a fresh SQLite database.
The manifest still verifies every metadata and payload file with SHA-256.

Do not edit `lms.sqlite3` while the server is running. Stop the server before
maintenance commands or manual inspection.
