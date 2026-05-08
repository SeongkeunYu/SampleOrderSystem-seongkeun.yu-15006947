from tools.monitor import Monitor
from tools.dummy_generator import DummyGenerator
from src.views.console_view import ConsoleView


class MonitorController:
    def __init__(self, monitor: Monitor, generator: DummyGenerator, view: ConsoleView):
        self._monitor   = monitor
        self._generator = generator
        self._view      = view

    def show_dashboard(self) -> None:
        snapshot = self._monitor.get_snapshot()
        self._view.print_monitor_dashboard(snapshot)

    def generate_dummy(self) -> None:
        try:
            n_samples = int(self._view.prompt("생성할 시료 수: "))
            n_orders  = int(self._view.prompt("생성할 주문 수: "))
            if n_samples > 0:
                self._generator.generate_samples(n_samples)
            if n_orders > 0:
                self._generator.generate_orders(n_orders)
            self._view.print_success(
                f"시료 {n_samples}종, 주문 {n_orders}건 생성 완료"
            )
        except ValueError as e:
            self._view.print_error(str(e))
