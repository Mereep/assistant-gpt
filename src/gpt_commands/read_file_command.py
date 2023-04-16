from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from exceptions.commands_execption import CommandExecutionError
from exceptions.repository_exceptions import RepositoryAccessNotAllowedException
from gpt_commands.i_command import ICommand


class ReadFileCommand(ICommand):

    @classmethod
    def name(cls) -> str:
        return 'read_file'

    @classmethod
    def description(cls) -> str:
        return 'Reads a file from storage.'

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [CommandArgument(name='file_name',
                                type=str,
                                required=True,
                                help='the file name')]

    def execute(self, chat_context: ChatContext, **args) -> str:
        file_name = args.pop('file_name')
        try:
            res = chat_context.file_storage_backend.read(file_name)
            if res is None:
                return "File not found."
            if res == '':
                return "Empty file."
            return res
        except RepositoryAccessNotAllowedException:
            raise CommandExecutionError(
                reason_for_bot="Not allowed to access `{}`".format(file_name),
                actual_reason="Not allowed to access `{}`".format(file_name)
            )
        except Exception as e:
            raise CommandExecutionError(
                reason_for_bot="Error reading file `{}`".format(file_name),
                actual_reason="Error reading file `{}`: {}".format(file_name, e))

    @classmethod
    def needs_confirmation(cls) -> bool:
        return True

