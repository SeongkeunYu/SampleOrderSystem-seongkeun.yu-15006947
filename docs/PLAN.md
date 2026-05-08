# 개발 계획서: 반도체 시료 생산주문관리 시스템

## 1. 개발 방향

- **아키텍처**: MVC 패턴 (Model / Service / Controller 계층 분리)
- **인터페이스**: 콘솔(CLI) 기반
- **데이터 영속성**: JSON 파일 기반 저장 (추후 DB 교체 가능하도록 Repository 패턴 적용)
- **개발 방법론**: TDD (Red-Green-Refactor), Agentic Engineering
- **테스트 프레임워크**: pytest

---

## 2. 디렉토리 구조

```
SampleOrderSystem/
├── src/
│   ├── models/
│   │   ├── sample.py          # 시료 도메인 모델
│   │   └── order.py           # 주문 도메인 모델 (OrderStatus Enum 포함)
│   ├── repositories/
│   │   ├── base.py            # Repository 추상 인터페이스
│   │   ├── sample_repository.py
│   │   └── order_repository.py
│   ├── services/
│   │   ├── sample_service.py  # 시료 등록/조회 비즈니스 로직
│   │   ├── order_service.py   # 주문 생성/승인/거절 비즈니스 로직
│   │   └── production_service.py  # 생산라인 및 출고 로직
│   ├── controllers/
│   │   ├── sample_controller.py
│   │   ├── order_controller.py
│   │   └── production_controller.py
│   ├── views/
│   │   └── console_view.py    # 콘솔 입출력 처리
│   ├── data/                  # JSON 데이터 저장 디렉토리
│   │   ├── samples.json
│   │   └── orders.json
│   └── main.py                # 진입점, 메인 메뉴
├── tests/
│   ├── test_sample_service.py
│   ├── test_order_service.py
│   └── test_production_service.py
├── tools/
│   ├── monitor.py             # 실시간 데이터 조회 도구
│   └── dummy_generator.py     # 테스트 데이터 생성 도구
└── requirements.txt
```

---

## 3. 도메인 모델

### Sample (시료)

| 필드 | 타입 | 설명 |
| :--- | :--- | :--- |
| `id` | str | 시료 고유 ID |
| `name` | str | 시료 이름 |
| `avg_production_time` | float | 평균 생산시간 (시간 단위) |
| `yield_rate` | float | 수율 (0.0 ~ 1.0) |
| `stock` | int | 현재 재고 수량 |

### Order (주문)

| 필드 | 타입 | 설명 |
| :--- | :--- | :--- |
| `id` | str | 주문 고유 ID |
| `sample_id` | str | 주문 시료 ID |
| `customer_name` | str | 고객명 |
| `quantity` | int | 주문 수량 |
| `status` | OrderStatus | 주문 상태 |
| `created_at` | str | 주문 생성 일시 |

### OrderStatus (주문 상태 Enum)

```
RESERVED   → 주문 접수
REJECTED   → 주문 거절
PRODUCING  → 생산 중 (재고 부족)
CONFIRMED  → 출고 대기
RELEASE    → 출고 완료
```

---

## 4. 핵심 비즈니스 로직

### 승인 처리 흐름

```
승인 요청 (RESERVED 주문)
    ├── 재고 >= 주문 수량  →  재고 차감 후 CONFIRMED
    └── 재고 < 주문 수량   →  부족분 생산 등록 후 PRODUCING
                               실 생산량 = ceil(부족분 / (수율 * 0.9))
```

### 생산라인 처리 흐름

```
생산 완료 이벤트
    →  PRODUCING 주문 중 가장 오래된 것 선택 (FIFO)
    →  재고 확보 후 CONFIRMED 상태로 전환
```

---

## 5. 개발 단계 (Phase)

### Phase 1 — 도메인 모델 및 영속성 계층

**목표**: 핵심 데이터 구조와 JSON 기반 저장소 구축

| 작업 | 산출물 |
| :--- | :--- |
| `OrderStatus` Enum 정의 | `models/order.py` |
| `Sample`, `Order` 데이터 클래스 정의 | `models/sample.py`, `models/order.py` |
| Repository 추상 인터페이스 정의 | `repositories/base.py` |
| JSON 기반 `SampleRepository` 구현 | `repositories/sample_repository.py` |
| JSON 기반 `OrderRepository` 구현 | `repositories/order_repository.py` |

---

### Phase 2 — 서비스 계층 (비즈니스 로직)

**목표**: 핵심 비즈니스 규칙 구현 및 테스트

| 작업 | 산출물 |
| :--- | :--- |
| 시료 등록/조회/검색 | `services/sample_service.py` |
| 주문 생성 (RESERVED 상태) | `services/order_service.py` |
| 주문 승인 (재고 충분 → CONFIRMED) | `services/order_service.py` |
| 주문 승인 (재고 부족 → PRODUCING, 생산량 계산) | `services/order_service.py` |
| 주문 거절 (→ REJECTED) | `services/order_service.py` |
| 생산 완료 처리 (FIFO → CONFIRMED) | `services/production_service.py` |
| 출고 처리 (CONFIRMED → RELEASE) | `services/production_service.py` |

---

### Phase 3 — 컨트롤러 및 콘솔 뷰

**목표**: 사용자 인터페이스 및 메뉴 시스템 구축

| 작업 | 산출물 |
| :--- | :--- |
| 콘솔 입출력 유틸리티 | `views/console_view.py` |
| 시료 관리 메뉴 | `controllers/sample_controller.py` |
| 주문/승인/거절 메뉴 | `controllers/order_controller.py` |
| 생산라인/출고 메뉴 | `controllers/production_controller.py` |
| 메인 메뉴 및 요약 대시보드 | `main.py` |

---

### Phase 4 — 모니터링 & Dummy 생성 도구

**목표**: 운영 및 테스트 지원 도구 구축

| 작업 | 산출물 |
| :--- | :--- |
| 시료/주문/생산라인 실시간 조회 | `tools/monitor.py` |
| 시료 및 주문 더미 데이터 생성 | `tools/dummy_generator.py` |

---

## 6. TDD 적용 원칙

모든 서비스 계층 구현은 `/test-driven-development` 스킬을 사용하여 아래 순서로 진행한다.

1. **RED**: 구현할 동작을 검증하는 테스트 작성 → `pytest -x`로 실패 확인
2. **GREEN**: 테스트를 통과시키는 최소한의 코드 작성 → `pytest`로 통과 확인
3. **REFACTOR**: 그린 상태 유지하며 코드 정리

테스트 파일은 `tests/` 디렉토리에 위치하며, 서비스 단위로 작성한다.

---

## 7. AI 에이전트 실행 순서

기능 구현 시 아래 에이전트 파이프라인을 준수한다.

```
consistency-verifier  →  문서 정합성 검증 (실패 시 ai-action 차단)
        ↓
    ai-action         →  TDD 방식으로 구현 코드 + 테스트 코드 생성
        ↓
compliance-verifier   →  구현-요구사항 정합성 검증  ┐
  test-verifier       →  테스트 품질 및 커버리지 검증 ┘ (병렬)
```

---

## 8. 커밋 전략

| 타입 | 설명 |
| :--- | :--- |
| `feat` | 새로운 기능 추가 |
| `test` | 테스트 코드 추가/수정 |
| `refactor` | 동작 변경 없는 코드 정리 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 |
| `chore` | 빌드, 설정 변경 |

Phase 단위로 커밋을 묶어 이력을 관리한다.
