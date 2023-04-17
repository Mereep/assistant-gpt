from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from exceptions.commands_execption import CommandExecutionError
from gpt_commands.i_command import ICommand
from utils.chatgpt import send_message


class AskAiAgentCommand(ICommand):

    @classmethod
    def name(cls) -> str:
        return 'ask_ai_agent'

    @classmethod
    def description(cls) -> str:
        return f'Ask an AI agent (like ChatGPT)  a question. ' \
               f'Can to gather general information and reasoning about a topic. ' \
               f'The agent is smart and very useful in reasoning and providing knowledge.'

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [CommandArgument(name='prompt',
                                type=str,
                                help='the prompt / question to ask the bot',
                                required=True,
                                )]

    def execute(self, chat_context: ChatContext, **args) -> str:
        question = args.pop('prompt')
        try:
            res = send_message(user_message=question,
                               model=chat_context.settings.model,
                               system_role="Knowledgeable Assistant that answer questions "
                                           "as precise as possible.",
                               logger=chat_context.default_logger
                               )
            return res
        except Exception as err:
            raise CommandExecutionError(
                reason_for_bot=f"Sorry, I can't ask a bot for an answer at the moment.",
                actual_reason=f"Couldn't interact with bot due to unknown error {err}")

    @classmethod
    def needs_confirmation(cls) -> bool:
        return True

