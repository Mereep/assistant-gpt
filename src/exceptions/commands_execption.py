from exceptions.command_gpt_exception import CommandGptException


class CommandGptCommandException(CommandGptException):
    """ Command execution related exceptions """


class ArgumentMissingException(CommandGptCommandException):
    """ Raised when an argument is missing """
    def __init__(self, argument: str):
        self.argument = argument
        super().__init__(f"Argument `{argument}` is missing")


class ArgumentTypeException(CommandGptCommandException):
    """ Raised when an argument is of the wrong type """
    def __init__(self, argument: str, expected_type: str, found_type: str):
        self.argument = argument
        self.expected_type = expected_type
        self.found_type = found_type
        super().__init__(f"Argument `{argument}` is of the wrong type. Expected {expected_type}. Found {found_type}")


class CommandExecutionError(CommandGptCommandException):
    """ Raised when an error occurs during command execution """
    def __init__(self, reason_for_bot: str, actual_reason: str):
        super().__init__(actual_reason)
        self.reason_for_bot = reason_for_bot
        self.actual_reason = actual_reason

