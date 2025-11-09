#!/usr/bin/env python3
import sys
from datetime import datetime
import duckdb

def main():
    current_datetime = datetime.now()
    notes = sys.argv[1:]


    for note in notes:
        print(f'  {current_datetime.strftime("%y.%m.%d %H:%M:%S")} | {note}')


    ## connect to notes database (or create if it doesn't exist)
    con = duckdb.connect('.notes.db')


    ## create schema and notes table
    con.execute('create schema if not exists coda;')
    con.execute('set schema = coda;')
    con.execute("""
        create table if not exists notes (
            date timestamp,
            message varchar
        );
    """)


    ## load notes into database
    for note in notes:
        con.execute(f"""
            insert into coda.notes
                (date, message)
            values
                (cast('{current_datetime}' as timestamp), '{note}');
        """)


    ## read database contents and write out to console
    result = con.execute("select * from notes;").pl()
    print(result)


    con.close() # close database connection




if __name__ == "__main__":
    main()
