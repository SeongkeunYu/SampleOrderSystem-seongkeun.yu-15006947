import pytest
from src.models.order import OrderStatus
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository
from src.services.order_service import OrderService
from src.services.sample_service import SampleService
from tools.monitor import Monitor


@pytest.fixture
def repos(tmp_path):
    return (
        SampleRepository(str(tmp_path / "samples.json")),
        OrderRepository(str(tmp_path / "orders.json")),
    )


@pytest.fixture
def sample_svc(repos):
    return SampleService(repos[0])


@pytest.fixture
def order_svc(repos):
    return OrderService(repos[1], repos[0])


@pytest.fixture
def monitor(sample_svc, order_svc):
    return Monitor(sample_svc, order_svc)


@pytest.fixture
def gan(sample_svc):
    return sample_svc.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)


def test_snapshot_contains_all_samples(monitor, sample_svc):
    sample_svc.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    sample_svc.register(name="SiC", avg_production_time=3.0, yield_rate=0.85)
    snapshot = monitor.get_snapshot()
    assert len(snapshot.samples) == 2


def test_snapshot_has_timestamp(monitor):
    snapshot = monitor.get_snapshot()
    assert len(snapshot.timestamp) > 0


def test_snapshot_calculates_total_stock(monitor, sample_svc):
    s = sample_svc.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    sample_svc.add_stock(s.id, 100)
    snapshot = monitor.get_snapshot()
    assert snapshot.total_stock == 100


def test_snapshot_groups_orders_by_status(monitor, sample_svc, order_svc, gan):
    sample_svc.add_stock(gan.id, 20)
    o1 = order_svc.create(gan.id, "홍길동", 5)
    o2 = order_svc.create(gan.id, "김철수", 5)
    order_svc.approve(o1.id)
    snapshot = monitor.get_snapshot()
    assert "CONFIRMED" in snapshot.orders_by_status
    assert "RESERVED" in snapshot.orders_by_status
    assert len(snapshot.orders_by_status["CONFIRMED"]) == 1
    assert len(snapshot.orders_by_status["RESERVED"]) == 1


def test_snapshot_production_queue_is_fifo_ordered(monitor, order_svc, gan):
    o1 = order_svc.create(gan.id, "홍길동", 10)
    o2 = order_svc.create(gan.id, "김철수", 10)
    order_svc.approve(o1.id)
    order_svc.approve(o2.id)
    snapshot = monitor.get_snapshot()
    assert snapshot.production_queue[0].id == o1.id
    assert snapshot.production_queue[1].id == o2.id


def test_snapshot_empty_when_no_data(monitor):
    snapshot = monitor.get_snapshot()
    assert snapshot.samples == []
    assert snapshot.orders_by_status == {}
    assert snapshot.production_queue == []
    assert snapshot.total_stock == 0
