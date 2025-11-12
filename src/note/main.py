#!/usr/bin/env python3
import sys
import re
from importlib import metadata
from . import notedb as db
from rich.console import Console


def main():
    ## rich console settings ##
    console = Console()
    # colors
    cdim = '#616161'
    csep = '#454545'
    cemph = '#faf6e4'
    cnorm = 'default'
    
    def color_tags(s: str) -> str:
        return re.sub(r":([a-z]*):", f"[{cdim}]:\\1:[/{cdim}]", s)


    ## no args - list notes ##
    if len(sys.argv) == 1:
        sys.argv += ['-list']


    ## version ##
    if sys.argv[1] in ('-version', '--version'):
        console.print(
            f'  [{cnorm}]note[/] [{cemph}]{metadata.version("note")}[/]'
        )
        return


    ## list notes ##
    if sys.argv[1] in ('-l', '-ls', '-list', '--list'):
        # read database contents and write out to console
        notes = db.get_notes()

        for nid, dt, msg in notes:
            console.print(
                f'  [{cdim}]{dt.strftime("%y.%m.%d %H:%M")}[/]' +
                f' [{csep}]|[/] ' +
                f'[{cdim}]{nid}[/]' +
                f' [{csep}]|[/] ' +
                f'[{cnorm}]{color_tags(msg)}[/]'
            )

        return


    ## clear notes ##
    if sys.argv[1] in ('-clear', '--clear', '-reset', '--reset'):
        db.clear_database()
        return


    ## delete note(s) ##
    if sys.argv[1] in ('-d', '-delete', '--delete', '-rm', '-complete', '--coplete', '-done', '--done'):
        # delete selected database entries
        note_ids = sys.argv[2:]

        notes = db.get_notes(note_ids)

        db.delete_entries(note_ids)

        for nid, dt, msg in notes:
            console.print(
                f'  [{cnorm}]{color_tags(msg)}[/]' +
                f' [{csep}]|[/] ' +
                f'[{cdim}]{nid}[/]' +
                f' [{csep}]|[/] ' +
                f'[{cnorm}](done)[/]'
            )

        return


    ## search (general) ##
    if sys.argv[1] in ('-s', '-search', '--search', '-f', '-fd', '-find', '--find', '-filter', '--filter'):
        # search database and output results
        match = sys.argv[2]

        search_matches = db.get_note_matches(match)

        for nid, dt, msg in search_matches:
            console.print(
                f'  [{cdim}]{dt.strftime("%y.%m.%d %H:%M")}[/]' +
                f' [{csep}]|[/] ' +
                f'[{cdim}]{nid}[/]' +
                f' [{csep}]|[/] ' +
                f'[{cnorm}]{color_tags(msg)}[/]'
            )

        return
        

    ## tag search ##
    if sys.argv[1] in ('-t', '-tag', '--tag'):
        # search database for tags and output results
        tag = sys.argv[2]

        search_matches = db.get_tag_matches(tag)

        for nid, dt, msg in search_matches:
            console.print(
                f'  [{cdim}]{dt.strftime("%y.%m.%d %H:%M")}[/]' +
                f' [{csep}]|[/] ' +
                f'[{cdim}]{nid}[/]' +
                f' [{csep}]|[/] ' +
                f'[{cnorm}]{color_tags(msg)}[/]'
            )

        return


    ## update note ##
    if sys.argv[1] in ('-u', '-update', '--update', '-e', '-edit', '--edit'):
        note_id = sys.argv[2]
        message = sys.argv[3]

        db.update_entry(note_id, message)

        nid, dt, msg = db.get_notes(note_id)[0]
        console.print(
            f'  [{cnorm}]{color_tags(msg)}[/]' +
            f' [{csep}]|[/] ' +
            f'[{cdim}]{nid}[/]' +
            f' [{csep}]|[/] ' +
            f'[{cnorm}](updated)[/]'
        )

        return


    ## append note ##
    if sys.argv[1] in ('-append', '--append'):
        note_id = sys.argv[2]
        s = sys.argv[3]

        # retrieve note
        nid, dt, msg = db.get_notes(note_id)[0]

        # update notw with appended message
        db.update_entry(note_id, msg + ' ' + s)

        anid, adt, amsg = db.get_notes(note_id)[0]
        console.print(
            f'  [{cnorm}]{color_tags(amsg)}[/]' +
            f' [{csep}]|[/] ' +
            f'[{cdim}]{anid}[/]' +
            f' [{csep}]|[/] ' +
            f'[{cnorm}](appended)[/]'
        )

        return


    ## rebase notes ##
    if sys.argv[1] in ('-rebase', '--rebase'):
        # update database nids
        db.rebase()
        return


    ## check for unknown option ##
    if sys.argv[1].startswith('-'):
        console.print(f'  note: unknown option ([{cdim}]{sys.argv[1]}[/])')
        return


    ## otherwise add notes ##
    # load notes into database
    add_notes = sys.argv[1:]

    db.add_entries(add_notes)

    db_notes = []
    for note in add_notes:
        db_notes += db.get_note_matches(note)

    disp_notes = sorted(
        db_notes,
        key=lambda tup: tup[0],
        reverse=True
    )[:len(add_notes)]

    # display confirmation message
    for nid, dt, msg in disp_notes:
        console.print(
            f'  [{cnorm}]{color_tags(msg)}[/]' +
            f' [{csep}]|[/] ' +
            f'[{cdim}]{nid}[/]' +
            f' [{csep}]|[/] ' +
            f'[{cnorm}](added)[/]'
        )


if __name__ == "__main__":
    main()
