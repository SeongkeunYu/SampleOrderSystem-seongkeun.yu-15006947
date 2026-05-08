from typing import Optional

from src.models.sample import Sample
from src.repositories.base import BaseRepository


class SampleRepository(BaseRepository[Sample]):
    def save(self, entity: Sample) -> None:
        data = self._load_raw()
        data[entity.id] = entity.to_dict()
        self._dump_raw(data)

    def find_by_id(self, entity_id: str) -> Optional[Sample]:
        raw = self._load_raw().get(entity_id)
        return Sample.from_dict(raw) if raw else None

    def find_all(self) -> list[Sample]:
        return [Sample.from_dict(v) for v in self._load_raw().values()]

    def find_by_name(self, keyword: str) -> list[Sample]:
        return [s for s in self.find_all() if keyword in s.name]
