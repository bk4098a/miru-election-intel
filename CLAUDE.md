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
| -30 | 노이즈 | employee election, board election, union election |

**중요: `score`는 UI 정렬/필터용 메타데이터. 점수 무관 모든 공고를 DB에 저장.**  
파서에서 `score > 0` 게이트를 제거했음. 사용자가 UI에서 키워드/점수로 직접 필터링.

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

## 현재 파서 상태 (`crawler/parsers/`) — 24개 파서

### 작동 중 (Static)
| 파일 | 포털 | 상태 |
|---|---|---|
| `bahrain.py` | 바레인 etendering.tenderboard.gov.bh | ✅ HTML 테이블 파싱 |
| `tenders_kenya.py` | 케냐 iebc.or.ke | ✅ IEBC 정적 HTML — PDF 링크, 313건 |
| `ihec_iraq.py` | 이라크 ihec.iq | ✅ WP 사이트, 점수 메타데이터 |
| `etenders_za.py` | 남아공 etenders.gov.za | ✅ DataTables GET API, IEC 필터 |
| `dncp_paraguay.py` | 파라과이 pncp.dncp.gov.py | ✅ OCDS API, ES→EN 번역 |
| `bcn_barcelona.py` | 스페인 licitacions.bcn.cat | ✅ HTML 스크래핑, CA→EN 번역, 18건 |

### 작동 중 (Playwright)
| 파일 | 포털 | 상태 |
|---|---|---|
| `philgeps.py` | 필리핀 notices.philgeps.gov.ph | ✅ 선거 키워드 검색 |

### 신규 추가 (테스트 필요)
| 파일 | 포털 | 상태 |
|---|---|---|
| `compr_ar.py` | 아르헨티나 comprar.gob.ar + cne.gov.ar | 🔧 HTML 스크래핑 (ASP.NET, REST API 없음) |
| `riigihanked_est.py` | 에스토니아 riigihanked.riik.ee | ⚠️ API 401 — HTML 폴백, ET→EN |
| `spa_georgia.py` | 조지아 tenders.procurement.gov.ge | 🔧 루트 URL 작동 확인, API 경로 탐색 중 |
| `tenderboard_omn.py` | 오만 tenderboard.gov.om | 🔧 DNS 미달성 (서버에서 테스트 필요) |
| `cppp_india.py` | 인도 ECI + cppp.gov.in | ⚠️ 403/geo-block |
| `armp_drc.py` | 콩고민주공화국 marchepublic.cd | ⚠️ JSF 세션 필요 |
| `ejn_bosnia.py` | 보스니아 ejn.gov.ba | 🔧 Angular 포털, HTML 경로 탐색 중 |
| `gpa_mongolia.py` | 몽골 tender.gov.mn | 🔧 DNS 미달성 (서버에서 테스트 필요) |

### 조건부 작동 (API 키 필요)
| 파일 | 포털 | 상태 |
|---|---|---|
| `goszakup.py` | 카자흐스탄 goszakup.gov.kz | ⚠️ `GOSZAKUP_TOKEN` 환경변수 필요 |
| `g2b_korea.py` | 한국 나라장터 g2b.go.kr | ⚠️ `G2B_SERVICE_KEY` 필요 |
| `samgov_usa.py` | 미국 sam.gov | ⚠️ `SAMGOV_API_KEY` 필요 |

### 이슈 있음
| 파일 | 포털 | 상태 |
|---|---|---|
| `pncp.py` | 브라질 pncp.gov.br | ⚠️ ConnectionReset — TLS/WAF |
| `ghaneps.py` | 가나 ghaneps.gov.gh | ⚠️ 로그인 필요 |
| `wp_portals.py` | 부탄 ECB | ⚠️ 타임아웃 |
| `wp_portals.py` | 알바니아 KQZ | ⚠️ Next.js 재구축 |
| `zakupki_kg.py` | 키르기스스탄 zakupki.gov.kg | 🔧 미테스트 |
| `gojep.py` | 자메이카 GOJEP | ⚠️ JS 렌더링 필요 (Playwright) |

---

## 즉시 해야 할 작업

### ✅ 완료
- Bahrain 파서 수정
- 23개 파서 등록 (8개 신규: ARG, EST, GEO, OMN, IND, COD, BIH, MNG)
- `crawler/translate.py` 공용 번역 모듈 (ES/ET/KA/AR/FR/BS/MN→EN)
- Paraguay 기존 151건 title_en 마이그레이션
- `data/tender_search.html` 다크/라이트 모드 연동 (`localStorage('miru_theme')`)
- 점수 필터 UI 제거 (score는 메타데이터만)
- South Africa etenders.gov.za 파서 추가

### 1. 외부 작업: API 키 발급
- **Kazakhstan**: `https://ows.goszakup.gov.kz` → `.env`에 `GOSZAKUP_TOKEN=...`
- **Korea**: `https://www.data.go.kr` "나라장터 입찰공고정보서비스" → `.env`에 `G2B_SERVICE_KEY=...`
- **USA**: SAM.gov API key → `.env`에 `SAMGOV_API_KEY=...`

### 2. zakupki.gov.kg 테스트
- Miru가 CEC Kyrgyzstan에 납품한 국가라 모니터링 필수
- OCDS API (`ocds.zakupki.gov.kg/api/`) 접근 여부 확인

### 3. 신규 파서 서버 테스트 (네트워크 이슈)
- Oman (`tenderboard.gov.om`), Mongolia (`tender.gov.mn`): 개발 PC에서 DNS 불가 → 서버에서 테스트
- Georgia (`tenders.procurement.gov.ge`): API 경로 발견 필요
- Estonia: API 401 → HTML 폴백 경로 확인

### 4. 공고 검색 UI 사용법
- 크롤 완료 후: `python scripts/gen_tenders_js.py` → `data/tenders_data.js` 생성
- `data/tender_search.html` 브라우저에서 열기

---

## 데이터 스키마 (`election_intel_tenders.db` → `tenders`)

```sql
notice_key    TEXT UNIQUE  -- SHA1(iso3|url|title[:120])[:20]
country       TEXT
iso3          TEXT         -- ISO 3166-1 alpha-3
portal_name   TEXT
title         TEXT         -- 원문 제목 (notice_key 안정성 유지)
title_en      TEXT         -- 영어 번역 제목 (UI 표시용)
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
