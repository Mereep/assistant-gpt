from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from exceptions.repository_exceptions import RepositoryNotReadableException, RepositoryNotWritableException
from repository.i_key_storage_backend import IKeyStorageBackend


class FileKeyKeyStorageKeyBackend(IKeyStorageBackend):
    _path: Path

    def __init__(self, path: Path):
        self._path = path
        if not path.exists():
            if not path.parent.is_dir():
                raise RepositoryNotWritableException(f"Couldn't initialise storage at {path!s} "
                                                     f"because {path.parent!s} is not a directory")
            else:
                try:
                    path.write_text('{}')
                except Exception as e:
                    raise RepositoryNotWritableException(f"Couldn't initialise storage at {path!s} "
                                                         f"due to {str(e)}")
    def list(self) -> Iterable[str]:
        data = self._read()
        return data.keys()

    def put(self, key: str, value: str):
        data = self._read()
        data[key] = value

        try:
            with open(self._path, "w") as file:
                json.dump(data, file)
        except Exception as e:
            raise RepositoryNotWritableException(f"Couldn't write to {file!s} due to {str(e)}")

    def read(self, key: str) -> str | None:
        data = self._read()
        if key in data:
            return data[key]
        else:
            return None

    def delete(self, key: str):
        data = self._read()
        if key in data:
            del data[key]
        try:
            with open(self._path, "w") as file:
                json.dump(data, file)
        except Exception as e:
            raise RepositoryNotWritableException(f"Couldn't delete from `{file!s}` due to `{str(e)}`")

    def _read(self) -> dict[str, str]:
        if not self._path.is_file():
            raise RepositoryNotReadableException(f"{self._path} is not a directory")
        else:
            try:
                with open(self._path, "r") as file:
                    return json.load(file)
            except Exception as e:
                raise RepositoryNotReadableException(f"Couldn't parse "
                                                     f"`{file!s}` due to `{str(e)}`")

