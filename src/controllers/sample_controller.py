from src.services.sample_service import SampleService
from src.views.console_view import ConsoleView


class SampleController:
    def __init__(self, service: SampleService, view: ConsoleView):
        self._service = service
        self._view = view

    def register(self) -> None:
        self._view.print_header("시료 등록")
        try:
            id_ = self._view.prompt("시료 ID: ").strip()
            name = self._view.prompt("시료 이름: ").strip()
            avg_time = float(self._view.prompt("평균 생산시간(시간): "))
            yield_rate = float(self._view.prompt("수율(0.0~1.0): "))
            sample = self._service.register(id_, name, avg_time, yield_rate)
            self._view.print_success(f"시료 등록 완료: [{sample.id}] {sample.name}")
        except ValueError as e:
            self._view.print_error(str(e))

    def list_all(self) -> None:
        samples = self._service.find_all()
        if not samples:
            self._view.print_line("등록된 시료가 없습니다.")
            return
        self._view.print_table(
            ["ID", "이름", "평균생산시간(h)", "수율", "재고"],
            [[s.id, s.name, s.avg_production_time, s.yield_rate, s.stock] for s in samples],
        )

    def search(self) -> None:
        keyword = self._view.prompt("검색어: ").strip()
        results = self._service.search_by_name(keyword)
        if not results:
            self._view.print_line("검색 결과가 없습니다.")
            return
        self._view.print_table(
            ["ID", "이름", "평균생산시간(h)", "수율", "재고"],
            [[s.id, s.name, s.avg_production_time, s.yield_rate, s.stock] for s in results],
        )
