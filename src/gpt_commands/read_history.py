from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from datatypes.gpt_response import GptResponse
from datatypes.user_message import UserMessage
from gpt_commands.i_command import ICommand


class ReadConversationHistory(ICommand):
    @classmethod
    def name(cls) -> str:
        return "read_conversation_history"

    @classmethod
    def description(cls) -> str:
        return (
            f"reads / retrieves an old message of the conversation by its index. Only use this if you don't "
            f"have the information you need and you are sure we talked about this"
        )

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [
            CommandArgument(
                name="index",
                type=int,
                help="the index of the message to read / retrieve",
                required=True,
            )
        ]

    def execute(self, chat_context: ChatContext, **args) -> str:
        index = args.pop("index")
        if index < 0:
            return "Index must be positive."

        if index >= len(chat_context.message_history):
            return "Index out of range. As of now, we only have {} messages in the message history.".format(
                len(chat_context.message_history)
            )

        message = chat_context.message_history[index]
        r = "Message at index #{}:\n".format(index)
        if isinstance(message, UserMessage):
            return (
                r
                + f"User message from user `{message.user}`: \n{message.user_response}\n "
                f"with additional info: {message.additional_info}"
            )
        elif isinstance(message, GptResponse):
            return r + "This was a message provided by you:\n{message}\n".format(
                message=message.json()
            )

    @classmethod
    def needs_confirmation(cls) -> bool:
        return False
