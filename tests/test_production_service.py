import math
import pytest
from datetime import datetime, timedelta
from src.models.order import OrderStatus
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository
from src.services.order_service import OrderService
from src.services.production_service import ProductionService
from src.services.sample_service import SampleService


@pytest.fixture
def repos(tmp_path):
    sample_repo = SampleRepository(str(tmp_path / "samples.json"))
    order_repo = OrderRepository(str(tmp_path / "orders.json"))
    return sample_repo, order_repo


@pytest.fixture
def sample_service(repos):
    return SampleService(repos[0])


@pytest.fixture
def order_service(repos):
    return OrderService(repos[1], repos[0])


@pytest.fixture
def production_service(repos):
    return ProductionService(repos[1], repos[0])


@pytest.fixture
def gan(sample_service):
    return sample_service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)


# --- 생산 완료 ---

def test_complete_production_sets_oldest_producing_to_confirmed(
    order_service, production_service, sample_service, gan
):
    o1 = order_service.create(gan.id, "홍길동", 10)
    o2 = order_service.create(gan.id, "김철수", 5)
    order_service.approve(o1.id)
    order_service.approve(o2.id)

    completed = production_service.complete_production()

    assert completed.id == o1.id
    assert completed.status == OrderStatus.CONFIRMED


def test_complete_production_increases_stock_to_fulfill_order(
    order_service, production_service, sample_service, gan
):
    yield_rate = 0.9
    order = order_service.create(gan.id, "홍길동", 10)
    order_service.approve(order.id)

    production_service.complete_production()

    sample = sample_service.find_by_id(gan.id)
    produced = math.ceil(10 / (yield_rate * 0.9))
    assert sample.stock == produced - 10


def test_complete_production_fifo_when_multiple_producing(
    order_service, production_service, sample_service, gan
):
    o1 = order_service.create(gan.id, "홍길동", 5)
    o2 = order_service.create(gan.id, "김철수", 5)
    order_service.approve(o1.id)
    order_service.approve(o2.id)

    first = production_service.complete_production()
    second = production_service.complete_production()

    assert first.id == o1.id
    assert second.id == o2.id


def test_complete_production_raises_if_no_producing_orders(production_service):
    with pytest.raises(ValueError, match="생산 중인 주문이 없습니다"):
        production_service.complete_production()


# --- 출고 ---

def test_release_sets_confirmed_order_to_release(
    order_service, production_service, sample_service, gan
):
    order = order_service.create(gan.id, "홍길동", 10)
    order_service.approve(order.id)          # stock=0 → PRODUCING
    production_service.complete_production() # PRODUCING → CONFIRMED

    released = production_service.release(order.id)

    assert released.status == OrderStatus.RELEASE


def test_release_raises_if_order_not_confirmed(
    order_service, production_service, gan
):
    order = order_service.create(gan.id, "홍길동", 10)
    with pytest.raises(ValueError, match="CONFIRMED 상태가 아닌 주문"):
        production_service.release(order.id)


def test_release_raises_if_order_not_found(production_service):
    with pytest.raises(ValueError, match="존재하지 않는 주문"):
        production_service.release("NONE")


# --- 시간 기반 자동 생산 완료 ---

def test_auto_complete_returns_empty_when_no_producing(production_service):
    assert production_service.auto_complete_productions() == []


def test_auto_complete_does_not_finish_order_immediately(
    production_service, order_service, gan
):
    order = order_service.create(gan.id, "홍길동", 10)
    order_service.approve(order.id)
    result = production_service.auto_complete_productions(now=datetime.now())
    assert result == []


def test_auto_complete_finishes_order_when_time_elapsed(
    production_service, order_service, sample_service, gan
):
    order = order_service.create(gan.id, "홍길동", 10)
    order_service.approve(order.id)
    result = production_service.auto_complete_productions(
        now=datetime.now() + timedelta(hours=1)
    )
    assert len(result) == 1
    assert result[0].status == OrderStatus.CONFIRMED


def test_auto_complete_updates_stock_after_completion(
    production_service, order_service, sample_service, gan
):
    order = order_service.create(gan.id, "홍길동", 10)
    order_service.approve(order.id)
    production_service.auto_complete_productions(
        now=datetime.now() + timedelta(hours=1)
    )
    assert sample_service.find_by_id(gan.id).stock >= 0


def test_auto_complete_fifo_only_completes_first_when_enough_time_for_one(
    production_service, order_service, sample_service, gan
):
    o1 = order_service.create(gan.id, "홍길동", 10)
    o2 = order_service.create(gan.id, "김철수", 10)
    order_service.approve(o1.id)
    order_service.approve(o2.id)

    sample = sample_service.find_by_id(gan.id)
    prod_qty = math.ceil(10 / (sample.yield_rate * 0.9))
    o1_end = (datetime.fromisoformat(o1.created_at)
               + timedelta(minutes=prod_qty * sample.avg_production_time))

    result = production_service.auto_complete_productions(
        now=o1_end + timedelta(seconds=1)
    )
    assert len(result) == 1
    assert result[0].id == o1.id


# --- 생산 진행률 조회 ---

def test_get_production_progress_returns_empty_when_no_producing(production_service):
    assert production_service.get_production_progress() == []


def test_get_production_progress_first_order_is_active(
    production_service, order_service, gan
):
    order = order_service.create(gan.id, "홍길동", 10)
    order_service.approve(order.id)
    progress = production_service.get_production_progress(now=datetime.now())
    assert len(progress) == 1
    assert progress[0]["is_active"] is True


def test_get_production_progress_subsequent_orders_are_waiting(
    production_service, order_service, gan
):
    o1 = order_service.create(gan.id, "홍길동", 10)
    o2 = order_service.create(gan.id, "김철수", 5)
    order_service.approve(o1.id)
    order_service.approve(o2.id)
    progress = production_service.get_production_progress(now=datetime.now())
    assert progress[0]["is_active"] is True
    assert progress[1]["is_active"] is False
    assert progress[1]["progress_pct"] == 0.0


def test_get_production_progress_shows_100_when_complete(
    production_service, order_service, gan
):
    order = order_service.create(gan.id, "홍길동", 10)
    order_service.approve(order.id)
    progress = production_service.get_production_progress(
        now=datetime.now() + timedelta(hours=1)
    )
    assert progress[0]["progress_pct"] == 100.0
