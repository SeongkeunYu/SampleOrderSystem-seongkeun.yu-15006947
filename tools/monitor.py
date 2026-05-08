from dataclasses import dataclass, field
from datetime import datetime

from src.models.order import Order, OrderStatus
from src.models.sample import Sample
from src.services.order_service import OrderService
from src.services.production_service import ProductionService
from src.services.sample_service import SampleService


@dataclass
class MonitorSnapshot:
    timestamp: str
    samples: list[Sample] = field(default_factory=list)
    orders_by_status: dict[str, list[Order]] = field(default_factory=dict)
    production_queue: list[Order] = field(default_factory=list)
    production_progress: list[dict] = field(default_factory=list)

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

        orders_by_status: dict[str, list[Order]] = {}
        for order in orders:
            orders_by_status.setdefault(order.status.value, []).append(order)

        production_queue = sorted(
            [o for o in orders if o.status == OrderStatus.PRODUCING],
            key=lambda o: o.created_at,
        )

        production_progress = self._prod_svc.get_production_progress()

        return MonitorSnapshot(
            timestamp          = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            samples            = samples,
            orders_by_status   = orders_by_status,
            production_queue   = production_queue,
            production_progress= production_progress,
        )
