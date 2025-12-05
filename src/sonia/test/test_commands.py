import os
from sonia import commands as cmd


entries: tuple[str, ...] = ('test_one', 'test_two', 'test_three')
test_path = './src/sonia/test/commands_test.db'


def test_cmd() -> None:
    print('test: sonia db version')
    cmd.commands['db'].run((test_path, 'version'))

    print('test: sonia add [...]')
    cmd.commands['add'].run(entries)

    print('test: sonia list')
    cmd.commands['list'].run()

    print('test: sonia search test')
    cmd.commands['search'].run(('test',))
    
    print('test: sonia update 1 [...]')
    cmd.commands['update'].run(('1', 'test_one :tag:'))

    print('test: sonia tag tag')
    cmd.commands['tag'].run(('tag',))

    print('test: sonia drop 1 3')
    cmd.commands['drop'].run(('1', '3',))

    print('test: sonia list')
    cmd.commands['list'].run()

    print('test: sonia rebase')
    cmd.commands['rebase'].run()

    print('test: sonia list')
    cmd.commands['list'].run()

    print('test: sonia -reset')
    cmd.commands['-reset'].run()

    print('test: sonia list')
    cmd.commands['list'].run()


def test_clean_up() -> None:
    # remove test database if exists
    if os.path.exists(test_path):
        os.remove(test_path)
