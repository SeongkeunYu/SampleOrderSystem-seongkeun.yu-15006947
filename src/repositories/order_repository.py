from typing import Optional

from src.models.order import Order, OrderStatus
from src.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def save(self, entity: Order) -> None:
        data = self._load_raw()
        data[entity.id] = entity.to_dict()
        self._dump_raw(data)

    def find_by_id(self, entity_id: str) -> Optional[Order]:
        raw = self._load_raw().get(entity_id)
        return Order.from_dict(raw) if raw else None

    def find_all(self) -> list[Order]:
        return [Order.from_dict(v) for v in self._load_raw().values()]

    def find_by_status(self, status: OrderStatus) -> list[Order]:
        return [o for o in self.find_all() if o.status == status]
