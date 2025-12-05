import sys
import re
from time import sleep, time
from rich.console import Console
from sonia import notedb as db


__all__ = [
    'send_version',
    'send_note',
    'send_confirmation',
    'send_error',
    'send_warning',
    'send_message',
]


## rich console settings ##
console = Console()


# console colors
CDIM = '#616161'
CSEP = '#454545'
CEMPH = '#faf6e4'
CNORM = 'default'
CERR = '#ff0000'
CWARN = '#fff670'


def send_version(version: str) -> None:
    '''Output version message using input version string.'''

    console.print(f'  [{CNORM}]sonia[/] [{CEMPH}]{version}[/]')


def send_note(note: db.Note) -> None:
    '''Output formatted note.'''

    console.print(
        f'  [{CDIM}]{note.date.strftime("%y.%m.%d %H:%M")}[/]' +
        f' [{CSEP}]|[/] ' +
        f'[{CDIM}]{note.id}[/]' +
        f' [{CSEP}]|[/] ' +
        f'[{CNORM}]{color_tags(note.message)}[/]'
    )

    sleep(0.016)


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


def send_warning(warning_message: str, arg: str = '') -> None:
    '''Output formatted warning message.'''

    if arg == '':
        console.print(f'  [{CWARN}]warning[/]: {warning_message}')
    else:
        console.print(f'  [{CWARN}]warning[/]: {warning_message} ([{CDIM}]{arg}[/])')


def send_message(message: str, arg: str = '') -> None:
    '''Output formatted message.'''

    if arg == '':
        console.print(f'  [{CEMPH}]{message}[/{CEMPH}]')
    else:
        console.print(f'  [{CEMPH}]{message}[/{CEMPH}] ([{CDIM}]{arg}[/])')


def send_consider_pause(duration: float) -> None:
    '''Output consider animation for specified time.'''

    animation_delay: float = 0.120
    start: float = time()

    sys.stdout.write('\033[?25l') # hide cursor
    sys.stdout.flush()

    while time() - start < duration:
        sys.stdout.write('\r       ')
        sys.stdout.flush()
        sleep(animation_delay)

        sys.stdout.write('\r    ·  ')
        sys.stdout.flush()
        sleep(animation_delay)

        sys.stdout.write('\r    ·· ')
        sys.stdout.flush()
        sleep(animation_delay)

        sys.stdout.write('\r    ···')
        sys.stdout.flush()
        sleep(animation_delay)

        sys.stdout.write('\r     ··')
        sys.stdout.flush()
        sleep(animation_delay)

        sys.stdout.write('\r      ·')
        sys.stdout.flush()
        sleep(animation_delay)

        sys.stdout.write('\r       ')
        sys.stdout.flush()
        sleep(animation_delay)

        sys.stdout.write('\r       ')
        sys.stdout.flush()
        sleep(animation_delay)

    sys.stdout.write('\r')
    sys.stdout.write('\033[?25h') # show cursor
    sys.stdout.flush()


def color_tags(s: str) -> str:
    '''Apply dimming to tags in input string.'''

    return re.sub(r":([a-zA-Z0-9]*):", f"[{CDIM}]:\\1:[/{CDIM}]", s)
