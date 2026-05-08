import pytest
from src.models.order import OrderStatus
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository
from src.services.order_service import OrderService
from src.services.sample_service import SampleService
from src.views.console_view import ConsoleView
from src.controllers.order_controller import OrderController


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
def controller(order_svc):
    return OrderController(order_svc, ConsoleView())


@pytest.fixture
def gan(sample_svc):
    return sample_svc.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)


def test_create_registers_order_as_reserved(controller, order_svc, gan, monkeypatch):
    inputs = iter([gan.id, "홍길동", "10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    controller.create()
    orders = order_svc.find_all()
    assert len(orders) == 1
    assert orders[0].status == OrderStatus.RESERVED


def test_create_shows_error_on_unknown_sample(controller, monkeypatch, capsys):
    inputs = iter(["NONE", "홍길동", "10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    controller.create()
    assert "오류" in capsys.readouterr().out


def test_approve_shows_release_when_stock_sufficient(controller, sample_svc, order_svc, gan, monkeypatch, capsys):
    sample_svc.add_stock(gan.id, 20)
    order = order_svc.create(gan.id, "홍길동", 10)
    monkeypatch.setattr("builtins.input", lambda _: order.id)
    controller.approve()
    assert "RELEASE" in capsys.readouterr().out


def test_approve_shows_producing_when_stock_insufficient(controller, order_svc, gan, monkeypatch, capsys):
    order = order_svc.create(gan.id, "홍길동", 10)
    monkeypatch.setattr("builtins.input", lambda _: order.id)
    controller.approve()
    assert "PRODUCING" in capsys.readouterr().out


def test_approve_shows_error_on_invalid_order(controller, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "NONE")
    controller.approve()
    assert "오류" in capsys.readouterr().out


def test_reject_shows_rejected_status(controller, order_svc, gan, monkeypatch, capsys):
    order = order_svc.create(gan.id, "홍길동", 10)
    monkeypatch.setattr("builtins.input", lambda _: order.id)
    controller.reject()
    assert "REJECTED" in capsys.readouterr().out


def test_reject_shows_error_on_invalid_order(controller, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "NONE")
    controller.reject()
    assert "오류" in capsys.readouterr().out


def test_list_all_displays_orders(controller, order_svc, gan, capsys):
    order_svc.create(gan.id, "홍길동", 10)
    controller.list_all()
    assert "홍길동" in capsys.readouterr().out


def test_list_all_shows_empty_when_no_orders(controller, capsys):
    controller.list_all()
    assert "없습니다" in capsys.readouterr().out
