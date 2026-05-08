import uuid
from datetime import datetime

from src.models.order import Order, OrderStatus
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository


class OrderService:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository):
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def create(self, sample_id: str, customer_name: str, quantity: int) -> Order:
        if self._sample_repo.find_by_id(sample_id) is None:
            raise ValueError(f"존재하지 않는 시료: {sample_id}")
        order = Order(
            id=str(uuid.uuid4()),
            sample_id=sample_id,
            customer_name=customer_name,
            quantity=quantity,
            status=OrderStatus.RESERVED,
            created_at=datetime.now().isoformat(),
        )
        self._order_repo.save(order)
        return order

    def approve(self, order_id: str) -> Order:
        order = self._get_order(order_id)
        if order.status != OrderStatus.RESERVED:
            raise ValueError(f"RESERVED 상태가 아닌 주문: {order_id}")
        sample = self._sample_repo.find_by_id(order.sample_id)

        if sample.stock >= order.quantity:
            sample.stock -= order.quantity
            self._sample_repo.save(sample)
            order.status = OrderStatus.CONFIRMED
        else:
            order.status = OrderStatus.PRODUCING

        self._order_repo.save(order)
        return order

    def reject(self, order_id: str) -> Order:
        order = self._get_order(order_id)
        if order.status != OrderStatus.RESERVED:
            raise ValueError(f"RESERVED 상태가 아닌 주문: {order_id}")
        order.status = OrderStatus.REJECTED
        self._order_repo.save(order)
        return order

    def _get_order(self, order_id: str) -> Order:
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"존재하지 않는 주문: {order_id}")
        return order
