import pytest
from src.models.sample import Sample
from src.repositories.sample_repository import SampleRepository
from src.services.sample_service import SampleService


@pytest.fixture
def service(tmp_path):
    return SampleService(SampleRepository(str(tmp_path / "samples.json")))


def test_register_creates_sample_with_zero_stock(service):
    sample = service.register(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9)
    assert sample.id == "S001"
    assert sample.name == "GaN"
    assert sample.stock == 0


def test_register_persists_sample(service):
    service.register(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9)
    found = service.find_by_id("S001")
    assert found.name == "GaN"


def test_register_raises_if_id_already_exists(service):
    service.register(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9)
    with pytest.raises(ValueError, match="이미 존재하는 시료 ID"):
        service.register(id="S001", name="SiC", avg_production_time=3.0, yield_rate=0.85)


def test_find_all_returns_all_registered_samples(service):
    service.register(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9)
    service.register(id="S002", name="SiC", avg_production_time=3.0, yield_rate=0.85)
    assert len(service.find_all()) == 2


def test_find_by_id_returns_sample(service):
    service.register(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9)
    sample = service.find_by_id("S001")
    assert sample.id == "S001"


def test_find_by_id_raises_if_not_found(service):
    with pytest.raises(ValueError, match="존재하지 않는 시료"):
        service.find_by_id("NONE")


def test_search_by_name_returns_matching_samples(service):
    service.register(id="S001", name="GaN wafer", avg_production_time=2.5, yield_rate=0.9)
    service.register(id="S002", name="SiC", avg_production_time=3.0, yield_rate=0.85)
    results = service.search_by_name("GaN")
    assert len(results) == 1
    assert results[0].id == "S001"


def test_search_by_name_returns_empty_if_no_match(service):
    service.register(id="S001", name="GaN", avg_production_time=2.5, yield_rate=0.9)
    assert service.search_by_name("SiC") == []
