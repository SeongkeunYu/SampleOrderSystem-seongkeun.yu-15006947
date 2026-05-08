# 반도체 시료(Sample) 주문 관리 시스템

## 프로젝트 개요

가상의 반도체 회사 "S-Semi"의 시료 생산주문관리 시스템. 엑셀·메모장 기반의 수동 관리를 콘솔 기반 자동화 시스템으로 대체하는 PoC(Proof of Concept) 프로젝트.

## 기술 스택

- Language: Python 3.x
- Test: pytest
- VCS: Git + GitHub (GitHub MCP 연동)
- 가상 환경: `.venv/`

## 디렉토리 구조

```
SampleOrderSystem/
├── agents/                     # AI 에이전트 역할 정의
│   ├── ai-action.md            # 코드 구현 에이전트
│   ├── compliance-verifier.md  # 구현-요구사항 정합성 검증
│   ├── consistency-verifier.md # 문서 간 정합성 검증
│   └── test-verifier.md        # 테스트 품질 검증
├── docs/
│   └── PRD.md                  # 제품 요구사항 문서 (핵심 명세)
├── .claude/
│   └── skills/
│       └── test-driven-development/SKILL.md
├── .venv/                      # Python 가상 환경
├── .mcp.json                   # GitHub MCP 서버 설정
└── CLAUDE.md
```

> 실제 애플리케이션 코드(src/, tests/ 등)는 아직 미작성 상태. PRD 및 에이전트 워크플로우 정의 완료 후 구현 시작 단계.

## 사용자 역할

| 역할 | 책임 |
|------|------|
| 고객 (Customer) | 이메일로 시료 요청 |
| 주문 담당자 (Order Manager) | 주문서 작성 및 시스템 등록 |
| 생산 담당자 (Production Manager) | 시료 등록, 주문 승인/거절 처리 |

## 주문 상태 흐름

```
RESERVED → CONFIRMED (재고 충분)
RESERVED → PRODUCING → CONFIRMED (재고 부족, 생산 후)
RESERVED → REJECTED
CONFIRMED → RELEASE
```

| 상태 | 의미 |
|------|------|
| RESERVED | 주문 접수 |
| REJECTED | 주문 거절 |
| PRODUCING | 재고 부족으로 생산 중 |
| CONFIRMED | 생산 완료, 출고 대기 |
| RELEASE | 출고 완료 |

## 핵심 비즈니스 로직

- **수율(Yield)**: 정상 시료 / 총 생산 시료
- **실 생산량**: `ceil(부족분 / (수율 * 0.9))`
- **생산 방식**: 단일 라인, FIFO(선입선출)
- **승인 시 재고 충분**: 즉시 CONFIRMED
- **승인 시 재고 부족**: 생산 라인 자동 등록 후 PRODUCING

## 주요 기능

1. **시료 관리**: 등록 (ID, 이름, 평균 생산시간, 수율), 목록 조회, 이름 검색
2. **주문 처리**: 생성 (시료 ID, 고객명, 수량), 승인, 거절
3. **생산 라인**: FIFO 생산 관리, 공정 완료 시 CONFIRMED 전환
4. **출고 처리**: CONFIRMED → RELEASE 전환
5. **메인 메뉴 요약**: 시료 종수, 총 재고량, 전체 주문 건수, 생산라인 대기 현황

## AI 에이전트 워크플로우

코드 생성 전 반드시 이 순서를 따른다.

```
1. consistency-verifier  → 문서 간 정합성 검증 (통과 시에만 다음 단계)
2. ai-action             → 구현 코드 + 테스트 코드 생성
3. compliance-verifier   → 구현이 PRD 요구사항을 충족하는지 검증  ┐ 병렬
   test-verifier         → 테스트 품질 및 커버리지 검증            ┘
```

- `consistency-verifier` 실패 시 ai-action 실행 차단
- `compliance-verifier` + `test-verifier` 둘 다 통과해야 최종 승인

## 개발 원칙

- **TDD**: 구현 코드보다 실패하는 테스트를 먼저 작성 (Red → Green → Refactor)
- **Clean Code**: 주석 최소화, 명확한 네이밍
- **MVC 패턴**: 패키지 구조 및 역할 분리
- **데이터 영속성**: 파일/JSON/DB 중 선택하여 CRUD 구현
- **커밋 이력**: 기능 단위로 커밋

