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
    inputs = iter(["S001", "GaN", "2.5", "0.9"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    controller.register()
    assert service.find_by_id("S001").name == "GaN"


def test_register_shows_error_on_duplicate(controller, service, monkeypatch, capsys):
    service.register("S001", "GaN", 2.5, 0.9)
    inputs = iter(["S001", "SiC", "3.0", "0.85"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    controller.register()
    assert "오류" in capsys.readouterr().out


def test_list_all_displays_all_samples(controller, service, capsys):
    service.register("S001", "GaN", 2.5, 0.9)
    service.register("S002", "SiC", 3.0, 0.85)
    controller.list_all()
    output = capsys.readouterr().out
    assert "GaN" in output
    assert "SiC" in output


def test_list_all_shows_empty_message_when_no_samples(controller, capsys):
    controller.list_all()
    assert "없습니다" in capsys.readouterr().out


def test_search_displays_matching_sample(controller, service, monkeypatch, capsys):
    service.register("S001", "GaN wafer", 2.5, 0.9)
    service.register("S002", "SiC", 3.0, 0.85)
    monkeypatch.setattr("builtins.input", lambda _: "GaN")
    controller.search()
    output = capsys.readouterr().out
    assert "GaN" in output
    assert "SiC" not in output


def test_search_shows_empty_message_when_no_match(controller, service, monkeypatch, capsys):
    service.register("S001", "GaN", 2.5, 0.9)
    monkeypatch.setattr("builtins.input", lambda _: "SiC")
    controller.search()
    assert "없습니다" in capsys.readouterr().out
