_SEP     = "=" * 60
_DIVIDER = "-" * 60

_BANNER = r"""
  ____                      _
 / ___|  __ _ _ __ ___  _ _| | ___
 \___ \ / _` | '_ ` _ \| '_ \/ _ \
  ___) | (_| | | | | | | |_) | __/
 |____/ \__,_|_| |_| |_| .__/ \___|
  ___          _        |_|
 / _ \ _ __ __| | ___ _ __
| | | | '__/ _` |/ _ \ '__|
| |_| | | | (_| |  __/ |
 \___/|_|  \__,_|\___|_|
  ____            _
 / ___| _   _ ___| |_ ___ _ __ ___
 \___ \| | | / __| __/ _ \ '_ ` _ \
  ___) | |_| \__ \ ||  __/ | | | | |
 |____/ \__, |___/\__\___|_| |_| |_|
        |___/                       """


class ConsoleView:
    def prompt(self, message: str) -> str:
        return input(message)

    def print_line(self, message: str = "") -> None:
        print(message)

    def print_header(self, title: str) -> None:
        print(f"\n{'=' * 42}")
        print(f"  {title}")
        print(f"{'=' * 42}")

    def print_menu(self, title: str, options: list[tuple[str, str]]) -> None:
        self.print_header(title)
        for key, desc in options:
            print(f"  [{key}] {desc}")
        print()

    def print_success(self, message: str) -> None:
        print(f"✓ {message}")

    def print_error(self, message: str) -> None:
        print(f"✗ 오류: {message}")

    def print_table(self, headers: list[str], rows: list[list]) -> None:
        widths = [
            max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
            for i, h in enumerate(headers)
        ]
        header_str = " | ".join(str(h).ljust(w) for h, w in zip(headers, widths))
        separator = "-+-".join("-" * w for w in widths)
        print(header_str)
        print(separator)
        for row in rows:
            print(" | ".join(str(v).ljust(w) for v, w in zip(row, widths)))

    def print_main_page(self, sample_count: int, total_stock: int,
                        order_count: int, producing_count: int, now: str) -> None:
        print(_SEP)
        print(_BANNER)
        print(f"{'반도체 시료 생산주문관리 시스템':^60}")
        print(_SEP)
        print(f" 시스템 현황  {now}")
        print()
        print(f" 등록 시료 {sample_count:3d}종      총 재고 {total_stock:6,d} ea")
        print(f" 전체 주문 {order_count:3d}건  생산라인 {producing_count:4d}건 대기")
        print(_DIVIDER)
        print()
        print(" [1] 시료 관리               [2] 시료 주문")
        print(" [3] 주문 승인/거절           [4] 모니터링")
        print(" [5] 생산라인 조회            [6] 출고 처리")
        print(" [0] 종료")
        print()
        print(_DIVIDER)

    def print_monitor_dashboard(self, snapshot) -> None:
        print(_SEP)
        print(f" 모니터링 대시보드              [{snapshot.timestamp}]")
        print(_SEP)

        print()
        print(" ── 시료 현황 " + "─" * 46)
        if not snapshot.samples:
            print("  등록된 시료가 없습니다.")
        else:
            self.print_table(
                ["ID", "이름", "평균생산시간(min/ea)", "수율", "재고(ea)"],
                [[s.id, s.name, s.avg_production_time, f"{s.yield_rate:.2f}", s.stock]
                 for s in snapshot.samples],
            )

        print()
        print(" ── 주문 현황 (상태별) " + "─" * 38)
        if not snapshot.orders_by_status:
            print("  등록된 주문이 없습니다.")
        else:
            for status_val in ["RESERVED", "PRODUCING", "CONFIRMED", "RELEASE", "REJECTED"]:
                group = snapshot.orders_by_status.get(status_val, [])
                if group:
                    print(f"\n  [{status_val}]  {len(group)}건")
                    self.print_table(
                        ["주문ID", "시료ID", "고객명", "수량"],
                        [[o.id[:8], o.sample_id, o.customer_name, o.quantity]
                         for o in group],
                    )

        print()
        print(" ── 생산 대기 큐 (FIFO 순서) " + "─" * 31)
        if not snapshot.production_queue:
            print("  생산 대기 중인 주문이 없습니다.")
        else:
            self.print_table(
                ["순번", "주문ID", "시료ID", "고객명", "수량"],
                [[i + 1, o.id[:8], o.sample_id, o.customer_name, o.quantity]
                 for i, o in enumerate(snapshot.production_queue)],
            )

        print()
        print(_DIVIDER)

    def print_summary(self, sample_count: int, total_stock: int,
                      order_count: int, producing_count: int) -> None:
        self.print_header("시스템 현황 요약")
        print(f"  시료 종수      : {sample_count}종")
        print(f"  총 재고량      : {total_stock:,}개")
        print(f"  전체 주문 건수 : {order_count}건")
        print(f"  생산라인 대기  : {producing_count}건")
