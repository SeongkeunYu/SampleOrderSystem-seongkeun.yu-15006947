import pytest
from src.models.order import OrderStatus
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository
from src.services.order_service import OrderService
from src.services.sample_service import SampleService


@pytest.fixture
def repos(tmp_path):
    sample_repo = SampleRepository(str(tmp_path / "samples.json"))
    order_repo = OrderRepository(str(tmp_path / "orders.json"))
    return sample_repo, order_repo


@pytest.fixture
def service(repos):
    sample_repo, order_repo = repos
    return OrderService(order_repo, sample_repo)


@pytest.fixture
def sample_service(repos):
    sample_repo, _ = repos
    return SampleService(sample_repo)


@pytest.fixture
def gan(sample_service):
    return sample_service.register(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9)


# --- 주문 생성 ---

def test_create_order_with_reserved_status(service, gan):
    order = service.create(sample_id="S001", customer_name="홍길동", quantity=10)
    assert order.status == OrderStatus.RESERVED
    assert order.sample_id == "S001"
    assert order.customer_name == "홍길동"
    assert order.quantity == 10


def test_create_order_generates_unique_ids(service, gan):
    o1 = service.create(sample_id="S001", customer_name="홍길동", quantity=5)
    o2 = service.create(sample_id="S001", customer_name="김철수", quantity=3)
    assert o1.id != o2.id


def test_create_raises_if_sample_not_found(service):
    with pytest.raises(ValueError, match="존재하지 않는 시료"):
        service.create(sample_id="NONE", customer_name="홍길동", quantity=10)


# --- 승인: 재고 충분 ---

def test_approve_sets_confirmed_when_stock_sufficient(service, sample_service, gan):
    sample_service.add_stock("S001", 20)
    order = service.create(sample_id="S001", customer_name="홍길동", quantity=10)
    approved = service.approve(order.id)
    assert approved.status == OrderStatus.CONFIRMED


def test_approve_deducts_stock_when_sufficient(service, sample_service, gan):
    sample_service.add_stock("S001", 20)
    order = service.create(sample_id="S001", customer_name="홍길동", quantity=10)
    service.approve(order.id)
    assert sample_service.find_by_id("S001").stock == 10


# --- 승인: 재고 부족 ---

def test_approve_sets_producing_when_stock_insufficient(service, sample_service, gan):
    sample_service.add_stock("S001", 5)
    order = service.create(sample_id="S001", customer_name="홍길동", quantity=10)
    approved = service.approve(order.id)
    assert approved.status == OrderStatus.PRODUCING


def test_approve_does_not_deduct_stock_when_insufficient(service, sample_service, gan):
    sample_service.add_stock("S001", 5)
    order = service.create(sample_id="S001", customer_name="홍길동", quantity=10)
    service.approve(order.id)
    assert sample_service.find_by_id("S001").stock == 5


def test_approve_sets_producing_when_stock_is_zero(service, sample_service, gan):
    order = service.create(sample_id="S001", customer_name="홍길동", quantity=10)
    approved = service.approve(order.id)
    assert approved.status == OrderStatus.PRODUCING


# --- 승인 예외 ---

def test_approve_raises_if_order_not_reserved(service, sample_service, gan):
    sample_service.add_stock("S001", 20)
    order = service.create(sample_id="S001", customer_name="홍길동", quantity=5)
    service.approve(order.id)
    with pytest.raises(ValueError, match="RESERVED 상태가 아닌 주문"):
        service.approve(order.id)


def test_approve_raises_if_order_not_found(service):
    with pytest.raises(ValueError, match="존재하지 않는 주문"):
        service.approve("NONE")


# --- 거절 ---

def test_reject_sets_rejected_status(service, gan):
    order = service.create(sample_id="S001", customer_name="홍길동", quantity=10)
    rejected = service.reject(order.id)
    assert rejected.status == OrderStatus.REJECTED


def test_reject_raises_if_order_not_reserved(service, sample_service, gan):
    sample_service.add_stock("S001", 20)
    order = service.create(sample_id="S001", customer_name="홍길동", quantity=5)
    service.approve(order.id)
    with pytest.raises(ValueError, match="RESERVED 상태가 아닌 주문"):
        service.reject(order.id)


def test_reject_raises_if_order_not_found(service):
    with pytest.raises(ValueError, match="존재하지 않는 주문"):
        service.reject("NONE")


# --- 조회 ---

def test_find_all_returns_all_orders(service, gan):
    service.create(sample_id="S001", customer_name="홍길동", quantity=10)
    service.create(sample_id="S001", customer_name="김철수", quantity=5)
    assert len(service.find_all()) == 2


def test_find_all_returns_empty_when_no_orders(service):
    assert service.find_all() == []


def test_find_by_status_filters_correctly(service, sample_service, gan):
    sample_service.add_stock("S001", 20)
    o1 = service.create(sample_id="S001", customer_name="홍길동", quantity=10)
    o2 = service.create(sample_id="S001", customer_name="김철수", quantity=5)
    service.approve(o1.id)
    reserved = service.find_by_status(OrderStatus.RESERVED)
    assert len(reserved) == 1
    assert reserved[0].id == o2.id
