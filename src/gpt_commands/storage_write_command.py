from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from gpt_commands.i_command import ICommand


class StorageWriteCommand(ICommand):
    @classmethod
    def description(cls) -> str:
        return 'Writes a value to the storage. Use this to remember long term information.'

    @classmethod
    def name(cls) -> str:
        return 'storage_write'

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [CommandArgument(name='key',
                                type=str,
                                required=True,
                                help='The storage key. You should be able to make sense of this.'),
                CommandArgument(name='value',
                                type=str,
                                required=True,
                                help='the value to store')
                ]

    def execute(self, chat_context: ChatContext, **args) -> str:
        key = args.pop("key")
        value = args.pop("value")
        chat_context.key_storage_backend.put(key, value)
        return 'Added {key} with value {value} to storage.'.format(key=key, value=value)

    @classmethod
    def needs_confirmation(cls) -> bool:
        return True
