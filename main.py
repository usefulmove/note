#!/usr/bin/env python3
import sys
from datetime import datetime
import duckdb
from importlib import metadata


def main():
    current_datetime = datetime.now()


    ## version
    if sys.argv[1] in ('--version'):
        print(f'note {metadata.version("note")}')
        return


    ## connect to notes database (or create if it doesn't exist)
    con = duckdb.connect('~/.notes.db')


    ## create schema and notes table
    con.execute('create schema if not exists coda;')
    con.execute('set schema = coda;')
    con.execute("""
        create table if not exists notes (
            date timestamp,
            message varchar
        );
    """)


    ## list notes
    if sys.argv[1] in ('-l', '-ls', '-list', '--list'):
        # read database contents and write out to console
        db_entries = con.execute("select date, message from notes;").fetchall()

        for i, e in enumerate(db_entries):
            print(f'  {e[0].strftime("%y.%m.%d %H:%M")} | {i + 1} | {e[1]}')

        con.close()
        return


    ## clear notes
    if sys.argv[1] in ('--clear', '--reset'):
        # clear database
        con.execute('delete from notes;')

        con.close()
        return


    notes = sys.argv[1:]


    for note in notes:
        print(f'  {current_datetime.strftime("%y.%m.%d %H:%M")} | {note}')



    ## load notes into database
    for note in notes:
        con.execute(f"""
            insert into coda.notes
                (date, message)
            values
                (cast('{current_datetime}' as timestamp), '{note}');
        """)


    con.close() # close database connection



if __name__ == "__main__":
    main()
