from exceptions.command_gpt_exception import CommandGptException


class RepositoryException(CommandGptException):
    """ Base Exception when something goes wrong with the repository. """


class RepositoryNotReadableException(RepositoryException):
    """ Raised when the repository is not readable. """
    ...


class RepositoryNotWritableException(RepositoryException):
    """ Raised when the repository is not writable. """


class RepositoryAccessNotAllowedException(RepositoryException):
    """ Raised when the repository access is not allowed. """
