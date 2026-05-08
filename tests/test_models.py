import pytest
from src.models.sample import Sample
from src.models.order import Order, OrderStatus


# --- Sample ---

def test_sample_has_required_fields():
    sample = Sample(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9, stock=100)
    assert sample.id == "S001"
    assert sample.name == "GaN"
    assert sample.avg_production_time == 2.5
    assert sample.yield_rate == 0.9
    assert sample.stock == 100


def test_sample_to_dict_contains_all_fields():
    sample = Sample(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9, stock=100)
    d = sample.to_dict()
    assert d == {
        "id": "S001",
        "name": "GaN",
        "avg_production_time": 2.5,
        "yield_rate": 0.9,
        "stock": 100,
    }


def test_sample_from_dict_restores_object():
    d = {"id": "S001", "name": "GaN", "avg_production_time": 2.5, "yield_rate": 0.9, "stock": 100}
    sample = Sample.from_dict(d)
    assert sample.id == "S001"
    assert sample.name == "GaN"
    assert sample.avg_production_time == 2.5
    assert sample.yield_rate == 0.9
    assert sample.stock == 100


# --- OrderStatus ---

def test_order_status_has_all_states():
    assert OrderStatus.RESERVED.value == "RESERVED"
    assert OrderStatus.REJECTED.value == "REJECTED"
    assert OrderStatus.PRODUCING.value == "PRODUCING"
    assert OrderStatus.CONFIRMED.value == "CONFIRMED"
    assert OrderStatus.RELEASE.value == "RELEASE"


# --- Order ---

def test_order_has_required_fields():
    order = Order(
        id="O001",
        sample_id="S001",
        customer_name="홍길동",
        quantity=10,
        status=OrderStatus.RESERVED,
        created_at="2026-05-08T00:00:00",
    )
    assert order.id == "O001"
    assert order.sample_id == "S001"
    assert order.customer_name == "홍길동"
    assert order.quantity == 10
    assert order.status == OrderStatus.RESERVED
    assert order.created_at == "2026-05-08T00:00:00"


def test_order_to_dict_serializes_status_as_string():
    order = Order(
        id="O001",
        sample_id="S001",
        customer_name="홍길동",
        quantity=10,
        status=OrderStatus.RESERVED,
        created_at="2026-05-08T00:00:00",
    )
    d = order.to_dict()
    assert d["status"] == "RESERVED"


def test_order_from_dict_restores_status_enum():
    d = {
        "id": "O001",
        "sample_id": "S001",
        "customer_name": "홍길동",
        "quantity": 10,
        "status": "RESERVED",
        "created_at": "2026-05-08T00:00:00",
    }
    order = Order.from_dict(d)
    assert order.status == OrderStatus.RESERVED
