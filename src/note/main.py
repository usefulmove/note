#!/usr/bin/env python3
import sys
from datetime import datetime
import duckdb
from importlib import metadata


def main():
    current_datetime = datetime.now()


    ## no args - list notes
    if len(sys.argv) == 1:
        sys.argv += ['-list']


    ## version
    if sys.argv[1] in ('-version', '--version'):
        print(f'  note {metadata.version("note")}')
        return


    SCHEMA = 'coredb'
    TABLE = 'notes'
    NID_COLUMN = 'nid'
    TIMESTAMP_COLUMN = 'date'
    MESSAGE_COLUMN = 'message'


    def get_db_connection() -> duckdb.DuckDBPyConnection:
        ## connect to notes database (or create if it doesn't exist)
        con = duckdb.connect('~/.notes.db')

        ## create schema and notes table
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


    ## list notes
    if sys.argv[1] in ('-l', '-ls', '-list', '--list'):
        # read database contents and write out to console
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

        with get_db_connection() as con:
            db_entries = con.execute(query).fetchall()

        print('')
        for e in db_entries:
            print(f'  {e[1].strftime("%y.%m.%d %H:%M")} | {e[0]} | {e[2]}')
        print('')

        return


    ## clear notes
    if sys.argv[1] in ('-clear', '--clear', '-reset', '--reset'):
        # clear database
        with get_db_connection as con:
            con.execute(f'delete from {TABLE};')

        return


    ## delete note(s)
    if sys.argv[1] in ('-d', '-delete', '--delete', '-rm'):
        # delete selected database entries
        nids = sys.argv[2:]

        with get_db_connection() as con:
            for nid in nids:
                query = f"""
                    delete from {TABLE}
                    where {NID_COLUMN} = {nid};
                """
                con.execute(query)

        return


    ## search (general)
    if sys.argv[1] in ('-s', '-search', '--search', '-f', '-fd', '-find', '--find', '-filter', '--filter'):
        # search database and output results
        match = sys.argv[2]

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

        with get_db_connection() as con:
            search_results = con.execute(query).fetchall()

        print('')
        for e in search_results:
            print(f'  {e[1].strftime("%y.%m.%d %H:%M")} | {e[0]} | {e[2]}')
        print('')

        return
        

    ## tag search
    if sys.argv[1] in ('-t', '-tag', '--tag'):
        # search database for tags and output results
        tag = sys.argv[2]

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

        with get_db_connection() as con:
            search_results = con.execute(query).fetchall()

        print('')
        for e in search_results:
            print(f'  {e[1].strftime("%y.%m.%d %H:%M")} | {e[0]} | {e[2]}')
        print('')

        return


    ## update note
    if sys.argv[1] in ('-u', '-update', '--update'):
        nid = sys.argv[2]
        msg = sys.argv[3]

        query = f"""
            update
                {TABLE}
            set
                {MESSAGE_COLUMN} = '{msg}'
            where
                {NID_COLUMN} = {nid};
        """

        with get_db_connection() as con:
            con.execute(query)

        return


    ## rebase notes
    if sys.argv[1] in ('-rebase', '--rebase'):
        # update database nids
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

        with get_db_connection() as con:
            con.execute(query)

        return


    ## check for unknown option
    if sys.argv[1].startswith('-'):
        print(f'  note: unknown option ({sys.argv[1]})')
        return


    ## otherwise add notes
    notes = sys.argv[1:]

    # load notes into database
    with get_db_connection() as con:
        for note in notes:
            query = f"""
                insert into {SCHEMA}.{TABLE}
                    ({NID_COLUMN}, {TIMESTAMP_COLUMN}, {MESSAGE_COLUMN})
                values (
                    (select max({NID_COLUMN}) from {TABLE}) + 1,
                    cast('{current_datetime}' as timestamp),
                    '{note}'
                );
            """
            con.execute(query)

    # display output message
    print('')
    for note in notes:
        print(f'  {current_datetime.strftime("%H:%M")} | {note} | ( added )')
    print('')




if __name__ == "__main__":
    main()
