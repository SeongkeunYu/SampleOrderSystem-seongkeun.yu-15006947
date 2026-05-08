from src.models.order import OrderStatus
from src.services.order_service import OrderService
from src.views.console_view import ConsoleView

_COMPLETED_STATUSES = {
    OrderStatus.PRODUCING, OrderStatus.CONFIRMED,
    OrderStatus.RELEASE, OrderStatus.REJECTED,
}


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
        self._show_reserved_orders()
        order_id = self._view.prompt("승인할 주문 ID: ").strip()
        try:
            order = self._service.approve(order_id)
            self._view.print_success(f"승인 완료: {order.id} → {order.status.value}")
        except ValueError as e:
            self._view.print_error(str(e))

    def reject(self) -> None:
        self._show_reserved_orders()
        order_id = self._view.prompt("거절할 주문 ID: ").strip()
        try:
            order = self._service.reject(order_id)
            self._view.print_success(f"거절 완료: {order.id} → {order.status.value}")
        except ValueError as e:
            self._view.print_error(str(e))

    def list_all(self) -> None:
        self._show_order_groups()

    def _show_reserved_orders(self) -> None:
        orders = _sort_desc(
            self._service.find_by_status(OrderStatus.RESERVED)
        )
        if not orders:
            self._view.print_line("  접수 대기 중인 주문이 없습니다.")
            return
        self._view.print_table(
            ["주문ID", "시료ID", "고객명", "수량", "주문일시"],
            [[o.id, o.sample_id, o.customer_name, o.quantity, o.created_at[:19]]
             for o in orders],
        )

    def _show_order_groups(self) -> None:
        all_orders = self._service.find_all()
        reserved  = _sort_desc([o for o in all_orders if o.status == OrderStatus.RESERVED])
        completed = _sort_desc([o for o in all_orders if o.status in _COMPLETED_STATUSES])

        self._view.print_header("접수 대상 (RESERVED)")
        if not reserved:
            self._view.print_line("  접수 대기 중인 주문이 없습니다.")
        else:
            self._view.print_table(
                ["주문ID", "시료ID", "고객명", "수량", "주문일시"],
                [[o.id, o.sample_id, o.customer_name, o.quantity, o.created_at[:19]]
                 for o in reserved],
            )

        self._view.print_header("접수 완료 (PRODUCING / CONFIRMED / RELEASE / REJECTED)")
        if not completed:
            self._view.print_line("  처리된 주문이 없습니다.")
        else:
            self._view.print_table(
                ["주문ID", "시료ID", "고객명", "수량", "상태", "주문일시"],
                [[o.id, o.sample_id, o.customer_name, o.quantity,
                  o.status.value, o.created_at[:19]]
                 for o in completed],
            )


def _sort_desc(orders: list) -> list:
    return sorted(orders, key=lambda o: o.created_at, reverse=True)
