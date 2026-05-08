from src.models.sample import Sample
from src.repositories.sample_repository import SampleRepository


class SampleService:
    def __init__(self, sample_repo: SampleRepository):
        self._repo = sample_repo

    def register(self, name: str, avg_production_time: float, yield_rate: float) -> Sample:
        sample = Sample(
            id=self._next_id(),
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
            stock=0,
        )
        self._repo.save(sample)
        return sample

    def find_all(self) -> list[Sample]:
        return self._repo.find_all()

    def find_by_id(self, id: str) -> Sample:
        sample = self._repo.find_by_id(id)
        if sample is None:
            raise ValueError(f"존재하지 않는 시료: {id}")
        return sample

    def search_by_name(self, keyword: str) -> list[Sample]:
        return self._repo.find_by_name(keyword)

    def add_stock(self, id: str, quantity: int) -> Sample:
        sample = self.find_by_id(id)
        sample.stock += quantity
        self._repo.save(sample)
        return sample

    def _next_id(self) -> str:
        nums = []
        for s in self._repo.find_all():
            parts = s.id.split("-")
            if len(parts) == 2 and parts[0] == "S":
                try:
                    nums.append(int(parts[1]))
                except ValueError:
                    pass
        return f"S-{(max(nums) + 1 if nums else 1):03d}"
