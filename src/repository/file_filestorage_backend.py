from __future__ import annotations

import abc
import os
from glob import glob
from pathlib import Path
from typing import Iterable

from exceptions.repository_exceptions import RepositoryAccessNotAllowedException
from repository.i_file_storage_backend import IFileStorageBackend


class FileFileStorageBackend(IFileStorageBackend):
    """ Storage backend for files """
    def __init__(self, base_path: Path):
        if not base_path.exists():
            if base_path.parent.is_dir():
                os.makedirs(base_path)
        self._base_path = base_path

    def list(self) -> Iterable[str]:
        for f in glob(f'{self._base_path.absolute()}/**', recursive=True):
            f = str(f)
            if os.path.isfile(f):
                # truncate the part below the base dir
                base_path_len = len(str(self._base_path.absolute()))
                yield f[base_path_len+1:]

    def put(self, key: str, value: str):
        self.check_access_policy(key)
        with open(self._base_path / key, 'w') as file:
            file.write(value)

    def read(self, key: str) -> str | None:
        self.check_access_policy(key)
        try:
            with open(self._base_path / key, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return None

    def delete(self, key: str):
        self.check_access_policy(key)
        os.remove(self._base_path / key)

    def check_access_policy(self, key: str):
        """ Checks if the key is allowed to be accessed
        Raises:
            RepositoryAccessNotAllowedException: if the key is not allowed to be accessed (..)
        """
        if '..' in key:
            raise RepositoryAccessNotAllowedException(f'Key `{key}` is not allowed.')