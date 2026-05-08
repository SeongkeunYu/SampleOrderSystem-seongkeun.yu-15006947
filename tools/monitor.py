from dataclasses import dataclass, field
from datetime import datetime

from src.models.order import Order, OrderStatus
from src.models.sample import Sample
from src.services.order_service import OrderService
from src.services.production_service import ProductionService
from src.services.sample_service import SampleService

_MONITORED_STATUSES = {
    OrderStatus.RESERVED, OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED, OrderStatus.RELEASE,
}


@dataclass
class MonitorSnapshot:
    timestamp: str
    samples: list[Sample] = field(default_factory=list)
    orders_by_status: dict[str, list[Order]] = field(default_factory=dict)
    production_queue: list[Order] = field(default_factory=list)
    production_progress: list[dict] = field(default_factory=list)
    stock_health: list[dict] = field(default_factory=list)

    @property
    def total_stock(self) -> int:
        return sum(s.stock for s in self.samples)

    @property
    def order_count(self) -> int:
        return sum(len(v) for v in self.orders_by_status.values())


class Monitor:
    def __init__(self, sample_svc: SampleService, order_svc: OrderService,
                 prod_svc: ProductionService):
        self._sample_svc = sample_svc
        self._order_svc  = order_svc
        self._prod_svc   = prod_svc

    def get_snapshot(self) -> MonitorSnapshot:
        samples = self._sample_svc.find_all()
        orders  = self._order_svc.find_all()

        # REJECTED 제외
        orders_by_status: dict[str, list[Order]] = {}
        for order in orders:
            if order.status in _MONITORED_STATUSES:
                orders_by_status.setdefault(order.status.value, []).append(order)

        production_queue = sorted(
            [o for o in orders if o.status == OrderStatus.PRODUCING],
            key=lambda o: o.created_at,
        )

        production_progress = self._prod_svc.get_production_progress()
        stock_health = _calc_stock_health(samples, orders_by_status)

        return MonitorSnapshot(
            timestamp          = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            samples            = samples,
            orders_by_status   = orders_by_status,
            production_queue   = production_queue,
            production_progress= production_progress,
            stock_health       = stock_health,
        )


def _calc_stock_health(samples: list[Sample],
                       orders_by_status: dict[str, list[Order]]) -> list[dict]:
    demand_by_sample: dict[str, int] = {}
    for status_val in ("RESERVED", "PRODUCING"):
        for o in orders_by_status.get(status_val, []):
            demand_by_sample[o.sample_id] = (
                demand_by_sample.get(o.sample_id, 0) + o.quantity
            )

    result = []
    for s in samples:
        demand = demand_by_sample.get(s.id, 0)
        total  = s.stock + demand

        if s.stock == 0:
            status        = "고갈"
            remaining_pct = 0.0
        elif s.stock < demand:
            status        = "부족"
            remaining_pct = round(s.stock / total * 100, 1)
        else:
            status        = "여유"
            remaining_pct = 100.0 if demand == 0 else round(s.stock / total * 100, 1)

        result.append({
            "sample":        s,
            "demand":        demand,
            "status":        status,
            "remaining_pct": remaining_pct,
        })
    return result
