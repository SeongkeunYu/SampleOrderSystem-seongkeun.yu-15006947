import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

from src.controllers.order_controller import OrderController
from src.controllers.production_controller import ProductionController
from src.controllers.sample_controller import SampleController
from src.models.order import OrderStatus
from src.repositories.order_repository import OrderRepository
from src.repositories.sample_repository import SampleRepository
from src.services.order_service import OrderService
from src.services.production_service import ProductionService
from src.services.sample_service import SampleService
from src.views.console_view import ConsoleView

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def build_app(data_dir: str = DATA_DIR):
    os.makedirs(data_dir, exist_ok=True)
    sample_repo = SampleRepository(os.path.join(data_dir, "samples.json"))
    order_repo  = OrderRepository(os.path.join(data_dir, "orders.json"))
    sample_svc  = SampleService(sample_repo)
    order_svc   = OrderService(order_repo, sample_repo)
    prod_svc    = ProductionService(order_repo, sample_repo)
    view        = ConsoleView()
    return (
        sample_svc, order_svc, prod_svc,
        SampleController(sample_svc, view),
        OrderController(order_svc, view),
        ProductionController(prod_svc, order_svc, view),
        view,
    )


def _show_main_page(sample_svc, order_svc, view):
    samples   = sample_svc.find_all()
    orders    = order_svc.find_all()
    producing = order_svc.find_by_status(OrderStatus.PRODUCING)
    view.print_main_page(
        sample_count   = len(samples),
        total_stock    = sum(s.stock for s in samples),
        order_count    = len(orders),
        producing_count= len(producing),
        now            = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


# ── [1] 시료 관리 ──────────────────────────────────────────────
def _sample_menu(ctrl: SampleController, view: ConsoleView) -> None:
    while True:
        view.print_menu("시료 관리", [
            ("1", "시료 등록"),
            ("2", "전체 시료 조회"),
            ("3", "시료 검색"),
            ("0", "뒤로"),
        ])
        choice = view.prompt(" 선택 > ").strip()
        if choice == "0":
            break
        elif choice == "1":
            ctrl.register()
        elif choice == "2":
            ctrl.list_all()
        elif choice == "3":
            ctrl.search()
        else:
            view.print_error("올바른 메뉴를 선택하세요.")


# ── [3] 주문 승인/거절 ─────────────────────────────────────────
def _approve_menu(ctrl: OrderController, view: ConsoleView) -> None:
    while True:
        view.print_menu("주문 승인/거절", [
            ("1", "접수 주문 목록 조회"),
            ("2", "주문 승인"),
            ("3", "주문 거절"),
            ("0", "뒤로"),
        ])
        choice = view.prompt(" 선택 > ").strip()
        if choice == "0":
            break
        elif choice == "1":
            ctrl.list_all()
        elif choice == "2":
            ctrl.approve()
        elif choice == "3":
            ctrl.reject()
        else:
            view.print_error("올바른 메뉴를 선택하세요.")


# ── [5] 생산라인 조회 ──────────────────────────────────────────
def _production_menu(ctrl: ProductionController, view: ConsoleView) -> None:
    while True:
        view.print_menu("생산라인 조회", [
            ("1", "생산 대기 목록 조회"),
            ("2", "생산 완료 처리 (FIFO)"),
            ("0", "뒤로"),
        ])
        choice = view.prompt(" 선택 > ").strip()
        if choice == "0":
            break
        elif choice == "1":
            ctrl.list_queue()
        elif choice == "2":
            ctrl.complete_production()
        else:
            view.print_error("올바른 메뉴를 선택하세요.")


def main():
    sample_svc, order_svc, _, sample_ctrl, order_ctrl, prod_ctrl, view = build_app()

    while True:
        _show_main_page(sample_svc, order_svc, view)
        choice = view.prompt(" 선택 > ").strip()

        if choice == "0":
            view.print_line("\n 시스템을 종료합니다.")
            break
        elif choice == "1":
            _sample_menu(sample_ctrl, view)
        elif choice == "2":                          # 시료 주문
            order_ctrl.create()
        elif choice == "3":                          # 주문 승인/거절
            _approve_menu(order_ctrl, view)
        elif choice == "4":                          # 모니터링 (Phase 4)
            view.print_line("\n  [모니터링] Phase 4에서 구현됩니다.")
            view.prompt("  엔터를 눌러 계속...")
        elif choice == "5":                          # 생산라인 조회
            _production_menu(prod_ctrl, view)
        elif choice == "6":                          # 출고 처리
            prod_ctrl.release()
        else:
            view.print_error("올바른 메뉴를 선택하세요.")


if __name__ == "__main__":
    main()
