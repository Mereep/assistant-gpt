from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from gpt_commands.i_command import ICommand


class StorageDeleteCommand(ICommand):
    @classmethod
    def description(cls) -> str:
        return "Deletes a value from the storage."

    @classmethod
    def name(cls) -> str:
        return "storage_delete"

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [
            CommandArgument(
                name="key", type=str, required=True, help="the key to delete"
            ),
        ]

    def execute(self, chat_context: ChatContext, **args) -> str:
        key = args.pop("key")
        if key not in chat_context.key_storage_backend.list():
            return f"Key {key} not found."
        else:
            chat_context.key_storage_backend.delete(key)
            return f"{key} deleted."

    @classmethod
    def needs_confirmation(cls) -> bool:
        return True
