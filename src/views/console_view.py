from rich import box as rich_box
from rich.console import Console
from rich.table import Table

_SEP     = "=" * 60
_DIVIDER = "-" * 60

_BANNER = r"""
 ____   ____    ___
/ ___| / ___| / _ \
\___ \ \___ \| | | |
 ___) | ___) || |_| |
|____/ |____/  \___/
 SampleOrderSystem"""

def _progress_bar(pct: float, width: int = 10) -> str:
    filled = int(width * pct / 100)
    return "█" * filled + "░" * (width - filled) + f" {pct:.1f}%"


_STATUS_STYLES = {
    "RESERVED":  "yellow",
    "PRODUCING": "bright_blue",
    "CONFIRMED": "bright_green",
    "RELEASE":   "cyan",
    "REJECTED":  "red",
}


class ConsoleView:
    def __init__(self):
        self._con = Console(highlight=False)

    def prompt(self, message: str) -> str:
        return input(message)

    def print_line(self, message: str = "") -> None:
        self._con.print(message, markup=False)

    def print_header(self, title: str) -> None:
        self._con.print()
        self._con.rule(f"[bold]{title}[/bold]")

    def print_menu(self, title: str, options: list[tuple[str, str]]) -> None:
        self.print_header(title)
        for key, desc in options:
            self._con.print(f"  [[[bold bright_cyan]{key}[/]]] {desc}")
        self._con.print()

    def print_success(self, message: str) -> None:
        self._con.print(f"[bold green]✓[/] {message}")

    def print_error(self, message: str) -> None:
        self._con.print(f"[bold red]✗ 오류:[/] {message}")

    def print_table(self, headers: list[str], rows: list[list]) -> None:
        table = Table(
            box=rich_box.SIMPLE,
            header_style="bold",
            highlight=False,
            show_edge=False,
        )
        for h in headers:
            table.add_column(h)
        for row in rows:
            table.add_row(*[str(v) for v in row])
        self._con.print(table)

    def print_monitor_dashboard(self, snapshot) -> None:
        self._con.print(_SEP, markup=False)
        self._con.print(
            f" [bold]모니터링 대시보드[/bold]"
            f"              [{snapshot.timestamp}]"
        )
        self._con.print(_SEP, markup=False)

        # ── 시료 현황 ────────────────────────────────────────
        self._con.print()
        self._con.rule("[bold]시료 현황[/bold]")
        if not snapshot.samples:
            self._con.print("  등록된 시료가 없습니다.", markup=False)
        else:
            t = Table(
                box=rich_box.SIMPLE, header_style="bold",
                highlight=False, show_edge=False,
            )
            for col in ["ID", "이름", "평균생산시간(min/ea)", "수율", "재고(ea)"]:
                t.add_column(col)
            for s in snapshot.samples:
                t.add_row(s.id, s.name, str(s.avg_production_time),
                          f"{s.yield_rate:.2f}", str(s.stock))
            self._con.print(t)

        # ── 주문 현황 ─────────────────────────────────────────
        self._con.print()
        self._con.rule("[bold]주문 현황 (상태별)[/bold]")
        if not snapshot.orders_by_status:
            self._con.print("  등록된 주문이 없습니다.", markup=False)
        else:
            for status_val in ["RESERVED", "PRODUCING", "CONFIRMED", "RELEASE"]:
                group = snapshot.orders_by_status.get(status_val, [])
                if not group:
                    continue
                style = _STATUS_STYLES.get(status_val, "white")
                self._con.print(f"\n  [{style}][bold][{status_val}][/bold][/]  {len(group)}건")
                t = Table(
                    box=rich_box.SIMPLE, header_style="bold",
                    highlight=False, show_edge=False,
                )
                for col in ["주문ID", "시료ID", "고객명", "수량"]:
                    t.add_column(col)
                for o in group:
                    t.add_row(o.id, o.sample_id, o.customer_name, str(o.quantity))
                self._con.print(t)

        # ── 생산 현황 (시간 기반) ────────────────────────────────
        self._con.print()
        self._con.rule("[bold]생산 현황[/bold]")
        if not snapshot.production_progress:
            self._con.print("  생산 대기 중인 주문이 없습니다.", markup=False)
        else:
            t = Table(
                box=rich_box.SIMPLE, header_style="bold",
                highlight=False, show_edge=False,
            )
            for col in ["순번", "상태", "주문ID", "시료", "수량",
                        "생산수량", "진행률", "완료예정"]:
                t.add_column(col)
            for i, p in enumerate(snapshot.production_progress):
                o = p["order"]
                status_text = "[bright_blue]진행중[/bright_blue]" \
                    if p["is_active"] else "[dim]대기중[/dim]"
                bar = _progress_bar(p["progress_pct"])
                end_str = p["end_time"].strftime("%H:%M")
                t.add_row(
                    str(i + 1), status_text, o.id,
                    p["sample_name"], str(o.quantity),
                    f"{p['prod_qty']}ea", bar, end_str,
                )
            self._con.print(t)

        self._con.print()
        self._con.print(_DIVIDER, markup=False)

    def print_production_queue(self, progress: list[dict]) -> None:
        t = Table(box=rich_box.SIMPLE, header_style="bold",
                  highlight=False, show_edge=False)
        for col in ["순번", "상태", "주문ID", "고객명", "시료", "수량",
                    "생산수량", "진행률", "완료예정"]:
            t.add_column(col)
        for i, p in enumerate(progress):
            o = p["order"]
            status_text = "[bright_blue]진행중[/bright_blue]" \
                if p["is_active"] else "[dim]대기중[/dim]"
            t.add_row(
                str(i + 1), status_text, o.id,
                o.customer_name, p["sample_name"], str(o.quantity),
                f"{p['prod_qty']}ea",
                _progress_bar(p["progress_pct"]),
                p["end_time"].strftime("%H:%M"),
            )
        self._con.print(t)

    def print_order_monitor(self, snapshot) -> None:
        self._con.print(_SEP, markup=False)
        self._con.print(f" [bold]주문량 현황[/bold]              [{snapshot.timestamp}]")
        self._con.print(_SEP, markup=False)

        if not snapshot.orders_by_status:
            self._con.print("\n  데이터가 존재하지 않습니다.", markup=False)
        else:
            for status_val in ["RESERVED", "PRODUCING", "CONFIRMED", "RELEASE"]:
                group = snapshot.orders_by_status.get(status_val, [])
                style = _STATUS_STYLES.get(status_val, "white")
                self._con.print(
                    f"\n  [{style}][bold][{status_val}][/bold][/]  {len(group)}건"
                )
                if group:
                    t = Table(box=rich_box.SIMPLE, header_style="bold",
                              highlight=False, show_edge=False)
                    for col in ["주문ID", "시료ID", "고객명", "수량"]:
                        t.add_column(col)
                    for o in group:
                        t.add_row(o.id, o.sample_id, o.customer_name, str(o.quantity))
                    self._con.print(t)

        self._con.print()
        self._con.print(_DIVIDER, markup=False)

    def print_stock_monitor(self, snapshot) -> None:
        self._con.print(_SEP, markup=False)
        self._con.print(f" [bold]재고량 현황[/bold]              [{snapshot.timestamp}]")
        self._con.print(_SEP, markup=False)

        if not snapshot.stock_health:
            self._con.print("\n  데이터가 존재하지 않습니다.", markup=False)
        else:
            t = Table(box=rich_box.SIMPLE, header_style="bold",
                      highlight=False, show_edge=False)
            for col in ["ID", "이름", "재고(ea)", "수요(ea)", "잔여율", "상태"]:
                t.add_column(col)
            for h in snapshot.stock_health:
                s      = h["sample"]
                status = h["status"]
                pct    = f"{h['remaining_pct']:.1f}%"
                bar    = _progress_bar(h["remaining_pct"])
                style  = {"여유": "bright_green", "부족": "yellow", "고갈": "bold red"}[status]
                t.add_row(
                    s.id, s.name, str(s.stock), str(h["demand"]),
                    bar, f"[{style}]{status}[/]",
                )
            self._con.print(t)

        self._con.print()
        self._con.print(_DIVIDER, markup=False)

    def print_main_page(self, sample_count: int, total_stock: int,
                        order_count: int, producing_count: int, now: str) -> None:
        self._con.print(_SEP, markup=False)
        for line in _BANNER.strip().split("\n"):
            self._con.print(line.center(60), markup=False)
        self._con.print(f"{'반도체 시료 생산주문관리 시스템':^60}", markup=False)
        self._con.print(_SEP, markup=False)
        self._con.print(f" 시스템 현황  {now}", markup=False)
        self._con.print()
        self._con.print(
            f" 등록 시료 [bold]{sample_count:3d}[/bold]종"
            f"      총 재고 [bold]{total_stock:6,d}[/bold] ea"
        )
        self._con.print(
            f" 전체 주문 [bold]{order_count:3d}[/bold]건"
            f"  생산라인 [bold yellow]{producing_count:4d}[/bold yellow]건 대기"
        )
        self._con.print(_DIVIDER, markup=False)
        self._con.print()
        self._con.print(" [1] 시료 관리               [2] 시료 주문", markup=False)
        self._con.print(" [3] 주문 승인/거절           [4] 모니터링", markup=False)
        self._con.print(" [5] 생산라인 조회            [6] 출고 처리", markup=False)
        self._con.print(" [0] 종료", markup=False)
        self._con.print()
        self._con.print(_DIVIDER, markup=False)

