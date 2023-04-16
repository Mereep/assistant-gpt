from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from exceptions.commands_execption import CommandExecutionError
from exceptions.user_interaction import InteractionNotPossible, CouldNotGetResponse
from gpt_commands.i_command import ICommand
from utils.human_interaction import ask_human
import gettext

_ = gettext.gettext


class AskHumanCommand(ICommand):
    @classmethod
    def name(cls) -> str:
        return 'ask_human'

    @classmethod
    def description(cls) -> str:
        return 'Ask the user a specific question. ' \
               'The question must be very precise and not be broad. Do only ask if you don\'t know the answer ' \
               'or have no other way to find it.'

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [CommandArgument(name='question',
                                type=str,
                                required=True,
                                help='the question to ask'),

                CommandArgument(name='human',
                                type=str,
                                required=False,
                                help='the human to ask a question (may also be `all`)')
                ]

    def execute(self, chat_context: ChatContext, **args) -> str:
        try:
            res = ask_human(prompt=_("Question from bot: ") + args.pop('question'),
                            app_settings=chat_context.settings)
            return res
        except InteractionNotPossible as err:
            raise CommandExecutionError(
                reason_for_bot=f"Sorry, I can't ask a human for an answer at the moment.",
                actual_reason=f"The human interaction could not be performed due to {err}")
        except CouldNotGetResponse as err:
            raise CommandExecutionError(
                reason_for_bot=f"The human did not want to answer the question.",
                actual_reason=f"Empty response from human interaction due to {err}")
        except Exception as err:
            raise CommandExecutionError(
                reason_for_bot=f"Sorry, I can't ask a human for an answer at the moment.",
                actual_reason=f"Couldn't interact with human due to unknown error {err}")

    @classmethod
    def needs_confirmation(cls) -> bool:
        return False
