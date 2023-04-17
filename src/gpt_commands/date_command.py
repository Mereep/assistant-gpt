import datetime

from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from gpt_commands.i_command import ICommand


class DateCommand(ICommand):
    @classmethod
    def name(cls) -> str:
        return "get_datetime"

    @classmethod
    def description(cls) -> str:
        return f"Provides the current date and time"

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return []

    def execute(self, chat_context: ChatContext, **args) -> str:
        return f'The current date is: `{datetime.datetime.now().strftime("%d/%m/%Y at %H:%M:%S")}`'

    @classmethod
    def needs_confirmation(cls) -> bool:
        return False
