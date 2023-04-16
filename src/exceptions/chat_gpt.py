from exceptions.command_gpt_exception import CommandGptException


class ChatGptException(CommandGptException):
    """ Base Exception when something goes wrong with the chatgpt. """


class ChatGptNotInitialized(ChatGptException):
    """ init function was not called """


class ChatGptNetworkError(ChatGptException):
    """ Something went wrong with the network request """


class ChatGptHttpResponseFailure(ChatGptException):
    """ ChatGPT responded but code was not 200 """


class ChatGptApiResponseFormatError(ChatGptException):
    """ ChatGPT API responded with invalid format """


class ChatGptResponseFormatError(ChatGptException):
    """ ChatGPT responded with invalid format within its message (missed task) """
