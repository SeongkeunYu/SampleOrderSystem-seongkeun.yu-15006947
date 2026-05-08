import pytest
from src.repositories.sample_repository import SampleRepository
from src.services.sample_service import SampleService
from src.views.console_view import ConsoleView
from src.controllers.sample_controller import SampleController


@pytest.fixture
def service(tmp_path):
    return SampleService(SampleRepository(str(tmp_path / "samples.json")))


@pytest.fixture
def controller(service):
    return SampleController(service, ConsoleView())


def test_register_persists_sample_from_input(controller, service, monkeypatch):
    inputs = iter(["GaN", "2.5", "0.9"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    controller.register()
    sample = service.find_all()[0]
    assert sample.id == "S-001"
    assert sample.name == "GaN"


def test_register_shows_generated_id_in_success_message(controller, monkeypatch, capsys):
    inputs = iter(["GaN", "2.5", "0.9"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    controller.register()
    assert "S-001" in capsys.readouterr().out


def test_list_all_displays_all_samples(controller, service, capsys):
    service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    service.register(name="SiC", avg_production_time=3.0, yield_rate=0.85)
    controller.list_all()
    output = capsys.readouterr().out
    assert "GaN" in output
    assert "SiC" in output


def test_list_all_shows_empty_message_when_no_samples(controller, capsys):
    controller.list_all()
    assert "없습니다" in capsys.readouterr().out


def test_search_displays_matching_sample(controller, service, monkeypatch, capsys):
    service.register(name="GaN wafer", avg_production_time=2.5, yield_rate=0.9)
    service.register(name="SiC", avg_production_time=3.0, yield_rate=0.85)
    monkeypatch.setattr("builtins.input", lambda _: "GaN")
    controller.search()
    output = capsys.readouterr().out
    assert "GaN" in output
    assert "SiC" not in output


def test_search_shows_empty_message_when_no_match(controller, service, monkeypatch, capsys):
    service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    monkeypatch.setattr("builtins.input", lambda _: "SiC")
    controller.search()
    assert "없습니다" in capsys.readouterr().out
