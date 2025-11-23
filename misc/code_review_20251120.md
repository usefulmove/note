# Code Review Feedback

## Key Findings
- `src/note/main.py` indexes `sys.argv[2]` / `sys.argv[3]` without arity checks across multiple commands (search, tag, update, append, add, delete); running with too few args raises `IndexError` instead of showing a friendly message.
- `src/note/main.py` assumes `db.get_notes([...])[0]` exists for update/append; unknown ids crash and the DB update still runs with bad input.
- `src/note/notedb.py` uses `DB_PATH = '~/'; DB_FILENAME = '.notes.db'` without `expanduser`, so DuckDB opens a literal `~/` path instead of the user’s home directory.
- `src/note/notedb.py` inserts with `(select max(nid) from notes) + 1`; on an empty table `max` is `NULL`, producing a `NULL` nid and an insert failure.
- `src/note/notedb.py` converts ids to `int` inside delete/update loops; a single bad id raises and aborts the whole operation without a user-facing error. The mutable default `get_notes(nids: list[str] = [])` is also a Python footgun.
- `src/note/console_output.py` tag dimming regex `r":([a-z]*):"` ignores digits/uppercase, so tags like `:TODO:` or `:v2:` are missed (ok if intentional).

## Proposed Improvements
- Add argument validation per command (len checks, required ids/messages) and surface failures via `cons.send_error` instead of tracebacks.
>   :0.3.4:
- Consider a thin argparse layer to centralize help/usage.
>   (rejected)
- Guard note lookups: if `get_notes([...])` returns empty, emit “id not found” and skip updates/appends/deletes.
>   :0.3.4:
- Normalize DB path creation with `pathlib.Path`/`os.path.expanduser` and make the target path configurable via env or CLI flag rather than the hard-coded `PRODUCTION` boolean.
- Fix insertion to `coalesce(max(nid), 0) + 1` (or use DuckDB sequences) so adding the first note works.
>   :0.3.4:
- Pre-parse id lists once with validation; reject/ignore non-integers with an error message instead of raising. Change mutable defaults to `None` and initialize inside functions.
>   :0.3.4:
- Broaden the tag-highlighting regex to include digits/uppercase if you want those tags to render consistently.
>   :0.3.3:
- Add lightweight tests for the CLI paths (arg validation), DB helpers (empty-table insert, rebase), and console formatting; run under a tmp duckdb file to avoid mutating real notes.
