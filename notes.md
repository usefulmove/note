```python
class Command:
    flags: List[str]
    check: function
    execute: function
    run: function

add_command = Command(...)

# command dictionary
commands = {}

for c in commands:
    for s in c.flags:
        commands[s] = c

# commands = {
#     'a': add_command,
#     'add': add_command,
#     '-add': add_command,
#     '--add': add_command,
#     ...
# }
```

```python
cmd = sys.argv[1]

if cmd in commands:
    commands[cmd].run()
    return

## unknown command ##
cons.send_error('unknown command', cmd)
```
