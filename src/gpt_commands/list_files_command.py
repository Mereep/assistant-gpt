from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from exceptions.commands_execption import CommandExecutionError
from gpt_commands.i_command import ICommand


class ListFilesCommand(ICommand):
    @classmethod
    def name(cls) -> str:
        return "list_files"

    @classmethod
    def description(cls) -> str:
        return "Lists all files in the file storage. You can receive all files we created during the conversation."

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return []

    def execute(self, chat_context: ChatContext, **args) -> str:
        try:
            files = list(chat_context.file_storage_backend.list())
            if files:
                return "Files found: " + ", ".join(files)
            else:
                return "No files found."

        except Exception as e:
            raise CommandExecutionError(
                reason_for_bot="Error listing file storage",
                actual_reason="Error reading file storage: {}".format(e),
            )

    @classmethod
    def needs_confirmation(cls) -> bool:
        return True
