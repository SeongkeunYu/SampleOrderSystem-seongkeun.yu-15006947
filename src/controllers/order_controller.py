from src.services.order_service import OrderService
from src.views.console_view import ConsoleView


class OrderController:
    def __init__(self, service: OrderService, view: ConsoleView):
        self._service = service
        self._view = view

    def create(self) -> None:
        self._view.print_header("주문 생성")
        try:
            sample_id = self._view.prompt("시료 ID: ").strip()
            customer = self._view.prompt("고객명: ").strip()
            qty = int(self._view.prompt("주문 수량: "))
            order = self._service.create(sample_id, customer, qty)
            self._view.print_success(f"주문 등록 완료: {order.id}")
        except ValueError as e:
            self._view.print_error(str(e))

    def approve(self) -> None:
        order_id = self._view.prompt("승인할 주문 ID: ").strip()
        try:
            order = self._service.approve(order_id)
            self._view.print_success(f"승인 완료: {order.id} → {order.status.value}")
        except ValueError as e:
            self._view.print_error(str(e))

    def reject(self) -> None:
        order_id = self._view.prompt("거절할 주문 ID: ").strip()
        try:
            order = self._service.reject(order_id)
            self._view.print_success(f"거절 완료: {order.id} → {order.status.value}")
        except ValueError as e:
            self._view.print_error(str(e))

    def list_all(self) -> None:
        orders = self._service.find_all()
        if not orders:
            self._view.print_line("등록된 주문이 없습니다.")
            return
        self._view.print_table(
            ["주문ID", "시료ID", "고객명", "수량", "상태", "주문일시"],
            [[o.id[:8], o.sample_id, o.customer_name, o.quantity,
              o.status.value, o.created_at[:19]] for o in orders],
        )
