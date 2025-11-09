#!/usr/bin/env python3
import sys
from datetime import datetime
import duckdb
from importlib import metadata


def main():
    current_datetime = datetime.now()


    ## version
    if sys.argv[1] in ('-version', '--version'):
        print(f'note {metadata.version("note")}')
        return


    SCHEMA = 'coredb'
    TABLE = 'notes'
    NID_COLUMN = 'nid'
    TIMESTAMP_COLUMN = 'date'
    MESSAGE_COLUMN = 'message'


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


    ## list notes
    if sys.argv[1] in ('-l', '-ls', '-list', '--list'):
        # read database contents and write out to console
        db_entries = con.execute(f"""
            select
                {NID_COLUMN},
                {TIMESTAMP_COLUMN},
                {MESSAGE_COLUMN}
            from
                {TABLE}
            order by
                1, 2;
        """).fetchall()

        print('')
        for e in db_entries:
            print(f'  {e[1].strftime("%y.%m.%d %H:%M")} | {e[0]} | {e[2]}')
        print('')

        con.close()
        return


    ## clear notes
    if sys.argv[1] in ('-clear', '--clear', '-reset', '--reset'):
        # clear database
        con.execute(f'delete from {TABLE};')

        con.close()
        return


    ## delete note(s)
    if sys.argv[1] in ('-d', '-delete', '--delete'):
        # delete database entry
        nids = sys.argv[2:]

        for nid in nids:
            con.execute(f"""
                delete from {TABLE}
                where {NID_COLUMN} = {nid};
            """)

        con.close()
        return


    ## search
    if sys.argv[1] in ('-s', '-search', '--search', '-f', '-find', '--find'):
        # search database and output results
        match = sys.argv[2]

        search_results = con.execute(f"""
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
        """).fetchall()

        print('')
        for e in search_results:
            print(f'  {e[1].strftime("%y.%m.%d %H:%M")} | {e[0]} | {e[2]}')
        print('')

        con.close()
        return
        

    ## add notes
    notes = sys.argv[1:]

    # load notes into database
    for note in notes:
        con.execute(f"""
            insert into {SCHEMA}.{TABLE}
                ({NID_COLUMN}, {TIMESTAMP_COLUMN}, {MESSAGE_COLUMN})
            values (
                (select max({NID_COLUMN}) from {TABLE}) + 1,
                cast('{current_datetime}' as timestamp),
                '{note}'
            );
        """)

    # display output message
    print('')
    for note in notes:
        print(f'  {current_datetime.strftime("%y.%m.%d %H:%M")} | {note} | ( added )')
    print('')


    con.close() # close database connection



if __name__ == "__main__":
    main()
