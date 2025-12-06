from pathlib import Path
from datetime import datetime
import duckdb
from typing import NamedTuple


__all__ = [
    'Note',
    'create_notes',
    'is_valid',
    'get_notes',
    'get_note_matches',
    'get_note_unmatches',
    'get_tag_matches',
    'get_tag_unmatches',
    'update_note',
    'rebase',
    'delete_notes',
    'clear_database',
    'set_path',
]


class Note(NamedTuple):
    '''note interface objects'''
    id: int
    date: datetime
    message: str

    def __repr__(self) -> str:
        return f'Note({self.id!r}, {self.date!r}, {self.message!r})'


class DatabaseCorrupted(Exception):
    '''Database corrupted exception'''
    pass


## database schema ##
SCHEMA = 'coredb'
TABLE = 'notes'
NID_COLUMN = 'nid'
TIMESTAMP_COLUMN = 'date'
MESSAGE_COLUMN = 'message'


## database path ##
db_path: str = '~/.notes.db'

def set_path(path: str) -> bool:
    global db_path

    if not Path(path).parent.exists():
        return False

    db_path = path

    return True


## module functions ##

def get_connection() -> duckdb.DuckDBPyConnection:
    '''Return the note database connection.'''

    # connect to database (or create if it doesn't exist)
    con = duckdb.connect(Path(db_path).expanduser())

    # create schema and notes table
    con.execute(f'create schema if not exists {SCHEMA};')
    con.execute(f'set schema = {SCHEMA};')
    con.execute('create sequence if not exists nid_sequence start 1;')
    con.execute(f"""
        create table if not exists {TABLE} (
            {NID_COLUMN} integer primary key default nextval('nid_sequence'),
            {TIMESTAMP_COLUMN} timestamp,
            {MESSAGE_COLUMN} varchar
        );
    """)

    return con


def get_notes(ids: tuple[int, ...] = ()) -> list[Note]:
    '''Return identified notes. Return all if none identified.'''

    rows: list[tuple[int, datetime, str]]

    with get_connection() as con:
        if not ids:
            # retrieve all notes
            query = f"""
            select
                {NID_COLUMN},
                {TIMESTAMP_COLUMN},
                {MESSAGE_COLUMN}
            from
                {TABLE}
            order by
                1, 2;
            """

            rows = con.execute(query).fetchall()
        else:
            query_insert: str = ', '.join('?' for _ in ids)

            # retrieve selected nids
            query = f"""
            select
                {NID_COLUMN},
                {TIMESTAMP_COLUMN},
                {MESSAGE_COLUMN}
            from
                {TABLE}
            where
                {NID_COLUMN} in ({query_insert})
            order by
                1, 2;
            """

            rows = con.execute(query, ids).fetchall()

    # covert each tuple into a Note
    notes: list[Note] = [Note(*row) for row in rows]

    return notes


def delete_notes(ids: tuple[int, ...]) -> list[Note]:
    '''Delete identified notes.'''

    rows: list[tuple[int, datetime, str]]

    query_insert: str = ', '.join('?' for _ in ids)

    query = f"""
    delete from {TABLE}
    where {NID_COLUMN} in ({query_insert})
    returning *;
    """

    with get_connection() as con:
        rows = con.execute(query, ids).fetchall()

    # covert each tuple into a Note
    notes: list[Note] = [Note(*row) for row in rows]

    return notes


def clear_database() -> None:
    '''Delete all notes from note database.'''

    with get_connection() as con:
        con.execute(f'delete from {TABLE};')


def get_note_matches(match: str) -> list[Note]:
    '''Return all notes that have text matching input.'''

    query = f"""
    select
        {NID_COLUMN},
        {TIMESTAMP_COLUMN},
        {MESSAGE_COLUMN}
    from
        {TABLE}
    where
        {MESSAGE_COLUMN} ilike ?
    order by
        1, 2;
    """

    with get_connection() as con:
        matches = con.execute(query, ['%' + match + '%']).fetchall()

    # covert each tuple into a Note
    notes: list[Note] = [Note(*row) for row in matches]

    return notes


