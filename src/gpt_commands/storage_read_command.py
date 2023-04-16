from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from gpt_commands.i_command import ICommand


class StorageReadCommand(ICommand):

    @classmethod
    def name(cls) -> str:
        return 'storage_read'

    @classmethod
    def description(cls) -> str:
        return 'Reads a value from the storage.'

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [CommandArgument(name='key',
                                type=str,
                                required=True,
                                help='the storage key')]

    def execute(self, chat_context: ChatContext, **args) -> str:
        key = args.pop("key")
        return chat_context.key_storage_backend.read(key) or 'N/A'

    @classmethod
    def needs_confirmation(cls) -> bool:
        return False
