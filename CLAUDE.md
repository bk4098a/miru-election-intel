# CLAUDE.md — miru-election-intel

이 파일은 Claude Code가 이 프로젝트를 처음 열 때 자동으로 읽는 컨텍스트입니다.

---

## 프로젝트 목적

Miru Systems 전략 인텔리전스 레이어.  
전 세계 기계투표(DRE/EVM/OMR) 35개국의 조달 공고를 수집·분석하는 별도 repo.

기존 `election-monitor` repo(운영 시스템 — 일일 크롤 + Streamlit 대시보드)와 분리하여 관리.

---

## 현재 상태 (2026-06-23 기준)

### 완성된 데이터 (`data/election_technology_world.db`, SQLite)

| 테이블 | 행수 | 설명 |
|---|---|---|
| `countries` | 206 | 전 세계 국가별 투표방식, 생체인증, Miru 공급 여부 |
| `machine_voting_portals` | 71 | 기계투표 35개국 조달 포털 목록 |
| `portal_analysis` | 66 | 각 포털 크롤링 사전 분석 결과 |

### 파서 구현 현황 (`crawler/parsers/`)

| 파일 | 포털 | 상태 |
|---|---|---|
| `goszakup.py` | 카자흐스탄 goszakup.gov.kz | ⚠️ API 토큰 필요 (환경변수 `GOSZAKUP_TOKEN`) |
| `pncp.py` | 브라질 pncp.gov.br | ⚠️ ConnectionReset — TLS/WAF 이슈. 엔드포인트 재확인 필요 |
| `ghaneps.py` | 가나 ghaneps.gov.gh | ⚠️ 검색 기능 로그인 필요. 공개 목록 URL 재탐색 필요 |
| `bahrain.py` | 바레인 etendering.tenderboard.gov.bh | 🔧 루트 URL(`/`) 접근 확인. 파서 URL 수정 필요 |
| `wp_portals.py` | 부탄 ECB / 알바니아 KQZ | ⚠️ ECB: 타임아웃. KQZ: Next.js로 재구축됨 (WordPress 아님) |
| `gojep.py` | 자메이카 GOJEP | ⚠️ JS 렌더링 필요 (Playwright 전환 필요) |
| `zakupki_kg.py` | 키르기스스탄 zakupki.gov.kg | 🔧 미테스트 |

### 핵심 모듈

```
crawler/
├── crawl.py       # 메인 오케스트레이터 (python crawler/crawl.py)
├── storage.py     # SQLite upsert (data/election_intel_tenders.db)
├── keywords.py    # 선거 키워드 필터 + 점수화
└── parsers/
    ├── __init__.py   # PARSERS 목록 (country, iso3, parse_fn)
    └── *.py          # 국가별 파서
```

---

## 즉시 해야 할 작업 (다음 세션)

### 1. Bahrain 파서 수정 (가장 쉬움, 30분)
```python
# bahrain.py 의 SEARCH_URLS 를 루트 URL로 수정
SEARCH_URLS = ['https://etendering.tenderboard.gov.bh/']
# table[1]이 공개 입찰 테이블 (8행+), 선거 키워드 없으면 구매처 기준으로도 필터
```

### 2. zakupki.gov.kg 테스트 및 수정 (1~2시간)
- OCDS API (`ocds.zakupki.gov.kg/api/`) 접근 여부 확인
- 실패 시 JSF ViewState 방식으로 폴백
- Miru가 CEC Kyrgyzstan에 납품한 국가라 모니터링 필수

### 3. goszakup API 토큰 발급 (외부 작업)
- `https://ows.goszakup.gov.kz` 에서 개발자 토큰 신청
- `.env` 파일에 `GOSZAKUP_TOKEN=your_token` 설정
- 토큰 없이 쓸 수 있는 공개 웹 검색(`/ru/search/lots`) 파서 fallback 추가

### 4. PNCP Brazil 엔드포인트 재확인
- `https://pncp.gov.br/api/consulta/v1/contratacoes/publicacoes` — ConnectionReset 발생
- 올바른 API 엔드포인트 탐색: `https://pncp.gov.br/api/pncp/v1/` 계열 시도
- 또는 공식 PNCP API 문서 확인: `https://pncp.gov.br/app/api`

### 5. KQZ Albania — Next.js 사이트
- `kqz.gov.al` 이 WordPress → Next.js 로 재구축됨
- `/procurimet` 또는 `/tendera` 경로 탐색
- requests 정적 파싱 시도 (Next.js SSR이면 가능)

### 6. GOJEP Jamaica — Playwright 전환
- `gojep.gov.jm` HTML은 JS 렌더링 필요
- Playwright 설치 후: `python -m playwright install chromium`

---

## 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 전체 크롤 (8개 포털)
python crawler/crawl.py

# 특정 국가만
python crawler/crawl.py --targets KAZ BHR KGZ

# 실제 저장 없이 테스트
python crawler/crawl.py --dry-run
```

---

## 데이터 스키마 (`election_intel_tenders.db` → `tenders` 테이블)

```sql
notice_key    TEXT UNIQUE  -- SHA1(iso3|url|title[:120])[:20]
country       TEXT
iso3          TEXT
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
score         INTEGER      -- keywords.py 기준 (40=강키워드, 15=약키워드)
crawled_at    TEXT
```

---

## 알려진 이슈 / 주의사항

- **SSL 오류**: 정부 사이트 다수 인증서 문제 → `verify=False` + `urllib3.disable_warnings()` 적용됨
- **goszakup API v3**: Bearer 토큰 없으면 모든 엔드포인트 401 반환
- **KQZ Albania**: WordPress가 아닌 Next.js (2026년 재구축). wp-json 경로 없음
- **GOJEP Jamaica**: ePPS (European Dynamics) 시스템. 조직 페이지(id=1936)가 JS 렌더링
- **GHANEPS Ghana**: Advanced Search는 로그인 필요. `/epps/notices/viewPublishedNotices.do` 공개 경로 시도 권장
- **Python 경로** (Windows): `C:\Users\KIM\AppData\Local\Python\bin\python.exe` (절대경로 사용)

---

## 관련 repo

- `election-monitor` (private): 운영 크롤러. 119개 글로벌 포털 일일 크롤, Streamlit 대시보드
  - DB: `data/election_monitor_country_tenders.db`
  - 이미 구현된 파서: SAM.gov, Paraguay DNCP, TED EU, World Bank, UNDP
