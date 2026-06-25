# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 프로젝트 목적

Miru Systems 전략 인텔리전스 레이어.  
전 세계 기계투표(DRE/EVM/OMR) 35개국의 조달 공고를 수집·분석하는 별도 repo.

기존 `election-monitor` repo(운영 시스템 — 일일 크롤 + Streamlit 대시보드)와 분리하여 관리.

---

## 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 전체 크롤 (8개 포털)
python crawler/crawl.py

# 특정 국가만
python crawler/crawl.py --targets KAZ BHR KGZ

# DB 저장 없이 테스트
python crawler/crawl.py --dry-run

# 속도 조절 (기본 1초 간격)
python crawler/crawl.py --delay 2.0
```

테스트 파일 없음 — 검증은 `--dry-run` 모드로 수행.  
**Python 경로 (Windows)**: `C:\Users\KIM\AppData\Local\Python\bin\python.exe`

---

## 아키텍처

### 두 개의 독립 데이터베이스

| DB 파일 | 용도 | 생성 방법 |
|---|---|---|
| `data/election_technology_world.db` | 레퍼런스 데이터 (정적) | `scripts/build_*.py` 수동 실행 |
| `data/election_intel_tenders.db` | 크롤 결과 누적 (동적) | `crawler/crawl.py` 자동 생성 |

레퍼런스 DB는 `scripts/`의 빌드 스크립트로 최초 1회 생성하며 이후 수동 업데이트.  
크롤 DB는 매 실행 시 upsert로 누적됨 (`notice_key` = SHA1(iso3|url|title[:120])[:20]).

### 크롤러 흐름

```
crawler/crawl.py          # CLI 오케스트레이터
  → parsers/__init__.py   # PARSERS 목록 (country, iso3, parse_fn)
  → parsers/*.py          # 국가별 파서 (API / HTML 파싱)
  → keywords.py           # 선거 키워드 필터 + 점수화
  → storage.py            # SQLite upsert → election_intel_tenders.db
```

### 키워드 점수 시스템 (`keywords.py`)

| 점수 | 키워드 유형 | 예시 |
|---|---|---|
| +40 | 강키워드 | election, EVM, DRE, VVPAT, выборы, eleição |
| +15 | 약키워드 | biometric, voter, OMR, tabulation, KIEMS |
| -30 | 노이즈 (자동 제외) | employee election, board election, union election |

`score > 0`인 공고만 DB에 저장.

### 빌드 스크립트 (`scripts/`)

| 파일 | 출력 |
|---|---|
| `build_election_tech_db.py` | `countries` 206개국 (투표방식·생체인증·Miru 공급) |
| `build_machine_voting_portals.py` | `machine_voting_portals` 71개 포털 (35개국) |
| `build_portal_analysis.py` | `portal_analysis` 71개 포털 크롤 타당성 분석 |

### 차트/보고서 (`brand_save.py`)

Matplotlib Miru 브랜드 테마 유틸리티. `data/*.html` 지역별 보고서 생성에 사용.  
폰트: `fonts/GmarketSansTTFMedium.ttf` (한국어 표시).

---

## 현재 파서 상태 (`crawler/parsers/`)

| 파일 | 포털 | 상태 |
|---|---|---|
| `goszakup.py` | 카자흐스탄 goszakup.gov.kz | ⚠️ API 토큰 필요 (`GOSZAKUP_TOKEN` 환경변수) |
| `pncp.py` | 브라질 pncp.gov.br | ⚠️ ConnectionReset — TLS/WAF 이슈 |
| `ghaneps.py` | 가나 ghaneps.gov.gh | ⚠️ 검색 기능 로그인 필요 |
| `bahrain.py` | 바레인 etendering.tenderboard.gov.bh | ✅ 루트 URL 수정 완료 |
| `wp_portals.py` | 부탄 ECB / 알바니아 KQZ | ⚠️ ECB 타임아웃 / KQZ Next.js 재구축 |
| `gojep.py` | 자메이카 GOJEP | ⚠️ JS 렌더링 필요 (Playwright 전환) |
| `zakupki_kg.py` | 키르기스스탄 zakupki.gov.kg | 🔧 미테스트 |
| `philgeps.py` | 필리핀 philgeps.gov.ph | ✅ 신규 — `/Indexes/` HTML 테이블 파싱 |
| `g2b_korea.py` | 한국 나라장터 g2b.go.kr | ✅ 신규 — data.go.kr API (`G2B_SERVICE_KEY` 필요) |
| `tenders_kenya.py` | 케냐 tenders.go.ke | ✅ 신규 — JSON API + HTML fallback |

---

## 즉시 해야 할 작업

### 1. ✅ Bahrain 파서 수정 — 완료

### 2. zakupki.gov.kg 테스트 (1~2시간)
- OCDS API (`ocds.zakupki.gov.kg/api/`) 접근 여부 확인
- 실패 시 JSF ViewState 방식 폴백
- Miru가 CEC Kyrgyzstan에 납품한 국가라 모니터링 필수

### 3. goszakup API 토큰 발급 (외부 작업)
- `https://ows.goszakup.gov.kz` 에서 개발자 토큰 신청 → `.env`에 `GOSZAKUP_TOKEN=...`
- 토큰 없이 쓸 수 있는 공개 웹 검색(`/ru/search/lots`) 파서 fallback 추가

### 4. Korea G2B API Key 발급 (외부 작업)
- `https://www.data.go.kr` → 검색: "나라장터 입찰공고정보서비스" → 활용 신청
- `.env`에 `G2B_SERVICE_KEY=...` 추가
- 무료 발급, 승인 1~2일 소요

### 5. PNCP Brazil 엔드포인트 재확인
- 현재 `https://pncp.gov.br/api/consulta/v1/contratacoes/publicacoes` → ConnectionReset
- 대안: `https://pncp.gov.br/api/pncp/v1/` 또는 공식 문서 `https://pncp.gov.br/app/api`

### 6. KQZ Albania — Next.js 전환
- `kqz.gov.al` WordPress → Next.js 재구축됨. wp-json 경로 없음
- `/procurimet` 또는 `/tendera` 경로 탐색 (SSR이면 requests 정적 파싱 가능)

### 7. GOJEP Jamaica — Playwright 전환
- `gojep.gov.jm` JSF 렌더링 필요
- `python -m playwright install chromium` 후 파서 재작성

### 8. 공고 검색 UI 사용법
- 크롤 완료 후: `python scripts/gen_tenders_js.py` → `data/tenders_data.js` 생성
- `data/tender_search.html` 브라우저에서 열기
- 키워드·지역·카테고리·점수 필터 + 알람 설정 (localStorage)

---

## 데이터 스키마 (`election_intel_tenders.db` → `tenders`)

```sql
notice_key    TEXT UNIQUE  -- SHA1(iso3|url|title[:120])[:20]
country       TEXT
iso3          TEXT         -- ISO 3166-1 alpha-3
portal_name   TEXT
title         TEXT
url           TEXT
published_date TEXT
deadline_date  TEXT
status        TEXT
buyer         TEXT
amount        REAL
currency      TEXT
snippet       TEXT
score         INTEGER      -- 40=강키워드, 15=약키워드
crawled_at    TEXT         -- UTC
```

---

## 알려진 이슈

- **SSL**: 정부 사이트 인증서 문제 → `verify=False` + `urllib3.disable_warnings()` 전체 적용
- **goszakup API v3**: Bearer 토큰 없으면 모든 엔드포인트 401
- **KQZ Albania**: wp-json 경로 없음 (2026년 Next.js 재구축)
- **GOJEP Jamaica**: ePPS(European Dynamics) 시스템. 조직 페이지(id=1936) JS 렌더링
- **GHANEPS Ghana**: `/epps/notices/viewPublishedNotices.do` 공개 경로 시도 권장

---

## 관련 repo

- `election-monitor` (private): 119개 글로벌 포털 일일 크롤 + Streamlit 대시보드
  - 기구현 파서: SAM.gov, Paraguay DNCP, TED EU, World Bank, UNDP
  - DB: `data/election_monitor_country_tenders.db`
