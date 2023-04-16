from exceptions.command_gpt_exception import CommandGptException


class SettingsException(CommandGptException):
    """ Base Exception when something goes wrong with the settings. """


class SettingsNotReadableException(SettingsException):
    """ Raised when the settings are not readable. """


