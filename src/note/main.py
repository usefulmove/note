#!/usr/bin/env python3
import sys
from note import console_output as cons
from note import notedb as db
from note import commands as cmd


def main() -> None:
    if not db.PRODUCTION:
        cons.send_warning('running in TEST mode')

    match sys.argv:
        case _, cmd_id, *args if cmd_id in cmd.commands:
            cmd.commands[cmd_id].run()

        case [_]: # no args
            cmd.commands['shortls'].run()

        case _, unknown, *_: 
            cons.send_error('unknown command', unknown)


if __name__ == "__main__":
    main()
