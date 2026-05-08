# 반도체 시료(Sample) 주문 관리 시스템

## 프로젝트 개요

가상의 반도체 회사 "S-Semi"의 시료 생산주문관리 시스템.  
엑셀·메모장 기반의 수동 관리를 콘솔 기반 자동화 시스템으로 대체하는 PoC 프로젝트.

## 기술 스택

| 항목 | 내용 |
|---|---|
| Language | Python 3.x |
| UI | 콘솔(CLI), `rich` 라이브러리 (테이블·색상·진행바) |
| Test | pytest, pytest-cov |
| 데이터 | JSON 파일 기반 영속성 (`src/data/`) |
| VCS | Git + GitHub |

## 디렉토리 구조

```
SampleOrderSystem/
├── src/
│   ├── models/
│   │   ├── sample.py              # Sample 데이터 클래스
│   │   └── order.py               # Order 데이터 클래스 + OrderStatus Enum
│   ├── repositories/
│   │   ├── base.py                # BaseRepository (공통 JSON I/O)
│   │   ├── sample_repository.py
│   │   └── order_repository.py
│   ├── services/
│   │   ├── sample_service.py      # 시료 등록/조회/검색, ID 자동채번
│   │   ├── order_service.py       # 주문 생성/승인/거절, 재고 처리
│   │   └── production_service.py  # 생산 완료(시간 기반), 진행률, 출고
│   ├── controllers/
│   │   ├── sample_controller.py
│   │   ├── order_controller.py    # 섹션 분리 목록 조회
│   │   ├── production_controller.py
│   │   └── monitor_controller.py
│   ├── views/
│   │   └── console_view.py        # rich 기반 콘솔 출력 전담
│   ├── data/                      # JSON 데이터 저장소
│   │   ├── samples.json
│   │   └── orders.json
│   └── main.py                    # 진입점 · 메인 루프
├── tests/                         # pytest 테스트 (105개)
├── tools/
│   ├── monitor.py                 # Monitor, MonitorSnapshot, 재고 건강도 계산
│   └── dummy_generator.py         # 테스트용 더미 데이터 생성
├── docs/
│   ├── PRD.md                     # 제품 요구사항
│   ├── PLAN.md                    # 개발 계획 (4-Phase)
│   └── monitoringPRD.md           # 모니터링 기능 요구사항
├── agents/
│   ├── ai-action.md               # 코드 구현 에이전트
│   ├── consistency-verifier.md    # 문서 정합성 검증
│   ├── compliance-verifier.md     # 요구사항 충족 검증
│   └── test-verifier.md           # 테스트 품질 검증
├── requirements.txt               # rich>=13.0.0, pytest>=7.0.0
└── CLAUDE.md
```

## 사용자 역할

| 역할 | 책임 |
|---|---|
| 고객 (Customer) | 이메일로 시료 요청 |
| 주문 담당자 (Order Manager) | 주문서 작성 및 시스템 등록 |
| 생산 담당자 (Production Manager) | 시료 등록, 주문 승인/거절, 출고 처리 |

## 주문 상태 흐름

```
RESERVED (주문 접수)
  ├─ [거절]               → REJECTED
  └─ [승인 - 재고 충분]   → CONFIRMED (출고 대기)
  └─ [승인 - 재고 부족]   → PRODUCING (생산 중)
                              ↓ [시간 경과, 자동 완료]
                           CONFIRMED (출고 대기)
                              ↓ [6] 출고 처리
                           RELEASE (출고 완료)
```

| 상태 | 의미 |
|---|---|
| RESERVED | 주문 접수, 승인/거절 대기 |
| REJECTED | 주문 거절 (모니터링 통계 제외) |
| PRODUCING | 재고 부족으로 생산 라인 진행 중 |
| CONFIRMED | 생산 완료 또는 재고 충분, 출고 대기 |
| RELEASE | 출고 완료 |

