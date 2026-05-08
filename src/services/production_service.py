import math
from datetime import datetime, timedelta

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
        self._complete_order(order)
        return order

    def auto_complete_productions(self, now: datetime | None = None) -> list[Order]:
        """시간 경과 기반으로 FIFO 생산 큐를 확인해 완료된 주문을 자동 처리한다."""
        now = now or datetime.now()
        producing = sorted(
            self._order_repo.find_by_status(OrderStatus.PRODUCING),
            key=lambda o: o.created_at,
        )
        if not producing:
            return []

        completed: list[Order] = []
        for order, _sample, _prod_qty, _start, end in self._build_schedule(producing):
            if now >= end:
                self._complete_order(order)
                completed.append(order)
            else:
                break  # FIFO: 이 주문이 미완이면 이후 주문도 시작 불가
        return completed

    def get_production_progress(self, now: datetime | None = None) -> list[dict]:
        """FIFO 순서로 각 생산 주문의 진행률과 예상 완료 시각을 반환한다."""
        now = now or datetime.now()
        producing = sorted(
            self._order_repo.find_by_status(OrderStatus.PRODUCING),
            key=lambda o: o.created_at,
        )
        result = []
        for i, (order, sample, prod_qty, start, end) in \
                enumerate(self._build_schedule(producing)):
            duration  = end - start
            is_active = (i == 0)
            if is_active:
                elapsed  = max(timedelta(0), now - start)
                progress = min(100.0, elapsed.total_seconds() / duration.total_seconds() * 100)
            else:
                progress = 0.0

            result.append({
                "order":       order,
                "sample_name": sample.name,
                "prod_qty":    prod_qty,
                "start_time":  start,
                "end_time":    end,
                "progress_pct": round(progress, 1),
                "is_active":   is_active,
            })
        return result

    def release(self, order_id: str) -> Order:
        order = self._get_order(order_id)
        if order.status != OrderStatus.CONFIRMED:
            raise ValueError(f"CONFIRMED 상태가 아닌 주문: {order_id}")
        order.status = OrderStatus.RELEASE
        self._order_repo.save(order)
        return order

    def _build_schedule(self, producing: list[Order]) -> list[tuple]:
        """FIFO 순서로 (order, sample, prod_qty, start, end) 튜플 목록을 반환한다."""
        result   = []
        prev_end: datetime | None = None
        for order in producing:
            sample   = self._sample_repo.find_by_id(order.sample_id)
            prod_qty = math.ceil(order.quantity / (sample.yield_rate * 0.9))
            duration = timedelta(minutes=prod_qty * sample.avg_production_time)
            start    = max(datetime.fromisoformat(order.created_at), prev_end) \
                       if prev_end else datetime.fromisoformat(order.created_at)
            end      = start + duration
            prev_end = end
            result.append((order, sample, prod_qty, start, end))
        return result

    def _complete_order(self, order: Order) -> None:
        sample   = self._sample_repo.find_by_id(order.sample_id)
        shortage = max(0, order.quantity - sample.stock)
        if shortage > 0:
            produced = math.ceil(shortage / (sample.yield_rate * 0.9))
            sample.stock += produced
        sample.stock -= order.quantity
        self._sample_repo.save(sample)
        order.status = OrderStatus.CONFIRMED
        self._order_repo.save(order)

    def _get_order(self, order_id: str) -> Order:
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"존재하지 않는 주문: {order_id}")
        return order
