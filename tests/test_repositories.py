import pytest
from src.models.sample import Sample
from src.models.order import Order, OrderStatus
from src.repositories.sample_repository import SampleRepository
from src.repositories.order_repository import OrderRepository


@pytest.fixture
def sample_repo(tmp_path):
    return SampleRepository(str(tmp_path / "samples.json"))


@pytest.fixture
def order_repo(tmp_path):
    return OrderRepository(str(tmp_path / "orders.json"))


@pytest.fixture
def sample():
    return Sample(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9, stock=100)


@pytest.fixture
def order():
    return Order(
        id="O001",
        sample_id="S001",
        customer_name="홍길동",
        quantity=10,
        status=OrderStatus.RESERVED,
        created_at="2026-05-08T00:00:00",
    )


# --- SampleRepository ---

def test_sample_repo_save_and_find_by_id(sample_repo, sample):
    sample_repo.save(sample)
    found = sample_repo.find_by_id("S001")
    assert found.name == "GaN"
    assert found.stock == 100


def test_sample_repo_find_by_id_returns_none_when_not_found(sample_repo):
    assert sample_repo.find_by_id("NONE") is None


def test_sample_repo_find_all_returns_all_saved(sample_repo):
    s1 = Sample(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9, stock=100)
    s2 = Sample(id="S002", name="SiC", avg_production_time=3.0, yield_rate=0.85, stock=50)
    sample_repo.save(s1)
    sample_repo.save(s2)
    all_samples = sample_repo.find_all()
    assert len(all_samples) == 2


def test_sample_repo_save_overwrites_existing(sample_repo, sample):
    sample_repo.save(sample)
    sample.stock = 80
    sample_repo.save(sample)
    found = sample_repo.find_by_id("S001")
    assert found.stock == 80


def test_sample_repo_persists_across_instances(tmp_path, sample):
    path = str(tmp_path / "samples.json")
    SampleRepository(path).save(sample)
    found = SampleRepository(path).find_by_id("S001")
    assert found.name == "GaN"


def test_sample_repo_find_by_name_returns_matching(sample_repo):
    s1 = Sample(id="S001", name="GaN wafer", avg_production_time=2.5, yield_rate=0.9, stock=100)
    s2 = Sample(id="S002", name="SiC", avg_production_time=3.0, yield_rate=0.85, stock=50)
    sample_repo.save(s1)
    sample_repo.save(s2)
    results = sample_repo.find_by_name("GaN")
    assert len(results) == 1
    assert results[0].id == "S001"


# --- OrderRepository ---

def test_order_repo_save_and_find_by_id(order_repo, order):
    order_repo.save(order)
    found = order_repo.find_by_id("O001")
    assert found.customer_name == "홍길동"
    assert found.status == OrderStatus.RESERVED


def test_order_repo_find_by_id_returns_none_when_not_found(order_repo):
    assert order_repo.find_by_id("NONE") is None


def test_order_repo_find_all_returns_all_saved(order_repo):
    o1 = Order(id="O001", sample_id="S001", customer_name="홍길동", quantity=10,
               status=OrderStatus.RESERVED, created_at="2026-05-08T00:00:00")
    o2 = Order(id="O002", sample_id="S001", customer_name="김철수", quantity=5,
               status=OrderStatus.CONFIRMED, created_at="2026-05-08T01:00:00")
    order_repo.save(o1)
    order_repo.save(o2)
    assert len(order_repo.find_all()) == 2


def test_order_repo_find_by_status_filters_correctly(order_repo):
    o1 = Order(id="O001", sample_id="S001", customer_name="홍길동", quantity=10,
               status=OrderStatus.RESERVED, created_at="2026-05-08T00:00:00")
    o2 = Order(id="O002", sample_id="S001", customer_name="김철수", quantity=5,
               status=OrderStatus.CONFIRMED, created_at="2026-05-08T01:00:00")
    order_repo.save(o1)
    order_repo.save(o2)
    reserved = order_repo.find_by_status(OrderStatus.RESERVED)
    assert len(reserved) == 1
    assert reserved[0].customer_name == "홍길동"


def test_order_repo_save_overwrites_existing(order_repo, order):
    order_repo.save(order)
    order.status = OrderStatus.CONFIRMED
    order_repo.save(order)
    found = order_repo.find_by_id("O001")
    assert found.status == OrderStatus.CONFIRMED


def test_order_repo_persists_across_instances(tmp_path, order):
    path = str(tmp_path / "orders.json")
    OrderRepository(path).save(order)
    found = OrderRepository(path).find_by_id("O001")
    assert found.status == OrderStatus.RESERVED
