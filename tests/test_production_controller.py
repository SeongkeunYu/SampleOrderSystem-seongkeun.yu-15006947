import pytest
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository
from src.services.order_service import OrderService
from src.services.production_service import ProductionService
from src.services.sample_service import SampleService
from src.views.console_view import ConsoleView
from src.controllers.production_controller import ProductionController


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
def prod_svc(repos):
    return ProductionService(repos[1], repos[0])


@pytest.fixture
def controller(prod_svc, order_svc):
    return ProductionController(prod_svc, order_svc, ConsoleView())


@pytest.fixture
def gan(sample_svc):
    return sample_svc.register("S001", "GaN", 2.5, 0.9)


def test_complete_production_shows_confirmed(controller, order_svc, gan, capsys):
    order = order_svc.create("S001", "홍길동", 10)
    order_svc.approve(order.id)
    controller.complete_production()
    assert "CONFIRMED" in capsys.readouterr().out


def test_complete_production_shows_error_when_none_producing(controller, capsys):
    controller.complete_production()
    assert "오류" in capsys.readouterr().out


def test_release_shows_release_status(controller, sample_svc, order_svc, gan, monkeypatch, capsys):
    sample_svc.add_stock("S001", 20)
    order = order_svc.create("S001", "홍길동", 10)
    order_svc.approve(order.id)
    monkeypatch.setattr("builtins.input", lambda _: order.id)
    controller.release()
    assert "RELEASE" in capsys.readouterr().out


def test_release_shows_error_on_invalid_order(controller, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "NONE")
    controller.release()
    assert "오류" in capsys.readouterr().out


def test_list_queue_shows_producing_orders(controller, order_svc, gan, capsys):
    order = order_svc.create("S001", "홍길동", 10)
    order_svc.approve(order.id)
    controller.list_queue()
    assert "홍길동" in capsys.readouterr().out


def test_list_queue_shows_empty_when_none_producing(controller, capsys):
    controller.list_queue()
    assert "없습니다" in capsys.readouterr().out
