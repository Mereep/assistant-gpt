from exceptions.command_gpt_exception import CommandGptException


class UserInteraction(CommandGptException):
    """Base Exception when something goes wrong with the settings."""


class CouldNotGetResponse(UserInteraction):
    """Raised when no response was given albeit the interaction was possible."""


class InteractionNotPossible(UserInteraction):
    """Raised when the interaction is not possible (User not available / method not supported...)."""
