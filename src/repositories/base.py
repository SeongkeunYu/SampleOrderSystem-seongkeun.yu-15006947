import json
import os
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    def __init__(self, path: str):
        self._path = path

    @abstractmethod
    def save(self, entity: T) -> None: ...

    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]: ...

    @abstractmethod
    def find_all(self) -> list[T]: ...

    def _load_raw(self) -> dict:
        if not os.path.exists(self._path):
            return {}
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _dump_raw(self, data: dict) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
