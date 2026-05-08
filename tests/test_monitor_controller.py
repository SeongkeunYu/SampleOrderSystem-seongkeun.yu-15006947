import pytest
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository
from src.services.order_service import OrderService
from src.services.sample_service import SampleService
from src.views.console_view import ConsoleView
from src.controllers.monitor_controller import MonitorController
from tools.monitor import Monitor
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
def controller(sample_svc, order_svc):
    monitor   = Monitor(sample_svc, order_svc)
    generator = DummyGenerator(sample_svc, order_svc)
    return MonitorController(monitor, generator, ConsoleView())


def test_show_dashboard_displays_sample_name(controller, sample_svc, capsys):
    sample_svc.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    controller.show_dashboard()
    assert "GaN" in capsys.readouterr().out


def test_show_dashboard_displays_timestamp(controller, capsys):
    controller.show_dashboard()
    assert "2026" in capsys.readouterr().out


def test_show_dashboard_shows_empty_messages_when_no_data(controller, capsys):
    controller.show_dashboard()
    out = capsys.readouterr().out
    assert "없습니다" in out


def test_generate_dummy_creates_samples_and_orders(
    controller, sample_svc, order_svc, monkeypatch
):
    inputs = iter(["3", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    controller.generate_dummy()
    assert len(sample_svc.find_all()) == 3
    assert len(order_svc.find_all()) == 5


def test_generate_dummy_shows_success_message(controller, monkeypatch, capsys):
    inputs = iter(["2", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    controller.generate_dummy()
    assert "생성" in capsys.readouterr().out


def test_generate_dummy_shows_error_when_no_samples_for_orders(
    controller, monkeypatch, capsys
):
    inputs = iter(["0", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    controller.generate_dummy()
    assert "오류" in capsys.readouterr().out
