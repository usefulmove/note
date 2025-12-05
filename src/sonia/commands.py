from importlib import metadata
from collections.abc import Callable
from random import randrange
from sonia import notedb as db
from sonia import console_output as cons


__all__ = [
    'Command',
    'commands',
]


class Command:
    '''Command behavior objects.'''
    def __init__(self, ids: tuple[str, ...], execute_func: Callable[[tuple[str, ...]], None]) -> None:
        self.ids: tuple[str, ...] = ids
        self.execute: Callable[[tuple[str, ...]], None] = execute_func

    def __repr__(self) -> str:
        return f'Command({self.ids[0]!r}, {self.execute!r})'

    def run(self, args: tuple[str, ...] = ()) -> None:
        '''Run (execute) command.'''
        self.execute(args)


## add notes command ###########################################################

def add_cmd_execute(messages: tuple[str, ...]) -> None:
    '''Add notes command execution function.'''

    if len(messages) < 1:
        cons.send_error('no add argument')
        return

    db_notes: list[db.Note] = db.create_notes(messages)

    # send confirmation using notes read back from database
    for note in db_notes:
        cons.send_confirmation(note, "added")

add_cmd = Command(
    ('add',  'a'),
    add_cmd_execute
)


## list all notes command ##########################################################

def list_cmd_execute(_: tuple[str, ...] = ()) -> None:
    '''List notes command execution function.'''

    # read database contents and write out to console
    for note in db.get_notes():
        cons.send_note(note)

list_cmd = Command(
    ('list', 'ls', 'long', 'all'),
    list_cmd_execute
)


## short list command ##########################################################

def short_list_cmd_execute(_: tuple[str, ...] = ()) -> None:
    '''Limited (short) list command execution function. Ignore :que: tagged notes.'''

    # read database and send notes to console
    notes: list[db.Note] = db.get_tag_unmatches('que')

    for note in notes:
        cons.send_note(note)

short_list_cmd = Command(
    ('important', 'imp', 'shortls', 'short', 'slist', 'sls', '_'),
    short_list_cmd_execute
)


## focus list command ##########################################################

def focus_list_cmd_execute(_: tuple[str, ...] = ()) -> None:
    '''Focus list command execution function. Show :mit: and :tod: tagged notes.'''

    # read database and send notes to console
    notes: list[db.Note] = db.get_tag_matches('mit')
    notes += db.get_tag_matches('tod')

    for note in sorted(set(notes), key=lambda note: note.id):
        cons.send_note(note)

focus_list_cmd = Command(
    ('focusls', 'focus', 'flist', 'fls'),
    focus_list_cmd_execute
)


## search (general) command ####################################################

def search_cmd_execute(args: tuple[str, ...]) -> None:
    '''Search notes command execution function. Show notes that match search term.'''

    if len(args) < 1:
        cons.send_error('no search argument')
        return

    match: str = args[0]

    for note in db.get_note_matches(match):
        cons.send_note(note)

search_cmd = Command(
    ('search', 's', 'find', 'f', 'fd', 'filter'),
    search_cmd_execute
)


## tag search command ##########################################################

def tag_cmd_execute(args: tuple[str, ...]) -> None:
    '''Search tag command execution function. Show notes that contain provided tag.'''

    if len(args) < 1:
        cons.send_error('no search argument', 'tag')
        return

    tag: str = args[0].strip(':')

    for note in db.get_tag_matches(tag):
        cons.send_note(note)

tag_cmd = Command(
    ('tag', 't'),
    tag_cmd_execute
)


## update command ##############################################################

def update_cmd_execute(args: tuple[str, ...]) -> None:
    '''Update note command execution function. Change note at provided note ID (nid).'''

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
    ('update', 'u', 'edit', 'e'),
    update_cmd_execute
)


## append command ##############################################################

def append_cmd_execute(args: tuple[str, ...]) -> None:
    '''Append note command execution function. Append text to provided note ID (nid).'''

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
    ('append', 'app'),
    append_cmd_execute
)


## delete command ##############################################################
# delete selected database entries

def delete_cmd_execute(nids: tuple[str, ...]) -> None:
    '''Delete note command execution function. Delete provided note IDs (nids).'''

    if len(nids) < 1:
        cons.send_error('no delete argument', 'nid')
        return

    # check nids
    try:
        ids: tuple[int, ...] = tuple(int(nid.strip()) for nid in nids)
    except ValueError:
        cons.send_error('invalid input')
        return

    for id in ids:
        if not db.is_valid(id):
            cons.send_error('not a valid note', str(id))
            return

    # delete notes and retrieve confirmation
    conf_notes: list[db.Note] = db.delete_notes(ids)

    for note in conf_notes:
        cons.send_confirmation(note, "removed")

delete_cmd = Command(
    ('delete', 'd', 'remove', 'rm', 'done', 'drop', 'complete'),
    delete_cmd_execute
)


## clear command ###############################################################

def clear_cmd_execute(_: tuple[str, ...] = ()) -> None:
    '''Clear database command execution function.'''

    db.clear_database()

clear_cmd = Command(
    ('-clear', '--clear', '-reset', '--reset', '-remove-all', '--remove-all'),
    clear_cmd_execute
)


## rebase command ##############################################################

def rebase_cmd_execute(_: tuple[str, ...] = ()) -> None:
    '''Rebase note IDs command execution function.'''

    # update database note ids
    db.rebase()

rebase_cmd = Command(
    ('rebase', '-rebase', '--rebase'),
    rebase_cmd_execute
)


## version command #############################################################

def version_cmd_execute(_: tuple[str, ...] = ()) -> None:
    '''Version command execution function.'''

    cons.send_version(metadata.version("sonia"))

version_cmd = Command(
    ('version', 'v', '-version', '--version'),
    version_cmd_execute
)


## select database command #####################################################
# use specified database

def db_cmd_execute(args: tuple[str, ...]) -> None:
    '''Use specified database command execution function.'''

    if len(args) < 1:
        cons.send_error('no database argument')
        return

    db_path, *rest = args

    # set database path
    if not db.set_path(db_path):
        cons.send_error('could not use database path', db_path)
        return

    # execute command
    match rest:
        case cmd_id, *cargs if cmd_id in commands:
            commands[cmd_id].run(tuple(cargs))
        case []: # no args
            commands['focus'].run()
        case unknown, *_: 
            cons.send_error('unknown command', unknown)


db_cmd = Command(
    ('db',),
    db_cmd_execute
)


## decide command ##############################################################
def decide_cmd_execute(_: tuple[str, ...] = ()) -> None:
    '''Provide helpful output.'''
    cons.send_consider_pause(3.8)
    cons.send_message(decisions[randrange(len(decisions))], str(randrange(52, 98)))
    return

decide_cmd = Command(
    ('decide',),
    decide_cmd_execute
)

decisions = (
    "do it",
    "it is certain",
    "it is decidedly so",
    "without a doubt",
    "definitely",
    "rely on it",
    "most likely",
    "outlook good",
    "yes",
    "signs point to yes",
    "reply hazy, try again",
    "ask again later",
    "better not tell you now",
    "cannot predict now",
    "focus and ask again",
    "don't count on it",
    "no",
    "sources say no",
    "outlook not so good",
    "doubtful",
)



## command list - register commands ##
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
    db_cmd,
    decide_cmd,
]



## build command dictionary ##
commands: dict[str, Command] = {id: cmd for cmd in command_list for id in cmd.ids}
