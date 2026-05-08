from dataclasses import dataclass


@dataclass
class Sample:
    id: str
    name: str
    avg_production_time: float
    yield_rate: float
    stock: int

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "avg_production_time": self.avg_production_time,
            "yield_rate": self.yield_rate,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Sample":
        return cls(
            id=d["id"],
            name=d["name"],
            avg_production_time=d["avg_production_time"],
            yield_rate=d["yield_rate"],
            stock=d["stock"],
        )