## 핵심 비즈니스 로직

### 시료 ID 자동채번
- `S-001`, `S-002` … 형태로 자동 생성 (현재 MAX + 1)

### 주문 승인 처리
- **재고 ≥ 주문 수량**: 재고 즉시 차감 → `CONFIRMED`
- **재고 < 주문 수량**: 생산 라인 자동 등록 → `PRODUCING`

### 생산량 산출 공식
```
실 생산량 = ceil(부족분 / (수율 × 0.9))
생산 소요 시간 = 실 생산량 × 평균생산시간 (min/ea)
```

### 시간 기반 자동 생산 완료 (FIFO)
- 메인 루프 매 반복마다 `auto_complete_productions()` 호출
- FIFO: 첫 번째 주문이 끝나야 두 번째 주문 시작
- 주문 접수 시각(`created_at`)부터 경과 시간 계산
- 경과 시간 ≥ 소요 시간이면 자동으로 `CONFIRMED` 전환, 완료 알림 출력

### 재고 건강도 판정
| 상태 | 조건 | 색상 |
|---|---|---|
| 여유 | stock ≥ 미처리 주문 수요량 | 초록 |
| 부족 | 0 < stock < 미처리 수요량 | 노랑 |
| 고갈 | stock = 0 | 빨강(bold) |

잔여율(%) = stock / (stock + 수요량) × 100

## 메인 메뉴 구조

```
[1] 시료 관리        → 등록 · 전체 조회 · 검색
[2] 시료 주문        → 주문 생성 (RESERVED)
[3] 주문 승인/거절   → 목록 조회 · 승인 · 거절
[4] 모니터링         → [1] 주문량 확인 / [2] 재고량 확인
[5] 생산라인 조회    → 생산 진행률 · 완료예정 시각 표시
[6] 출고 처리        → CONFIRMED 목록 조회 후 RELEASE 처리
```

### 주문량 확인 ([4]-[1])
- RESERVED / PRODUCING / CONFIRMED / RELEASE 상태별 건수 및 목록
- REJECTED는 통계에서 완전 제외

### 재고량 확인 ([4]-[2])
- 시료별 재고(ea), 수요(ea), 잔여율(%), 상태(여유/부족/고갈)
- 고갈 임박 시 색상 강조

### 생산라인 조회 ([5])
- FIFO 순서, 상태(진행중/대기중), 생산수량(ea), 진행률 바(██░░), 완료예정(HH:MM)

### 접수 주문 목록 ([3] 서브메뉴)
- `[1] 접수 주문 목록 조회`: RESERVED(접수 대상) + 처리 완료 2섹션 분리
- `[2] 주문 승인` / `[3] 주문 거절`: RESERVED 목록만 출력 (최신순)

## AI 에이전트 워크플로우

코드 생성 전 반드시 이 순서를 따른다.

```
1. consistency-verifier  → 문서 간 정합성 검증 (실패 시 차단)
2. ai-action             → TDD 방식으로 구현 코드 + 테스트 생성
3. compliance-verifier   ┐ 병렬
   test-verifier         ┘ → 요구사항 충족 및 테스트 품질 검증
```

## 개발 원칙

- **TDD**: 실패하는 테스트 먼저 작성 (Red → Green → Refactor)
- **Clean Code**: 주석 최소화(WHY만), 명확한 네이밍, dead code 제거
- **MVC 패턴**: Model · Repository · Service · Controller · View 계층 분리
- **데이터 영속성**: JSON 파일 기반, Repository 패턴 (DB 교체 가능)
- **커밋 이력**: Conventional Commits (feat/fix/refactor/docs/chore)

## 테스트 현황

- **총 105개** 테스트 (전부 통과)
- 계층별 커버리지: 서비스·모델·레포지토리 99%+, 전체 약 75%
- mock은 `builtins.input`(콘솔 경계)과 `tmp_path`(파일시스템)에서만 사용
