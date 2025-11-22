from . import notedb as db
from rich.console import Console
import re

__all__ = [
    'send_version',
    'send_note',
    'send_confirmation',
    'send_error',
]


## rich console settings ##
console = Console()


# colors
CDIM = '#616161'
CSEP = '#454545'
CEMPH = '#faf6e4'
CNORM = 'default'
CERR = '#ff0000'


def send_version(version: str) -> None:
    '''Output version message using input version string.'''

    console.print(f'  [{CNORM}]note[/] [{CEMPH}]{version}[/]')


def send_note(note: db.Note) -> None:
    '''Output formatted note.'''

    console.print(
        f'  [{CDIM}]{note.date.strftime("%y.%m.%d %H:%M")}[/]' +
        f' [{CSEP}]|[/] ' +
        f'[{CDIM}]{note.id}[/]' +
        f' [{CSEP}]|[/] ' +
        f'[{CNORM}]{color_tags(note.message)}[/]'
    )


def send_confirmation(note: db.Note, action: str) -> None:
    '''Output formatted note confirmation.'''

    console.print(
        f'  [{CNORM}]{color_tags(note.message)}[/]' +
        f' [{CSEP}]|[/] ' +
        f'[{CDIM}]{note.id}[/]' +
        f' [{CSEP}]|[/] ' +
        f'[{CNORM}]({action})[/]'
    )


def send_error(error_message: str, arg: str = '') -> None:
    '''Output formatted error message.'''

    if arg == '':
        console.print(f'  [{CERR}]error[/]: {error_message}')
    else:
        console.print(f'  [{CERR}]error[/]: {error_message} ([{CDIM}]{arg}[/])')


def color_tags(s: str) -> str:
    '''Apply dimming to tags in input string.'''

    return re.sub(r":([a-zA-Z0-9]*):", f"[{CDIM}]:\\1:[/{CDIM}]", s)
