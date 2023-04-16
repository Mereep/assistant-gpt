from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from gpt_commands.i_command import ICommand


class AnswerCommand(ICommand):

    @classmethod
    def name(cls) -> str:
        return 'answer'

    @classmethod
    def description(cls) -> str:
        return f'Provide a final answer.'

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [CommandArgument(name='answer',
                                type=str,
                                help='the answer or result you want to provide',
                                required=True,
                                )]

    def execute(self, chat_context: ChatContext, **args) -> str:
        return args.pop('answer')

    @classmethod
    def needs_confirmation(cls) -> bool:
        return False
