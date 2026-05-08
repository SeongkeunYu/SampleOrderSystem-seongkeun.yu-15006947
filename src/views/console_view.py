class ConsoleView:
    def prompt(self, message: str) -> str:
        return input(message)

    def print_line(self, message: str = "") -> None:
        print(message)

    def print_header(self, title: str) -> None:
        width = 42
        print(f"\n{'=' * width}")
        print(f"  {title}")
        print(f"{'=' * width}")

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

    def print_summary(self, sample_count: int, total_stock: int,
                      order_count: int, producing_count: int) -> None:
        self.print_header("시스템 현황 요약")
        print(f"  시료 종수      : {sample_count}종")
        print(f"  총 재고량      : {total_stock:,}개")
        print(f"  전체 주문 건수 : {order_count}건")
        print(f"  생산라인 대기  : {producing_count}건")
