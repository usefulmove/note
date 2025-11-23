#!/usr/bin/env python3
import sys
from . import console_output as cons
from . import notedb as db
from . import commands as cmd


def main() -> None:
    if not db.PRODUCTION:
        cons.send_warning('running in TEST mode')

    ## no args - list notes ##
    if len(sys.argv) == 1:
        cmd.commands['_'].run()
        return

    ## run command ##
    cmd_id: str = sys.argv[1]

    if cmd_id in cmd.commands:
        cmd.commands[cmd_id].run()
        return

    ## unknown command ##
    cons.send_error('unknown command', sys.argv[1])


if __name__ == "__main__":
    main()
