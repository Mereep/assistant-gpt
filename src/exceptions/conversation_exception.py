from exceptions.command_gpt_exception import CommandGptException


class ConversationException(CommandGptException):
    """ Base Exception when something goes wrong with the conversation. """


class ConversationCannotBeSavedException(ConversationException):
    """ Raised when the conversation cannot be saved. """


class ConversationNotReadableException(ConversationException):
    """ Raised when the conversation is not readable. """