def get_note_unmatches(unmatch: str) -> list[Note]:
    '''Return all notes that do not have text matching input.'''

    query = f"""
    select
        {NID_COLUMN},
        {TIMESTAMP_COLUMN},
        {MESSAGE_COLUMN}
    from
        {TABLE}
    where
        {MESSAGE_COLUMN} not ilike ?
    order by
        1, 2;
    """

    with get_connection() as con:
        unmatches = con.execute(query, ['%' + unmatch + '%']).fetchall()

    # covert each tuple into a Note
    notes: list[Note] = [Note(*row) for row in unmatches]

    return notes


def get_tag_matches(tag: str) -> list[Note]:
    '''Return all notes that have tags matching input.'''

    query = f"""
    select
        {NID_COLUMN},
        {TIMESTAMP_COLUMN},
        {MESSAGE_COLUMN}
    from
        {TABLE}
    where
        {MESSAGE_COLUMN} ilike ?
    order by
        1, 2;
    """

    with get_connection() as con:
        matches = con.execute(query, ['%:' + tag + ':%']).fetchall()

    # covert each tuple into a Note
    notes: list[Note] = [Note(*row) for row in matches]

    return notes


def get_tag_unmatches(tag: str) -> list[Note]:
    '''Return all notes that do not have tags matching input.'''

    query = f"""
    select
        {NID_COLUMN},
        {TIMESTAMP_COLUMN},
        {MESSAGE_COLUMN}
    from
        {TABLE}
    where
        {MESSAGE_COLUMN} not ilike ?
    order by
        1, 2;
    """

    with get_connection() as con:
        unmatches = con.execute(query, ['%:' + tag + ':%']).fetchall()

    # covert each tuple into a Note
    notes: list[Note] = [Note(*row) for row in unmatches]

    return notes


def update_note(id: int, message: str) -> None:
    '''Replace note text of identified note with provided input.'''

    query = f"""
    update
        {TABLE}
    set
        {MESSAGE_COLUMN} = ?
    where
        {NID_COLUMN} = ?;
    """

    with get_connection() as con:
        con.execute(query, [message, id])


def create_notes(entries: tuple[str, ...]) -> list[Note]:
    '''Add notes to database using note text inputs.'''

    rows: list[tuple[int, datetime, str]] = []

    with get_connection() as con:
        con.begin()
        for message in entries:
            query = f"""
            insert into {TABLE}
                ({TIMESTAMP_COLUMN}, {MESSAGE_COLUMN})
            values
                (cast('{datetime.now()}' as timestamp), ?)
            returning *;
            """
            rows += con.execute(query, [message]).fetchall()
        con.commit()

    # covert each tuple into a Note
    notes: list[Note] = [Note(*row) for row in rows]

    return notes


def rebase() -> None:
    '''Rebase note identifiers starting at 1.'''

    query = f"""
    with n{NID_COLUMN} as (
            select
                row_number() over(order by {NID_COLUMN})
                    as updated_{NID_COLUMN},
                {NID_COLUMN},
                {TIMESTAMP_COLUMN},
                {MESSAGE_COLUMN}
            from
                {TABLE}
    )

    update
        {TABLE} n
    set
        {NID_COLUMN} = nn.updated_{NID_COLUMN}
    from
        n{NID_COLUMN} nn
    where
        n.{NID_COLUMN} = nn.{NID_COLUMN};
    """

    with get_connection() as con:
        con.begin()

        con.execute(query) # rebase nids

        # retrieve next nid in sequence
        resp = con.execute(f'select coalesce(max({NID_COLUMN}), 0) + 1 from {TABLE}').fetchone()
        if resp is None:
            # should never happen due do COALESCE, but required by type checker
            raise DatabaseCorrupted("Failed to retrieve max NID from database")
        nid_next = resp[0]

        con.execute(f'create or replace sequence nid_sequence start {nid_next}') # reset sequence

        con.commit()


def is_valid(id: int) -> bool:
    '''Return whether argument is a valid note identifier.'''

    query = f"""
    select
        count(*)
    from
        {TABLE}
    where
        {NID_COLUMN} = ?;
    """

    with get_connection() as con:
        count, *_ = con.execute(query, [id]).fetchall()[0]

    return count > 0
