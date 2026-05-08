from src.models.order import OrderStatus
from src.services.order_service import OrderService
from src.services.production_service import ProductionService
from src.views.console_view import ConsoleView


class ProductionController:
    def __init__(self, production_service: ProductionService,
                 order_service: OrderService, view: ConsoleView):
        self._prod_svc = production_service
        self._order_svc = order_service
        self._view = view

    def complete_production(self) -> None:
        try:
            order = self._prod_svc.complete_production()
            self._view.print_success(f"생산 완료: 주문 {order.id} → CONFIRMED")
        except ValueError as e:
            self._view.print_error(str(e))

    def release(self) -> None:
        order_id = self._view.prompt("출고할 주문 ID: ").strip()
        try:
            order = self._prod_svc.release(order_id)
            self._view.print_success(f"출고 완료: {order.id} → RELEASE")
        except ValueError as e:
            self._view.print_error(str(e))

    def list_queue(self) -> None:
        orders = self._order_svc.find_by_status(OrderStatus.PRODUCING)
        if not orders:
            self._view.print_line("생산 중인 주문이 없습니다.")
            return
        self._view.print_table(
            ["주문ID", "시료ID", "고객명", "수량", "주문일시"],
            [[o.id, o.sample_id, o.customer_name, o.quantity,
              o.created_at[:19]] for o in orders],
        )
