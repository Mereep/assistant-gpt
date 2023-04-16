from __future__ import annotations

import abc
from typing import Iterable


class IFileStorageBackend(abc.ABC):
    """ Storage backend for files """
    @abc.abstractmethod
    def list(self) -> Iterable[str]:
        ...

    @abc.abstractmethod
    def put(self, key: str, value: str):
        """
        writes the content to the file
        Args:
            key: the key as in the file name
            value: the content to store
        Raises:
            RepositoryAccessNotAllowedException: if the key is not allowed to be accessed
        """

    @abc.abstractmethod
    def read(self, key: str) -> str | None:
        """

        Args:
            key: the key as in the file name
        Returns:
            the content of the file or None if the file does not exist
        Raises:
            RepositoryAccessNotAllowedException: if the key is not allowed to be accessed
        """

    @abc.abstractmethod
    def delete(self, key: str):
        """
        deletes the file
        Args:
            key: the key as in the file name
        Raises:
            RepositoryAccessNotAllowedException: if the key is not allowed to be accessed
        """

