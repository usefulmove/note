#!/usr/bin/env python3
import sys
from importlib import metadata
from . import console_output as cons
from . import notedb as db


def main():
    if not db.PRODUCTION:
        print('  [warning: note running in TEST mode]')


    ## no args - list notes ##
    if len(sys.argv) == 1:
        # read database contents and write out to console
        # ( ignore :later: tagged notes )
        current_notes: list[db.Note] = db.get_tag_unmatches('later')

        for note in current_notes:
            cons.send_note(note)

        return


    ## version ##
    version_flags: tuple[str, ...] = ('-version', '--version')

    if sys.argv[1] in version_flags:
        cons.send_version(metadata.version("note"))
        return


    ## list notes ##
    list_flags: tuple[str, ...] = (
        '-l', 'l', '-ls', 'ls',
        '-list', '--list', 'list',
    )

    if sys.argv[1] in list_flags:
        # read database contents and write out to console
        for note in db.get_notes():
            cons.send_note(note)

        return


    ## clear (remove all) notes ##
    clear_flags: tuple[str, ...] = (
        '-clear', '--clear',
        '-reset', '--reset',
        '-remove-all', '--remove-all',
    )

    if sys.argv[1] in clear_flags:
        db.clear_database()
        return


    ## delete note(s) ##
    delete_flags: tuple[str, ...] = (
        '-d', 'd', '-delete', '--delete', 'delete',
        '-rm', 'rm', '-remove', '--remove', 'remove',
        '-complete', '--complete', 'complete',
        '-done', '--done', 'done',
        '-drop', '--drop', 'drop',
    )

    if sys.argv[1] in delete_flags:
        # delete selected database entries
        note_ids: list[str] = sys.argv[2:]

        conf_notes: list[db.Note] = db.get_notes(note_ids)

        db.delete_entries(note_ids)

        for note in conf_notes:
            cons.send_confirmation(note, "done")

        return


    ## search (general) ##
    message_search_flags: tuple[str, ...] = (
        '-s', 's', '-search', '--search', 'search',
        '-f', '-fd', 'fd', '-find', '--find', 'find',
        '-filter', '--filter', 'filter',
    )

    if sys.argv[1] in message_search_flags:
        # search database and output results
        match: str = sys.argv[2]

        for note in db.get_note_matches(match):
            cons.send_note(note)

        return
        

    ## tag search ##
    tag_search_flags: tuple[str, ...] = ('-t', 't', '-tag', '--tag', 'tag')

    if sys.argv[1] in tag_search_flags:
        # search database for tags and output results
        tag: str = sys.argv[2]

        for note in db.get_tag_matches(tag):
            cons.send_note(note)

        return


    ## update note ##
    update_flags: tuple[str, ...] = (
        '-u', 'u', '-update', '--update', 'update',
        '-e', 'e', '-edit', '--edit', 'edit',
    )

    if sys.argv[1] in update_flags:
        upd_note_id: str = sys.argv[2]
        message: str = sys.argv[3]

        db.update_entry(upd_note_id, message)

        # read note back from database and send confirmation
        cons.send_confirmation(db.get_notes([upd_note_id])[0], "updated")

        return


    ## append note ##
    append_flags: tuple[str, ...] = ('-append', '--append', 'append')

    if sys.argv[1] in append_flags:
        app_note_id: str = sys.argv[2]
        s: str = sys.argv[3]

        # retrieve note
        original_note: db.Note = db.get_notes([app_note_id])[0]

        # update note with appended message
        db.update_entry(app_note_id, original_note.message + ' ' + s)

        # read note back from database and send confirmation
        cons.send_confirmation(db.get_notes([app_note_id])[0], "appended")

        return


    ## rebase notes ##
    rebase_flags: tuple[str, ...] = ('-rebase', '--rebase', 'rebase')

    if sys.argv[1] in rebase_flags:
        # update database note ids
        db.rebase()
        return


    ## add notes ##
    add_flags: tuple[str, ...] = (
        '-a', 'a',
        '-add', '--add', 'add',
    )

    if sys.argv[1] in add_flags:
        # load notes into database
        add_note_messages: list[str] = sys.argv[2:]

        db.add_entries(add_note_messages)

        # read notes back from database and send confirmation

        db_notes: list[db.Note] = []
        for msg in add_note_messages:
            db_notes += db.get_note_matches(msg)

        disp_notes: list[db.Note] = sorted(
            db_notes,
            key=lambda note: note.id,
            reverse=True, # current addition(s) at top
        )[:len(add_note_messages)] # take same number as added

        for note in reversed(disp_notes):
            cons.send_confirmation(note, "added")

        return


    ## check for unknown option ##
    cons.send_option_unknown(sys.argv[1])




if __name__ == "__main__":
    main()
