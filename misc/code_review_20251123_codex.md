# Code Review (2025-11-23 Codex)

Scope: project structure best practices and targeted review of `src/note/`.

## Strengths
- Clear src-layout with a single entrypoint (`pyproject.toml` script) and minimal dependencies.
- CLI, DB access, and console formatting are separated into dedicated modules.

## Key Issues & Risks
- `PRODUCTION` is a constant toggle (`src/note/notedb.py:23-38`), so tests require code edits and the default DB writes to the user home dir; expose a config/env override and default to an app data dir to avoid polluting `~/`.
- Database table lacks a primary key/uniqueness and manual ID generation uses `max(nid)+1` (`src/note/notedb.py:62-67,277-285`), leaving room for duplicate IDs on concurrent writes and inconsistent ordering after deletes/rebases; use an identity/sequence column with `PRIMARY KEY` plus an index on `nid`.
- CLI errors only print but always exit 0 and have no usage/help (`src/note/main.py:13-28`); adopt `argparse`/`typer` to enforce required args, return non-zero exit codes, and provide `--help/--version`.
- Mutable default and inefficient queries: `get_notes(ids=[])` uses a mutable default (`src/note/notedb.py:72`); `is_valid` loads all IDs (`src/note/notedb.py:318`) and `delete_notes` issues one DELETE per ID (`src/note/notedb.py:137-147`), leading to O(n²) behavior when validating/deleting many notes; use `ids=None`, a targeted `count(*)` check, and a bulk `WHERE nid IN (...)` delete.
- Add confirmation can report the wrong notes when messages repeat because it re-queries by text and slices sorted results (`src/note/commands.py:34-52`); return inserted rows via `INSERT … RETURNING` or pull by generated IDs.
- Update/append assume the note still exists after validation (`src/note/commands.py:168-225`), so a concurrent delete would raise; guard on `get_notes` returning data and emit a failure instead of indexing `[0]`.
- Type hints and command wiring are misleading: `Command.check` is typed as returning `None` and `Command.ids` is declared as a list but receives a bare string for the short-list command (`src/note/commands.py:14-22,91-95`); tighten types and use tuples/lists consistently to avoid silent iteration surprises.
- No automated tests or linting; the `test/` folder only ships DB fixtures. Add unit tests for DB operations, integration tests for CLI commands, and simple formatting/lint (ruff/black) to catch regressions.

## Recommended Next Steps
- Introduce configuration (env vars or CLI flags) for DB path, mode (prod/test), and optionally schema/table names; use OS-specific data dirs for defaults.
- Refactor command parsing around a real parser to consolidate validation, emit structured help/errors, and centralize exit codes.
- Strengthen the schema (PK, not-null constraints, identity column, indexes) and consolidate DB operations to single statements to improve correctness and performance.
- Add test coverage for add/list/search/update/delete flows and basic output formatting, plus CI to run them.***
