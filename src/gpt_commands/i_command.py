import abc
from typing import Any

from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from exceptions.commands_execption import (
    ArgumentMissingException,
    ArgumentTypeException,
)


class ICommand(abc.ABC):
    _collected_args: dict[str, Any]
    _chat_context: ChatContext

    @classmethod
    @abc.abstractmethod
    def description(cls) -> str:
        """The description of the command."""

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        """The name of the command."""
        pass

    @classmethod
    @abc.abstractmethod
    def arguments(cls) -> list[CommandArgument]:
        """which arguments are accepted and which type and function do they have"""
        pass

    def __init__(self, chat_context: ChatContext, **kwargs):
        """Initialize the command.

        Args:
            chat_context: The chat context to provide for execution
        """
        self._chat_context = chat_context
        collected_args = {}
        for argument in self.arguments():
            if argument.name not in kwargs and argument.required:
                raise ArgumentMissingException(argument.name)

            # check if the argument is provided and if it is the correct type
            # if it is not provided and not required, it will be ignored
            if argument.name in kwargs:
                arg = kwargs[argument.name]
                if not isinstance(arg, argument.type):
                    raise ArgumentTypeException(
                        argument=argument.name,
                        expected_type=str(argument.type),
                        found_type=str(type(arg)),
                    )

                collected_args[argument.name] = argument.type(arg)

        self._collected_args = collected_args

    def __call__(self):
        """Call the actual command."""
        return self.execute(chat_context=self._chat_context, **self._collected_args)

    @abc.abstractmethod
    def execute(self, chat_context: ChatContext, **args) -> str:
        """Execute the command.

        Args:
            chat_context: The chat context.
            args: The provided arguments by the bot
        Raises:
            CommandExecutionError: When an error occurs during command execution.
        """

    @classmethod
    @abc.abstractmethod
    def needs_confirmation(cls) -> bool:
        """Does the command need confirmation by the user?  i.e., might ur be harmful or
        leak information."""
