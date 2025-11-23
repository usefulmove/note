#!/usr/bin/env python3

class Command:
    def __init__(self, ids, check_func, execute_func):
        self.ids = ids
        self.check = check_func
        self.execute = execute_func

    def run(self):
        self.check()
        self.execute()


## add command ##

def add_check():
    print('running add check function')

def add_execute():
    print('running add execution function')

add_command = Command(
    ['a', 'add', '-add', '--add'],
    add_check,
    add_execute
)


## build command dictionary ##

command_list = [
    add_command,
]

commands = {}

for c in command_list:
    for id in c.ids:
        commands.update({id: c})

# commands = {
#     'a': add_command,
#     'add': add_command,
#     '-add': add_command,
#     '--add': add_command,
#     ...
# }

## output result ##

print(f'{commands=}')

commands['a'].run()
