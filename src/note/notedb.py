from datetime import datetime
import duckdb
import re


## database schema
SCHEMA = 'coredb'
TABLE = 'notes'
NID_COLUMN = 'nid'
TIMESTAMP_COLUMN = 'date'
MESSAGE_COLUMN = 'message'


def get_connection() -> duckdb.DuckDBPyConnection:
    # connect to database (or create if it doesn't exist)
    con = duckdb.connect('~/.notes.db')

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


def get_notes(nids: list[str] = []) -> list[tuple[int, datetime, str]]:
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
        # retrieve selected nids
        query = f"""
            select
                {NID_COLUMN},
                {TIMESTAMP_COLUMN},
                {MESSAGE_COLUMN}
            from
                {TABLE}
            where
                {NID_COLUMN} in ({re.sub(r'[\[\]]', '', str(nids))})
            order by
                1, 2;
        """

    with get_connection() as con:
        entries = con.execute(query).fetchall()

    return entries


def delete_entries(nids: list[str]) -> None:
    # delete selected database entries
    with get_connection() as con:
        for nid in nids:
            query = f"""
                delete from {TABLE}
                where {NID_COLUMN} = {nid};
            """
            con.execute(query)


def clear_database() -> None:
    # clear database
    with get_connection() as con:
        con.execute(f'delete from {TABLE};')


def get_note_matches(match: str) -> list[tuple[int, datetime, str]]:
    query = f"""
        select
            {NID_COLUMN},
            {TIMESTAMP_COLUMN},
            {MESSAGE_COLUMN}
        from
            {TABLE}
        where
            {MESSAGE_COLUMN} ilike '%{match}%'
        order by
            1, 2;
    """

    with get_connection() as con:
        matches = con.execute(query).fetchall()

    return matches


def get_note_unmatches(unmatch: str) -> list[tuple[int, datetime, str]]:
    query = f"""
        select
            {NID_COLUMN},
            {TIMESTAMP_COLUMN},
            {MESSAGE_COLUMN}
        from
            {TABLE}
        where
            {MESSAGE_COLUMN} not ilike '%{unmatch}%'
        order by
            1, 2;
    """

    with get_connection() as con:
        unmatches = con.execute(query).fetchall()

    return unmatches


def get_tag_matches(tag: str) -> list[tuple[int, datetime, str]]:
    query = f"""
        select
            {NID_COLUMN},
            {TIMESTAMP_COLUMN},
            {MESSAGE_COLUMN}
        from
            {TABLE}
        where
            {MESSAGE_COLUMN} ilike '%:{tag}:%'
        order by
            1, 2;
    """

    with get_connection() as con:
        matches = con.execute(query).fetchall()

    return matches


def get_tag_unmatches(tag: str) -> list[tuple[int, datetime, str]]:
    query = f"""
        select
            {NID_COLUMN},
            {TIMESTAMP_COLUMN},
            {MESSAGE_COLUMN}
        from
            {TABLE}
        where
            {MESSAGE_COLUMN} not ilike '%:{tag}:%'
        order by
            1, 2;
    """

    with get_connection() as con:
        unmatches = con.execute(query).fetchall()

    return unmatches


def update_entry(nid: str, message: str) -> None:
    query = f"""
        update
            {TABLE}
        set
            {MESSAGE_COLUMN} = '{message}'
        where
            {NID_COLUMN} = {nid};
    """

    with get_connection() as con:
        con.execute(query)


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
        for msg in entries:
            query = f"""
                insert into {SCHEMA}.{TABLE}
                    ({NID_COLUMN}, {TIMESTAMP_COLUMN}, {MESSAGE_COLUMN})
                values (
                    (select max({NID_COLUMN}) from {TABLE}) + 1,
                    cast('{datetime.now()}' as timestamp),
                    '{msg}'
                );
            """
            con.execute(query)
