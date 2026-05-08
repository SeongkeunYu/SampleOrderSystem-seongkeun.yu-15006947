import math

from src.models.order import Order, OrderStatus
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository


class ProductionService:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository):
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def complete_production(self) -> Order:
        producing = self._order_repo.find_by_status(OrderStatus.PRODUCING)
        if not producing:
            raise ValueError("생산 중인 주문이 없습니다")

        order = min(producing, key=lambda o: o.created_at)
        sample = self._sample_repo.find_by_id(order.sample_id)

        shortage = max(0, order.quantity - sample.stock)
        if shortage > 0:
            produced = math.ceil(shortage / (sample.yield_rate * 0.9))
            sample.stock += produced

        sample.stock -= order.quantity
        self._sample_repo.save(sample)

        order.status = OrderStatus.CONFIRMED
        self._order_repo.save(order)
        return order

    def release(self, order_id: str) -> Order:
        order = self._get_order(order_id)
        if order.status != OrderStatus.CONFIRMED:
            raise ValueError(f"CONFIRMED 상태가 아닌 주문: {order_id}")
        order.status = OrderStatus.RELEASE
        self._order_repo.save(order)
        return order

    def _get_order(self, order_id: str) -> Order:
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"존재하지 않는 주문: {order_id}")
        return order
