from datetime import datetime
import duckdb
import re
from typing import NamedTuple


PRODUCTION = True


class Note(NamedTuple):
    id: int
    date: datetime
    message: str


## notes database ##
if PRODUCTION:
    DB_FILENAME = '.notes.db'
    DB_PATH = '~/'
else:
    DB_FILENAME = 'notes.db'
    DB_PATH = './test/'


## database schema ##

SCHEMA = 'coredb'
TABLE = 'notes'
NID_COLUMN = 'nid'
TIMESTAMP_COLUMN = 'date'
MESSAGE_COLUMN = 'message'


## module functions ##

def get_connection() -> duckdb.DuckDBPyConnection:
    '''Return the note database connection.'''

    # connect to database (or create if it doesn't exist)
    con = duckdb.connect(DB_PATH + DB_FILENAME)

    # create schema and notes table
    con.execute(f'create schema if not exists {SCHEMA};')
    con.execute(f'set schema = {SCHEMA};')
    con.execute(f"""
        create table if not exists {TABLE} (
            {NID_COLUMN} integer,
            {TIMESTAMP_COLUMN} timestamp,
            {MESSAGE_COLUMN} varchar
        );
    """)

    return con


def get_notes(ids: list[int] = []) -> list[Note]:
    '''Return identified notes. Return all if none identified.'''

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

    with get_connection() as con:
        if not ids:
            entries = con.execute(query).fetchall()
        else:
            entries = con.execute(query, ids).fetchall()

    # covert each tuple into a Note object
    notes: list[Note] = [Note(*row) for row in entries]

    return notes


def get_nids() -> list[int]:
    '''Return all note identifiers.'''

    query = f"""
        select
            {NID_COLUMN}
        from
            {TABLE}
        order by
            1;
    """

    with get_connection() as con:
        entries = con.execute(query).fetchall()

    # covert
    ids: list[int] = [int(tup[0]) for tup in entries]

    return ids


def delete_notes(ids: list[int]) -> None:
    '''Delete identified notes.'''

    with get_connection() as con:
        for id in ids:
            query = f"""
                delete from {TABLE}
                where {NID_COLUMN} = ?;
            """
            con.execute(query, [id])


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

    # covert each tuple into a Note object
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

    # covert each tuple into a Note object
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

    # covert each tuple into a Note object
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

    # covert each tuple into a Note object
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


def create_notes(entries: list[str]) -> None:
    '''Add notes to database using note text inputs (list[str]).'''

    with get_connection() as con:
        for message in entries:
            query = f"""
                insert into {SCHEMA}.{TABLE}
                    ({NID_COLUMN}, {TIMESTAMP_COLUMN}, {MESSAGE_COLUMN})
                values (
                    (select coalesce(max({NID_COLUMN}), 0) + 1 from {TABLE}),
                    cast('{datetime.now()}' as timestamp),
                    ?
                );
            """
            con.execute(query, [message])


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
        con.execute(query)


def is_valid(id: int) -> bool:
    return id in get_nids()
