from __future__ import annotations

import abc
from typing import Iterable


class IKeyStorageBackend(abc.ABC):
    """ simple storage for key value pairs """
    @abc.abstractmethod
    def list(self) -> Iterable[str]:
        ...

    @abc.abstractmethod
    def put(self, key: str, value: str):
        ...

    @abc.abstractmethod
    def read(self, key: str) -> str | None:
        ...

    @abc.abstractmethod
    def delete(self, key: str):
        ...
