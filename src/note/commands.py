import sys
from importlib import metadata
from collections.abc import Callable
from note import notedb as db
from note import console_output as cons


__all__ = [
    'Command',
    'commands',
]


class Command:
    def __init__(self, ids, check_func, execute_func) -> None:
        self.ids: tuple[str, ...] = ids
        self.check: Callable[[None], bool] = check_func
        self.execute: Callable[[None], None] = execute_func

    def run(self):
        if self.check():
            self.execute()


## add notes command ###########################################################

def add_cmd_check() -> bool:
    if len(sys.argv) < 3:
        cons.send_error('no add argument')
        return False

    return True

def add_cmd_execute() -> None:
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

add_cmd = Command(
    (
        '-a', 'a',
        '-add', '--add', 'add',
    ),
    add_cmd_check,
    add_cmd_execute
)


## list all notes command ##########################################################

def list_cmd_execute() -> None:
    # read database contents and write out to console
    for note in db.get_notes():
        cons.send_note(note)

list_cmd = Command(
    (
        '-l', 'l', '-ls', 'ls',
        '-list', '--list', 'list',
    ),
    lambda : True,
    list_cmd_execute
)


## short list command ##########################################################

def short_list_cmd_execute() -> None:
    # read database and send notes to console
    # ignore notes tagged :later:
    current_notes: list[db.Note] = db.get_tag_unmatches('later')

    for note in current_notes:
        cons.send_note(note)

short_list_cmd = Command(
    ('_', 'shortls'),
    lambda : True,
    short_list_cmd_execute
)


## search (general) command ####################################################

def search_cmd_check() -> bool:
    if len(sys.argv) < 3:
        cons.send_error('no search argument')
        return False

    return True

def search_cmd_execute() -> None:
    match: str = sys.argv[2]

    for note in db.get_note_matches(match):
        cons.send_note(note)

search_cmd = Command(
    (
        '-s', 's', '-search', '--search', 'search',
        '-f', '-fd', 'fd', '-find', '--find', 'find',
        '-filter', '--filter', 'filter',
    ),
    search_cmd_check,
    search_cmd_execute
)


## tag search command ##########################################################

def tag_cmd_check() -> bool:
    if len(sys.argv) < 3:
        cons.send_error('no search argument', 'tag')
        return False

    return True

def tag_cmd_execute() -> None:
    tag: str = sys.argv[2]

    for note in db.get_tag_matches(tag):
        cons.send_note(note)

tag_cmd = Command(
    ('-t', 't', '-tag', '--tag', 'tag'),
    tag_cmd_check,
    tag_cmd_execute
)


## update command ##############################################################

def update_cmd_check() -> bool:
    if len(sys.argv) < 4:
        cons.send_error('not enough update arguments', 'nid message')
        return False

    upd_note_id: str = sys.argv[2]

    # valid note id?
    try:
        id: int = int(upd_note_id.strip())
    except ValueError:
        cons.send_error('invalid input', upd_note_id)
        return False

    if not db.is_valid(id):
        cons.send_error('not a valid note', str(id))
        return False

    return True

def update_cmd_execute() -> None:
    upd_note_id: str = sys.argv[2]
    message: str = sys.argv[3]

    id: int = int(upd_note_id.strip())

    # update note
    db.update_note(id, message)

    # read note back from database and send confirmation
    confirmation_note, *_ = db.get_notes([id])
    cons.send_confirmation(confirmation_note, "updated")

update_cmd = Command(
    (
        '-u', 'u', '-update', '--update', 'update',
        '-e', 'e', '-edit', '--edit', 'edit',
    ),
    update_cmd_check,
    update_cmd_execute
)


## append command ##############################################################

def append_cmd_check() -> bool:
    if len(sys.argv) < 4:
        cons.send_error('not enough append arguments', 'nid extension')
        return False

    app_note_id: str = sys.argv[2]

    # valid note id?
    try:
        id: int = int(app_note_id.strip())
    except ValueError:
        cons.send_error('invalid input', app_note_id)
        return False

    if not db.is_valid(id):
        cons.send_error('not a valid note', str(id))
        return False

    return True

def append_cmd_execute() -> None:
    app_note_id: str = sys.argv[2]
    s: str = sys.argv[3]

    id: int = int(app_note_id.strip())

    # retrieve note
    original_note, *_ = db.get_notes([id])

    # update note with appended message
    db.update_note(id, original_note.message + ' ' + s)

    # read note back from database and send confirmation
    confirmation_note, *_ = db.get_notes([id])
    cons.send_confirmation(confirmation_note, "appended")

append_cmd = Command(
    ('-append', '--append', 'append'),
    append_cmd_check,
    append_cmd_execute
)


## delete command ##############################################################
# delete selected database entries

def delete_cmd_check() -> bool:
    if len(sys.argv) < 3:
        cons.send_error('no delete argument', 'nid')
        return False

    # check nid args
    note_ids: list[str] = sys.argv[2:]

    try:
        ids: list[int] = [int(nid.strip()) for nid in note_ids]
    except ValueError:
        cons.send_error('invalid input')
        return False

    for id in ids:
        if not db.is_valid(id):
            cons.send_error('not a valid note', str(id))
            return False

    return True

def delete_cmd_execute() -> None:
    note_ids: list[str] = sys.argv[2:]
    ids: list[int] = [int(nid.strip()) for nid in note_ids]

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
    delete_cmd_check,
    delete_cmd_execute
)


## clear command ###############################################################

def clear_cmd_execute() -> None:
    db.clear_database()

clear_cmd = Command(
    (
        '-clear', '--clear',
        '-reset', '--reset',
        '-remove-all', '--remove-all',
    ),
    lambda : True,
    clear_cmd_execute
)


## rebase command ##############################################################

def rebase_cmd_execute() -> None:
    # update database note ids
    db.rebase()

rebase_cmd = Command(
    ('-rebase', '--rebase', 'rebase'),
    lambda : True,
    rebase_cmd_execute
)


## version command #############################################################

def version_cmd_execute() -> None:
    cons.send_version(metadata.version("note"))

version_cmd = Command(
    ('-version', '--version'),
    lambda : True,
    version_cmd_execute
)


## ? command ##########################################################

#def _cmd_check() -> bool:
#    return True
#
#def _cmd_execute() -> None:
#    pass
#
#_cmd = Command(
#    ,
#    _cmd_check,
#    _cmd_execute
#)


## command list ##

command_list = [
    add_cmd,
    list_cmd,
    short_list_cmd,
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
