from importlib import metadata
from collections.abc import Callable
from note import notedb as db
from note import console_output as cons


__all__ = [
    'Command',
    'commands',
]


class Command:
    def __init__(self, ids, execute_func) -> None:
        self.ids: tuple[str, ...] = ids
        self.execute: Callable[[tuple[str, ...]], None] = execute_func

    def run(self, args: tuple[str, ...] = ()):
        self.execute(args)


## add notes command ###########################################################

def add_cmd_execute(args: tuple[str, ...]) -> None:
    if len(args) < 1:
        cons.send_error('no add argument')
        return

    add_note_messages: tuple[str, ...] = args

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

add_cmd = Command(
    (
        '-a', 'a',
        '-add', '--add', 'add',
    ),
    add_cmd_execute
)


## list all notes command ##########################################################

def list_cmd_execute(args: tuple[str, ...]) -> None:
    # read database contents and write out to console
    for note in db.get_notes():
        cons.send_note(note)

list_cmd = Command(
    (
        '-l', 'l', '-ls', 'ls',
        '-list', '--list', 'list',
    ),
    list_cmd_execute
)


## short list command ##########################################################

def short_list_cmd_execute(args: tuple[str, ...]) -> None:
    # read database and send notes to console
    # ignore notes tagged :later:
    notes: list[db.Note] = db.get_tag_unmatches('que')

    for note in notes:
        cons.send_note(note)

short_list_cmd = Command(
    ('sls', 'shortls', 'short'),
    short_list_cmd_execute
)


## focus list command ##########################################################

def focus_list_cmd_execute(args: tuple[str, ...]) -> None:
    # read database and send notes to console
    # ignore notes tagged :later:
    notes: list[db.Note] = db.get_tag_matches('mit')
    notes += db.get_tag_matches('tod')

    for note in sorted(set(notes), key=lambda n: n.id):
        cons.send_note(note)

focus_list_cmd = Command(
    ('fls', 'focusls', 'focus'),
    focus_list_cmd_execute
)


## search (general) command ####################################################

def search_cmd_execute(args: tuple[str, ...]) -> None:
    if len(args) < 1:
        cons.send_error('no search argument')
        return

    match: str = args[0]

    for note in db.get_note_matches(match):
        cons.send_note(note)

search_cmd = Command(
    (
        '-s', 's', '-search', '--search', 'search',
        '-f', '-fd', 'fd', '-find', '--find', 'find',
        '-filter', '--filter', 'filter',
    ),
    search_cmd_execute
)


## tag search command ##########################################################

def tag_cmd_execute(args: tuple[str, ...]) -> None:
    if len(args) < 1:
        cons.send_error('no search argument', 'tag')
        return

    tag: str = args[0]

    for note in db.get_tag_matches(tag):
        cons.send_note(note)

tag_cmd = Command(
    ('-t', 't', '-tag', '--tag', 'tag'),
    tag_cmd_execute
)


## update command ##############################################################

def update_cmd_execute(args: tuple[str, ...]) -> None:
    if len(args) < 2:
        cons.send_error('not enough update arguments', 'nid message')
        return

    upd_note_id: str = args[0]

    # valid note id?
    try:
        id: int = int(upd_note_id.strip())
    except ValueError:
        cons.send_error('invalid input', upd_note_id)
        return

    if not db.is_valid(id):
        cons.send_error('not a valid note', str(id))
        return

    message: str = args[1]

    # update note
    db.update_note(id, message)

    # read note back from database and send confirmation
    confirmation_note, *_ = db.get_notes((id,))
    cons.send_confirmation(confirmation_note, "updated")

update_cmd = Command(
    (
        '-u', 'u', '-update', '--update', 'update',
        '-e', 'e', '-edit', '--edit', 'edit',
    ),
    update_cmd_execute
)


## append command ##############################################################

def append_cmd_execute(args: tuple[str, ...]) -> None:
    if len(args) < 2:
        cons.send_error('not enough append arguments', 'nid extension')
        return

    app_note_id: str = args[0]

    # valid note id?
    try:
        id: int = int(app_note_id.strip())
    except ValueError:
        cons.send_error('invalid input', app_note_id)
        return

    if not db.is_valid(id):
        cons.send_error('not a valid note', str(id))
        return

    s: str = args[1]

    # retrieve note
    original_note, *_ = db.get_notes((id,))

    # update note with appended message
    db.update_note(id, original_note.message + ' ' + s)

    # read note back from database and send confirmation
    confirmation_note, *_ = db.get_notes((id,))
    cons.send_confirmation(confirmation_note, "appended")

append_cmd = Command(
    ('-append', '--append', 'append'),
    append_cmd_execute
)


## delete command ##############################################################
# delete selected database entries

def delete_cmd_execute(args: tuple[str, ...]) -> None:
    if len(args) < 1:
        cons.send_error('no delete argument', 'nid')
        return

    # check nid args
    note_ids: tuple[str, ...] = args

    try:
        ids: tuple[int, ...] = tuple(int(nid.strip()) for nid in note_ids)
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

delete_cmd = Command(
    (
        '-d', 'd', '-delete', '--delete', 'delete',
        '-rm', 'rm', '-remove', '--remove', 'remove',
        '-complete', '--complete', 'complete',
        '-done', '--done', 'done',
        '-drop', '--drop', 'drop',
    ),
    delete_cmd_execute
)


## clear command ###############################################################

def clear_cmd_execute(args: tuple[str, ...]) -> None:
    db.clear_database()

clear_cmd = Command(
    (
        '-clear', '--clear',
        '-reset', '--reset',
        '-remove-all', '--remove-all',
    ),
    clear_cmd_execute
)


## rebase command ##############################################################

def rebase_cmd_execute(args: tuple[str, ...]) -> None:
    # update database note ids
    db.rebase()

rebase_cmd = Command(
    ('-rebase', '--rebase', 'rebase'),
    rebase_cmd_execute
)


## version command #############################################################

def version_cmd_execute(args: tuple[str, ...]) -> None:
    cons.send_version(metadata.version("note"))

version_cmd = Command(
    ('-version', '--version'),
    version_cmd_execute
)


## ? command ##########################################################

#def _cmd_execute(args: tuple[str, ...]) -> None:
#    pass
#
#_cmd = Command(
#    ,
#    _cmd_execute
#)


## command list ##

command_list = [
    add_cmd,
    list_cmd,
    short_list_cmd,
    focus_list_cmd,
    search_cmd,
    update_cmd,
    append_cmd,
    tag_cmd,
    delete_cmd,
    clear_cmd,
    rebase_cmd,
    version_cmd,
]


## build command dictionary ####################################################

commands: dict[str, Command] = {id: cmd for cmd in command_list for id in cmd.ids}
