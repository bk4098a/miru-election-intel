# Crawler

기계투표 35개국 조달 포털 크롤러.

portal_analysis 테이블의 P1/P2 포털을 대상으로 입찰공고를 수집합니다.

## 구현 예정 (P1 — 즉시)

| 포털 | 방식 | 파일 |
|------|------|------|
| Kazakhstan goszakup | REST API v3 | `parsers/goszakup.py` |
| Brazil PNCP | REST API | `parsers/pncp.py` |
| Bahrain Tender Board | HTML 테이블 | `parsers/bahrain.py` |
| Ghana GHANEPS | Struts HTML | `parsers/ghaneps.py` |
| Bhutan ECB | WordPress API | `parsers/ecb_bhutan.py` |
| Albania KQZ | WordPress API | `parsers/kqz_albania.py` |
| Jamaica GOJEP | JSF HTML | `parsers/gojep_jamaica.py` |
| Kyrgyzstan zakupki | JSF HTML | `parsers/zakupki_kg.py` |

## 구현 예정 (P2 — Playwright)

Bosnia eJN (POST), Philippines PhilGEPS, Kenya Tenders.go.ke, etc.
