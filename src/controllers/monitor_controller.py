from tools.monitor import Monitor
from src.views.console_view import ConsoleView


class MonitorController:
    def __init__(self, monitor: Monitor, view: ConsoleView):
        self._monitor = monitor
        self._view    = view

    def show_dashboard(self) -> None:
        snapshot = self._monitor.get_snapshot()
        self._view.print_monitor_dashboard(snapshot)

    def show_order_monitor(self) -> None:
        snapshot = self._monitor.get_snapshot()
        self._view.print_order_monitor(snapshot)

    def show_stock_monitor(self) -> None:
        snapshot = self._monitor.get_snapshot()
        self._view.print_stock_monitor(snapshot)
