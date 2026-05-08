import pytest
from src.repositories.sample_repository import SampleRepository
from src.services.sample_service import SampleService


@pytest.fixture
def service(tmp_path):
    return SampleService(SampleRepository(str(tmp_path / "samples.json")))


def test_register_assigns_s001_to_first_sample(service):
    sample = service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    assert sample.id == "S-001"


def test_register_assigns_next_sequential_id(service):
    service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    sample2 = service.register(name="SiC", avg_production_time=3.0, yield_rate=0.85)
    assert sample2.id == "S-002"


def test_register_uses_max_id_plus_one(service):
    service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    service.register(name="SiC", avg_production_time=3.0, yield_rate=0.85)
    sample3 = service.register(name="InP", avg_production_time=1.5, yield_rate=0.95)
    assert sample3.id == "S-003"


def test_register_creates_sample_with_zero_stock(service):
    sample = service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    assert sample.name == "GaN"
    assert sample.stock == 0


def test_register_persists_sample(service):
    sample = service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    found = service.find_by_id(sample.id)
    assert found.name == "GaN"


def test_find_all_returns_all_registered_samples(service):
    service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    service.register(name="SiC", avg_production_time=3.0, yield_rate=0.85)
    assert len(service.find_all()) == 2


def test_find_by_id_returns_sample(service):
    registered = service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    sample = service.find_by_id(registered.id)
    assert sample.id == registered.id


def test_find_by_id_raises_if_not_found(service):
    with pytest.raises(ValueError, match="존재하지 않는 시료"):
        service.find_by_id("NONE")


def test_search_by_name_returns_matching_samples(service):
    s1 = service.register(name="GaN wafer", avg_production_time=2.5, yield_rate=0.9)
    service.register(name="SiC", avg_production_time=3.0, yield_rate=0.85)
    results = service.search_by_name("GaN")
    assert len(results) == 1
    assert results[0].id == s1.id


def test_search_by_name_returns_empty_if_no_match(service):
    service.register(name="GaN", avg_production_time=2.5, yield_rate=0.9)
    assert service.search_by_name("SiC") == []
