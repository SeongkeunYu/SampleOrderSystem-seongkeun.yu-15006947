# 리팩토링 계획서 (REFACT_PLAN.md)

## 개요

전체 프로젝트 점검을 통해 도출된 4가지 개선 항목을 우선순위 순서로 정리한다.  
각 항목은 독립적으로 진행 가능하며, 변경 후 전체 테스트(105개)가 통과해야 한다.

---

## Item 1 — `approve()` / `reject()` 빈 목록 시 조기 반환 🔴

### 문제
`_show_reserved_orders()`가 내부적으로 `return`해도 호출한 `approve()` / `reject()`는
계속 실행되어 주문 ID 프롬프트가 나타난다.  
`release()`는 이미 동일 패턴으로 수정됐으나 두 메서드는 미처리 상태다.

### 현재 코드 (`order_controller.py`)
```python
def approve(self) -> None:
    self._show_reserved_orders()           # 빈 경우 내부에서 return
    order_id = self._view.prompt(...)      # ← 그래도 실행됨 (버그)
    ...
```

### 개선 방향
`_show_reserved_orders()`를 목록을 **반환**하는 함수로 변경하고,
`approve()` / `reject()` 에서 빈 경우 직접 조기 반환한다.

```python
def approve(self) -> None:
    orders = self._get_reserved_orders()
    if not orders:
        self._view.print_line("  접수 대기 중인 주문이 없습니다.")
        return
    self._view.print_table(...)
    order_id = self._view.prompt(...)
    ...
```

### 영향 파일
- `src/controllers/order_controller.py`
- `tests/test_order_controller.py` (approve/reject 빈 목록 테스트 추가)

---

## Item 2 — `MonitorSnapshot.production_queue` Dead Field 제거 🟡

### 문제
`production_queue: list[Order]` 필드는 `Monitor.get_snapshot()`에서 매번 생성되지만,
어떤 Controller나 View도 이 필드를 읽지 않는다.

| 사용처 | 실제 사용 여부 |
|---|---|
| `print_monitor_dashboard()` | `production_progress` 사용 |
| `ProductionController.list_queue()` | `get_production_progress()` 직접 호출 |
| `MonitorSnapshot.production_queue` | **아무도 읽지 않음** |

### 개선 방향
- `MonitorSnapshot`에서 `production_queue` 필드 제거
- `Monitor.get_snapshot()`에서 관련 계산 코드 제거
- `tests/test_monitor.py`에서 `production_queue` 관련 테스트 제거 또는 대체

### 영향 파일
- `tools/monitor.py`
- `tests/test_monitor.py`

---

## Item 3 — `MonitorController.show_dashboard()` Dead Method 제거 🟡

### 문제
`show_dashboard()`는 전체 대시보드를 출력하는 메서드이나,
`_monitor_menu()`에서 호출되지 않는다.  
현재 메뉴는 `show_order_monitor()` / `show_stock_monitor()`만 사용한다.

```python
# src/main.py _monitor_menu() — show_dashboard 호출 없음
elif choice == "1": ctrl.show_order_monitor()
elif choice == "2": ctrl.show_stock_monitor()
```

`ConsoleView.print_monitor_dashboard()`도 `show_dashboard()`를 통해서만 호출되므로
함께 제거 대상이 된다.

### 개선 방향
- `MonitorController.show_dashboard()` 제거
- `ConsoleView.print_monitor_dashboard()` 제거
- `tests/test_monitor_controller.py`에서 `show_dashboard` 관련 테스트 3개 제거

### 영향 파일
- `src/controllers/monitor_controller.py`
- `src/views/console_view.py`
- `tests/test_monitor_controller.py`

---

## Item 4 — FIFO 스케줄 계산 헬퍼 추출 🟠

### 문제
`auto_complete_productions()`와 `get_production_progress()` 두 메서드가
동일한 FIFO 타임라인 계산 로직을 반복한다.

```python
# 두 메서드에서 동일하게 반복
for order in producing:
    sample   = self._sample_repo.find_by_id(order.sample_id)
    prod_qty = math.ceil(order.quantity / (sample.yield_rate * 0.9))
    duration = timedelta(minutes=prod_qty * sample.avg_production_time)
    start    = max(datetime.fromisoformat(order.created_at), prev_end) \
               if prev_end else datetime.fromisoformat(order.created_at)
    end      = start + duration
    prev_end = end
```

### 개선 방향
`_build_schedule()` private 메서드를 추출해 두 메서드가 공유한다.

```python
def _build_schedule(self, producing: list[Order]) -> list[tuple]:
    """FIFO 순서로 (order, sample, prod_qty, start, end) 튜플 목록을 반환한다."""
    result = []
    prev_end = None
    for order in producing:
        sample   = self._sample_repo.find_by_id(order.sample_id)
        prod_qty = math.ceil(order.quantity / (sample.yield_rate * 0.9))
        duration = timedelta(minutes=prod_qty * sample.avg_production_time)
        start    = max(datetime.fromisoformat(order.created_at), prev_end) \
                   if prev_end else datetime.fromisoformat(order.created_at)
        end      = start + duration
        prev_end = end
        result.append((order, sample, prod_qty, start, end))
    return result
```

`auto_complete_productions()`와 `get_production_progress()`는 이 목록을 받아
각자의 로직(시간 비교 / 진행률 계산)만 수행한다.

### 영향 파일
- `src/services/production_service.py`
- `tests/test_production_service.py` (기존 테스트 그대로 통과 확인)

---

## 실행 순서

```
Item 1 → Item 2 → Item 3 → Item 4
```

각 Item 완료 후 `python -m pytest tests/ -q` 로 전체 테스트 통과를 확인한다.

## 완료 기준

- [x] Item 1: approve/reject 빈 목록 → 즉시 반환
- [x] Item 2: production_queue 필드 제거
- [x] Item 3: show_dashboard 제거
- [x] Item 4: FIFO 스케줄 헬퍼 추출
- [x] 전체 테스트 통과 (103 passed)
