from collections import namedtuple
from handlers import add_command, list_command, done_command, clear_command, clear_confirm_handler, add_next_command

Command = namedtuple('Command', ['name', 'handler', 'handler_type'])
COMMANDS = [
    Command('add', add_command, 'command'),
    Command('add_next', add_next_command, 'command' ),
    Command('list', list_command, 'command'), 
    Command('done', done_command, 'command'),
    Command('clear', clear_command, 'command'),
    Command('clear_handler', clear_confirm_handler, 'callback')
]