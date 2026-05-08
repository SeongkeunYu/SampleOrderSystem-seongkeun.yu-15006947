import random

from src.models.order import Order
from src.models.sample import Sample
from src.services.order_service import OrderService
from src.services.sample_service import SampleService

_SAMPLE_NAMES = [
    "GaN", "SiC", "InP", "GaAs", "InGaAs", "AlGaN",
    "Si", "Ge", "InAs", "GaSb", "ZnO", "AlN", "InN", "CdTe", "HgCdTe",
]
_CUSTOMERS = [
    "김철수", "이영희", "박민준", "최수진", "정현우",
    "강지은", "윤성민", "임서연", "한지수", "오승호",
]


class DummyGenerator:
    def __init__(self, sample_svc: SampleService, order_svc: OrderService):
        self._sample_svc = sample_svc
        self._order_svc  = order_svc

    def generate_samples(self, n: int) -> list[Sample]:
        existing_names = {s.name for s in self._sample_svc.find_all()}
        available = [name for name in _SAMPLE_NAMES if name not in existing_names]
        samples = []
        for i in range(n):
            name       = available.pop(0) if available else f"Sample-{i + 1}"
            avg_time   = round(random.uniform(1.0, 15.0), 1)
            yield_rate = round(random.uniform(0.75, 0.98), 2)
            samples.append(self._sample_svc.register(name, avg_time, yield_rate))
        return samples

    def generate_orders(self, n: int) -> list[Order]:
        all_samples = self._sample_svc.find_all()
        if not all_samples:
            raise ValueError("등록된 시료가 없습니다")
        orders = []
        for _ in range(n):
            sample   = random.choice(all_samples)
            customer = random.choice(_CUSTOMERS)
            quantity = random.randint(1, 100)
            orders.append(self._order_svc.create(sample.id, customer, quantity))
        return orders
