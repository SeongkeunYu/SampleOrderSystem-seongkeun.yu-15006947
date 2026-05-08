import pytest
from src.models.order import OrderStatus
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository
from src.services.order_service import OrderService
from src.services.sample_service import SampleService
from tools.dummy_generator import DummyGenerator


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
def generator(sample_svc, order_svc):
    return DummyGenerator(sample_svc, order_svc)


def test_generates_correct_number_of_samples(generator, sample_svc):
    generator.generate_samples(3)
    assert len(sample_svc.find_all()) == 3


def test_generated_samples_have_valid_yield_rate(generator, sample_svc):
    generator.generate_samples(5)
    for s in sample_svc.find_all():
        assert 0.0 < s.yield_rate <= 1.0


def test_generated_samples_have_valid_avg_production_time(generator, sample_svc):
    generator.generate_samples(5)
    for s in sample_svc.find_all():
        assert s.avg_production_time > 0


def test_generated_samples_have_zero_stock(generator, sample_svc):
    generator.generate_samples(3)
    for s in sample_svc.find_all():
        assert s.stock == 0


def test_generates_correct_number_of_orders(generator, sample_svc, order_svc):
    generator.generate_samples(2)
    generator.generate_orders(4)
    assert len(order_svc.find_all()) == 4


def test_generated_orders_are_reserved(generator, sample_svc, order_svc):
    generator.generate_samples(2)
    generator.generate_orders(3)
    for o in order_svc.find_all():
        assert o.status == OrderStatus.RESERVED


def test_generated_orders_reference_valid_samples(generator, sample_svc, order_svc):
    generator.generate_samples(2)
    generator.generate_orders(5)
    sample_ids = {s.id for s in sample_svc.find_all()}
    for o in order_svc.find_all():
        assert o.sample_id in sample_ids


def test_generate_orders_raises_if_no_samples(generator):
    with pytest.raises(ValueError, match="등록된 시료가 없습니다"):
        generator.generate_orders(3)
