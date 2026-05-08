# SampleOrderSystem

> 반도체 시료 생산주문관리 시스템 (S-Semi PoC)

엑셀·메모장 기반의 수동 주문 관리를 콘솔 자동화 시스템으로 대체합니다.

---

## 기술 스택

- **Language**: Python 3.x
- **UI**: CLI (`rich` 라이브러리)
- **데이터**: JSON 파일
- **Test**: pytest

## 실행 방법

```bash
pip install -r requirements.txt
python -m src.main
```

---

## 메뉴 구조

```
[1] 시료 관리        등록 · 조회 · 검색
[2] 시료 주문        주문 생성
[3] 주문 승인/거절   승인 · 거절 처리
[4] 모니터링         주문량 확인 · 재고량 확인
[5] 생산라인 조회    FIFO 생산 진행률 · 완료예정 시각
[6] 출고 처리        출고 실행
```

---

## 주문 상태 흐름

```
RESERVED ──[승인, 재고 충분]──▶ CONFIRMED ──[출고]──▶ RELEASE
         ──[승인, 재고 부족]──▶ PRODUCING
                                    │
                          (시간 경과, 자동 완료)
                                    ▼
                               CONFIRMED ──[출고]──▶ RELEASE
         ──[거절]──────────▶ REJECTED
```

---

## 핵심 로직

| 항목 | 내용 |
|---|---|
| 시료 ID | S-001, S-002 … 자동 채번 |
| 실 생산량 | `ceil(부족분 / (수율 × 0.9))` |
| 생산 방식 | 단일 라인 FIFO, 주문 접수 시각 기준 시간 계산 |
| 자동 생산 완료 | 메인 루프마다 경과 시간 확인 → 완료 시 CONFIRMED 자동 전환 |
| 재고 상태 | 여유 / 부족 / 고갈 자동 판정 + 잔여율(%) 시각화 |

---

## 프로젝트 구조

```
src/
├── models/          데이터 클래스 (Sample, Order, OrderStatus)
├── repositories/    JSON CRUD
├── services/        비즈니스 로직
├── controllers/     UI 조율
├── views/           콘솔 출력 (rich)
└── main.py          진입점
tests/               pytest 테스트 105개
tools/               Monitor, DummyGenerator
docs/                PRD.md · PLAN.md · monitoringPRD.md
```

---

## 테스트

```bash
python -m pytest tests/
python -m pytest tests/ --cov=src --cov=tools   # 커버리지 포함
```
