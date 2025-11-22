#!/usr/bin/env python3
import sys
from importlib import metadata
from . import console_output as cons
from . import notedb as db


def main() -> None:
    if not db.PRODUCTION:
        print('  [warning: running in TEST mode]')


    ## no args - list notes ##
    if len(sys.argv) == 1:
        # read database and send notes to console
        # ignore notes tagged :later:
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

        # check for args
        if len(sys.argv) < 3:
            cons.send_error('no delete argument', 'nid')
            return

        # check nid args
        note_ids: list[str] = sys.argv[2:]

        try:
            ids = [int(nid.strip()) for nid in note_ids]
        except ValueError:
            cons.send_error('invalid input')
            return

        for id in ids:
            if not db.is_valid(id):
                cons.send_error('not a valid note', str(id))
                return

        # retrieve notes (for confirmation)
        conf_notes: list[db.Note] = db.get_notes(ids)

        # delete notes
        db.delete_notes(ids)

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

        # check for args
        if len(sys.argv) < 3:
            cons.send_error('no search argument')
            return

        match: str = sys.argv[2]

        for note in db.get_note_matches(match):
            cons.send_note(note)

        return
        

    ## tag search ##
    tag_search_flags: tuple[str, ...] = ('-t', 't', '-tag', '--tag', 'tag')

    if sys.argv[1] in tag_search_flags:
        # search database for tags and output results

        # check for args
        if len(sys.argv) < 3:
            cons.send_error('no search argument', 'tag')
            return

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
        # update identified note

        # check for args
        if len(sys.argv) < 4:
            cons.send_error('not enough update arguments', 'nid message')
            return

        upd_note_id: str = sys.argv[2]

        # valid note id?
        try:
            id = int(upd_note_id.strip())
        except ValueError:
            cons.send_error('invalid input', upd_note_id)
            return

        if not db.is_valid(id):
            cons.send_error('not a valid note', str(id))
            return

        message: str = sys.argv[3]

        # update note
        db.update_note(id, message)

        # read note back from database and send confirmation
        cons.send_confirmation(db.get_notes([id])[0], "updated")

        return


    ## append note ##
    append_flags: tuple[str, ...] = ('-append', '--append', 'append')

    if sys.argv[1] in append_flags:
        # append to identified note

        # check for args
        if len(sys.argv) < 4:
            cons.send_error('not enough append arguments', 'nid extension')
            return

        app_note_id: str = sys.argv[2]

        # valid note id?
        try:
            id = int(app_note_id.strip())
        except ValueError:
            cons.send_error('invalid input', app_note_id)
            return

        if not db.is_valid(id):
            cons.send_error('not a valid note', str(id))
            return

        s: str = sys.argv[3]

        # retrieve note
        original_note: db.Note = db.get_notes([id])[0]

        # update note with appended message
        db.update_note(id, original_note.message + ' ' + s)

        # read note back from database and send confirmation
        cons.send_confirmation(db.get_notes([id])[0], "appended")

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

        db.create_notes(add_note_messages)

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


    ## unknown command ##
    cons.send_error('unknown command', sys.argv[1])




if __name__ == "__main__":
    main()
