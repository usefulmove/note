from datetime import datetime
import duckdb
import re
from typing import NamedTuple
from . import console_output as cons


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


## module methods ##

def get_connection() -> duckdb.DuckDBPyConnection:
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


def get_notes(nids: list[str] = []) -> list[Note]:
    if not nids:
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
        query_insert: str = ', '.join('?' for _ in nids)

        try:
            ids: list[int] = list(map(int, nids))
        except ValueError:
            cons.send_error('improper input. could not convert note identifier.')
            return []

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
        if not nids:
            entries = con.execute(query).fetchall()
        else:
            entries = con.execute(query, ids).fetchall()

    # covert each tuple into a Note object
    notes: list[Note] = [Note(*row) for row in entries]

    return notes


def delete_entries(nids: list[str]) -> None:
    # delete selected database entries
    with get_connection() as con:
        for nid in nids:
            query = f"""
                delete from {TABLE}
                where {NID_COLUMN} = ?;
            """
            con.execute(query, [int(nid)])


def clear_database() -> None:
    # clear database
    with get_connection() as con:
        con.execute(f'delete from {TABLE};')


def get_note_matches(match: str) -> list[Note]:
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


def update_entry(nid: str, message: str) -> None:
    query = f"""
        update
            {TABLE}
        set
            {MESSAGE_COLUMN} = ?
        where
            {NID_COLUMN} = ?;
    """

    with get_connection() as con:
        con.execute(query, [message, int(nid)])


def rebase() -> None:
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


def add_entries(entries: list[str]) -> None:
    with get_connection() as con:
        for message in entries:
            query = f"""
                insert into {SCHEMA}.{TABLE}
                    ({NID_COLUMN}, {TIMESTAMP_COLUMN}, {MESSAGE_COLUMN})
                values (
                    (select max({NID_COLUMN}) from {TABLE}) + 1,
                    cast('{datetime.now()}' as timestamp),
                    ?
                );
            """
            con.execute(query, [message])
