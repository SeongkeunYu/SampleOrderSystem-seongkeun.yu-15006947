import pytest
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository
from src.services.order_service import OrderService
from src.services.production_service import ProductionService
from src.services.sample_service import SampleService
from src.views.console_view import ConsoleView
from src.controllers.monitor_controller import MonitorController
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
def prod_svc(repos):
    return ProductionService(repos[1], repos[0])


@pytest.fixture
def controller(sample_svc, order_svc, prod_svc):
    monitor = Monitor(sample_svc, order_svc, prod_svc)
    return MonitorController(monitor, ConsoleView())


def test_show_dashboard_displays_sample_name(controller, sample_svc, capsys):
    sample_svc.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    controller.show_dashboard()
    assert "GaN" in capsys.readouterr().out


def test_show_dashboard_displays_timestamp(controller, capsys):
    controller.show_dashboard()
    assert "2026" in capsys.readouterr().out


def test_show_dashboard_shows_empty_messages_when_no_data(controller, capsys):
    controller.show_dashboard()
    assert "없습니다" in capsys.readouterr().out


def test_show_order_monitor_displays_order_info(controller, sample_svc, order_svc, capsys):
    sample = sample_svc.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    order_svc.create(sample.id, "홍길동", 10)
    controller.show_order_monitor()
    assert "홍길동" in capsys.readouterr().out


def test_show_stock_monitor_displays_sample_info(controller, sample_svc, capsys):
    sample_svc.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    controller.show_stock_monitor()
    assert "GaN" in capsys.readouterr().out


def test_show_stock_monitor_displays_stock_status(controller, sample_svc, capsys):
    sample_svc.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    controller.show_stock_monitor()
    out = capsys.readouterr().out
    assert any(s in out for s in ["여유", "부족", "고갈"])
