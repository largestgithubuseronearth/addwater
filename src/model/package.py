from enum import Enum
from os import PathLike
from pathlib import Path
from typing import abstractmethod


class AppPack(Enum):
    _name: str
    _path: Path

    def __init__(self, name: str, path: PathLike | Path) -> None:
        self._name = name
        self._path = Path(path)

    @staticmethod
    @abstractmethod
    def new_from_name(name: str) -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def new_from_path(path: Path | PathLike) -> None:
        raise NotImplementedError


    @property
    def pack_name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

