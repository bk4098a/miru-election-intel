"""
Update machine_voting_portals with verified URL status, tender_section_url,
and search_keywords based on live verification (2026-06-23).
"""
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

DB = "data/election_technology_world.db"
VERIFIED_DATE = "2026-06-23"

# --------------------------------------------------------------------------
# Schema additions
# --------------------------------------------------------------------------
NEW_COLS = [
    ("tender_section_url", "TEXT"),
    ("http_status", "TEXT"),   # Working / Dead / Login / Blocked / JS_rendered / Info_only
    ("search_keywords", "TEXT"),
    ("verified_date", "TEXT"),
]

# --------------------------------------------------------------------------
# Verified data: (iso3, portal_name_fragment, updates_dict)
# portal_name_fragment is a LIKE match on portal_name column
# --------------------------------------------------------------------------
UPDATES = [
    # ── PHILIPPINES ──────────────────────────────────────────────────────
    ("PHL", "PhilGEPS", {
        "tender_section_url": "https://notices.philgeps.gov.ph/GEPS/Tender/SplashOpportunitiesSearchUI.aspx?menuIndex=3&ClickFrom=OpenOpp",
        "http_status": "Working",
        "search_keywords": "voting machine,electronic voting,automated counting machine,ACM,PCOS,COMELEC",
        "verified_date": VERIFIED_DATE,
    }),
    ("PHL", "COMELEC Procurement", {
        "tender_section_url": "https://www.comelec.gov.ph/?r=Procurement",
        "http_status": "Working",
        "search_keywords": "bidding,equipment,ACM,automated counting",
        "verified_date": VERIFIED_DATE,
    }),
    ("PHL", "COMELEC Latest", {
        "tender_section_url": "https://www.comelec.gov.ph/index.html?r=Procurement/LatestUpdates",
        "http_status": "Working",
        "search_keywords": "bidding,contract",
        "verified_date": VERIFIED_DATE,
    }),

    # ── SOUTH KOREA ──────────────────────────────────────────────────────
    ("KOR", "나라장터", {
        "http_status": "Login",   # OIDC SSO — no public browse URL
        "search_keywords": "선거,투표,전자개표,투표기,선거관리위원회",
        "notes": "SSO 로그인 필요 (OIDC). 공개 URL 없음. PPS OpenAPI 대안 검토 필요",
        "verified_date": VERIFIED_DATE,
    }),
    ("KOR", "EVA G2B", {
        "http_status": "Login",
        "search_keywords": "전자,입찰",
        "verified_date": VERIFIED_DATE,
    }),
    ("KOR", "중앙선거관리위원회", {
        "http_status": "Info_only",
        "notes": "NEC는 자체 입찰 없음. 모든 조달은 G2B 통해 공고",
        "verified_date": VERIFIED_DATE,
    }),

    # ── MONGOLIA ─────────────────────────────────────────────────────────
    ("MNG", "State Procurement", {
        "http_status": "Dead",   # 403 Forbidden
        "notes": "403 Forbidden — 접근 불가. e-tender.mn 사용 권장",
        "verified_date": VERIFIED_DATE,
    }),
    ("MNG", "GPA e-Tender", {
        "url": "https://www.e-tender.mn/",
        "tender_section_url": "https://www.e-tender.mn/en/tenders/",
        "http_status": "Working",
        "search_keywords": "election,voting,сонгуулийн,санал хураалт",
        "verified_date": VERIFIED_DATE,
    }),
    ("MNG", "GEC Mongolia", {
        "http_status": "Info_only",
        "notes": "선거위원회 정보 사이트. 조달 없음. e-tender.mn 사용",
        "verified_date": VERIFIED_DATE,
    }),

    # ── INDIA ────────────────────────────────────────────────────────────
    ("IND", "eProcure", {
        "tender_section_url": "https://eprocure.gov.in/cppp/tendersearch",
        "http_status": "Working",
        "search_keywords": "electronic voting machine,EVM,VVPAT,ballot unit,Election Commission of India",
        "verified_date": VERIFIED_DATE,
    }),
    ("IND", "ECI Tender", {
        "http_status": "Dead",   # 403 Forbidden
        "notes": "403 반환. eprocure.gov.in에서 ECI 기관 필터 사용 권장",
        "verified_date": VERIFIED_DATE,
    }),
    ("IND", "CPPP", {
        "url": "https://eprocure.gov.in/cppp/tendersearch",
        "tender_section_url": "https://eprocure.gov.in/cppp/tendersearch",
        "http_status": "Working",
        "search_keywords": "EVM,VVPAT,election commission",
        "verified_date": VERIFIED_DATE,
    }),

    # ── BHUTAN ───────────────────────────────────────────────────────────
    ("BTN", "e-GP Bhutan", {
        "tender_section_url": "https://www.egp.gov.bt/resources/common/TenderListing.jsp?h=t",
        "http_status": "Working",
        "search_keywords": "election,voting,ECB,Election Commission of Bhutan",
        "verified_date": VERIFIED_DATE,
    }),
    ("BTN", "ECB Tender", {
        "url": "https://www.ecb.bt/tender",            # fixed from /tender-information/
        "tender_section_url": "https://www.ecb.bt/tender",
        "http_status": "Working",
        "notes": "/tender-information/ 는 2017년 아카이브. 현행 URL: /tender",
        "verified_date": VERIFIED_DATE,
    }),

    # ── IRAQ ─────────────────────────────────────────────────────────────
    ("IRQ", "IHEC Iraq", {
        "tender_section_url": "https://ihec.iq/tenders-and-contracts/",
        "http_status": "Working",
        "notes": "PDF 아카이브만 존재. 실시간 입찰 DB 없음. PDF 업로드 주기 모니터링 필요",
        "search_keywords": "voting machine,electronic ballot,جهاز التصويت",
        "verified_date": VERIFIED_DATE,
    }),
    ("IRQ", "MoP Iraq", {
        "http_status": "Info_only",
        "notes": "규제/감독 기관. 입찰 발주기관 아님. IHEC가 직접 조달",
        "verified_date": VERIFIED_DATE,
    }),

    # ── KYRGYZSTAN ───────────────────────────────────────────────────────
    ("KGZ", "zakupki.gov.kg", {
        "url": "http://zakupki.gov.kg/popp/view/order/list.xhtml",
        "tender_section_url": "http://zakupki.gov.kg/popp/view/order/list.xhtml",
        "http_status": "Working",
        "search_keywords": "ЦИК,Центральная избирательная комиссия,электронный,голосование",
        "notes": "공개 검색 가능. OCDS API: http://ocds.zakupki.gov.kg/dashboard/weekly",
        "verified_date": VERIFIED_DATE,
    }),
    ("KGZ", "CEC Kyrgyzstan", {
        "http_status": "Info_only",
        "notes": "선거 정보 사이트. 조달은 zakupki.gov.kg에서 ЦИК로 검색",
        "verified_date": VERIFIED_DATE,
    }),

    # ── UZBEKISTAN ───────────────────────────────────────────────────────
    ("UZB", "xarid.uzex.uz", {
        "http_status": "JS_rendered",
        "search_keywords": "Марказий сайлов комиссияси,Центральная избирательная комиссия,овоз бериш машинаси",
        "notes": "JS 렌더링. 뷰: 공개. 입찰참여: 등록+EDS 필요. etender.uzex.uz도 확인",
        "verified_date": VERIFIED_DATE,
    }),
    ("UZB", "CEC Uzbekistan", {
        "http_status": "Info_only",
        "notes": "정보 사이트. 조달은 xarid.uzex.uz에서 CEC로 검색",
        "verified_date": VERIFIED_DATE,
    }),

    # ── OMAN ─────────────────────────────────────────────────────────────
    ("OMN", "Tender Board Oman", {
        "tender_section_url": "https://etendering.tenderboard.gov.om/product/publicDash?CTRL_STRDIRECTION=LTR",
        "http_status": "Working",
        "search_keywords": "آلة تصويت,إلكتروني,انتخاب,voting,election",
        "notes": "공개 대시보드 2,262개+ 공고. /ctm/Am/PublicSearchTender.html WAF 차단됨",
        "verified_date": VERIFIED_DATE,
    }),

    # ── UAE ──────────────────────────────────────────────────────────────
    ("ARE", "Federal e-Procurement", {
        "url": "https://mof.gov.ae/en/public-finance/government-procurement/current-business-opportunities/",
        "tender_section_url": "https://mof.gov.ae/en/public-finance/government-procurement/current-business-opportunities/",
        "http_status": "Working",
        "search_keywords": "election,voting,Federal National Council",
        "notes": "procurement.gov.ae는 로그인 전용. MoF 공개 목록 페이지 사용",
        "verified_date": VERIFIED_DATE,
    }),
    ("ARE", "UAE NEC", {
        "http_status": "Info_only",
        "notes": "NEC 정보 사이트. 조달 없음. FNC 선거는 제한된 선거인단 방식",
        "verified_date": VERIFIED_DATE,
    }),

    # ── IRAN ─────────────────────────────────────────────────────────────
    ("IRN", "SETAD Iran", {
        "http_status": "Blocked",
        "notes": "이란 외부에서 geo-차단. Farsi 전용. irantenders.com 대리 모니터링 고려",
        "verified_date": VERIFIED_DATE,
    }),
    ("IRN", "MoI Iran", {
        "http_status": "Blocked",
        "notes": "403 반환. 이란 외부 접근 불가",
        "verified_date": VERIFIED_DATE,
    }),

    # ── BRAZIL ───────────────────────────────────────────────────────────
    ("BRA", "Compras.gov.br", {
        "tender_section_url": "https://pncp.gov.br/app/editais",
        "http_status": "Working",
        "search_keywords": "urna eletrônica,votação eletrônica,TSE,equipamento eleitoral",
        "verified_date": VERIFIED_DATE,
    }),
    ("BRA", "TSE", {
        "url": "https://www.tse.jus.br/transparencia-e-prestacao-de-contas/licitacoes-e-contratos/licitacoes",
        "tender_section_url": "https://www.tse.jus.br/transparencia-e-prestacao-de-contas/licitacoes-e-contratos/licitacoes",
        "http_status": "Working",
        "search_keywords": "urna eletrônica,contratação eleições,equipamento",
        "notes": "URL 변경됨: /transparencia/gestao-de-contratacoes → /transparencia-e-prestacao-de-contas/...",
        "verified_date": VERIFIED_DATE,
    }),
    ("BRA", "ComprasNet", {
        "http_status": "Working",
        "search_keywords": "urna,votação,eleições",
        "verified_date": VERIFIED_DATE,
    }),

    # ── PARAGUAY ─────────────────────────────────────────────────────────
    ("PRY", "DNCP", {
        "tender_section_url": "https://www.contrataciones.gov.py/buscador/licitaciones.html",
        "http_status": "Working",
        "search_keywords": "máquina de votación,BUE,boleta única electrónica,TSJE",
        "verified_date": VERIFIED_DATE,
    }),

    # ── VENEZUELA ────────────────────────────────────────────────────────
    ("VEN", "SNC", {
        "http_status": "Working",
        "notes": "직접 입찰 목록 없음. 홈페이지 Servicios en Línea 통해 접근. CNE는 비공개 조달",
        "search_keywords": "máquina de votación,CNE,SAES,Smartmatic",
        "verified_date": VERIFIED_DATE,
    }),
    ("VEN", "CNE", {
        "http_status": "Dead",   # ECONNREFUSED
        "notes": "사이트 접근 불가 (ECONNREFUSED). CNE는 공개 조달 없음. SNC로 대체",
        "verified_date": VERIFIED_DATE,
    }),

    # ── ARGENTINA ────────────────────────────────────────────────────────
    ("ARG", "COMPR.AR", {
        "http_status": "Working",
        "search_keywords": "máquina de votar,BUE,boleta única electrónica,elecciones",
        "verified_date": VERIFIED_DATE,
    }),
    ("ARG", "Cámara Nacional Electoral", {
        "http_status": "Info_only",
        "notes": "사법기관. 자체 조달 없음. 내무부 Dirección Electoral이 조달. COMPR.AR 사용",
        "verified_date": VERIFIED_DATE,
    }),

    # ── BELGIUM ──────────────────────────────────────────────────────────
    ("BEL", "e-Notification", {
        "url": "https://enot.publicprocurement.be/enot-war/searchNotice.do",
        "tender_section_url": "https://enot.publicprocurement.be/enot-war/searchNotice.do",
        "http_status": "Working",
        "search_keywords": "machine à voter,stemcomputer,voting machine,Smartmatic,elections",
        "notes": "EU 외부에서 연결 차단될 수 있음. BOSA eProcurement 시스템",
        "verified_date": VERIFIED_DATE,
    }),
    ("BEL", "e-Tendering Belgium", {
        "http_status": "Working",
        "search_keywords": "vote électronique,stemmen",
        "verified_date": VERIFIED_DATE,
    }),

    # ── BULGARIA ─────────────────────────────────────────────────────────
    ("BGR", "eOP", {
        "http_status": "JS_rendered",
        "search_keywords": "електронно гласуване,машина за гласуване,ЦИК,Smartmatic",
        "notes": "React/Angular SPA — 정적 파서 불가. Playwright 필요. Negometrix 기반",
        "verified_date": VERIFIED_DATE,
    }),
    ("BGR", "CIK Bulgaria", {
        "http_status": "Dead",   # 403
        "notes": "403 반환. CIK 입찰은 app.eop.bg에서 ЦИК 기관명으로 검색",
        "verified_date": VERIFIED_DATE,
    }),

    # ── BOSNIA ───────────────────────────────────────────────────────────
    ("BIH", "eJN Bosnia", {
        "url": "https://next.ejn.gov.ba/Announcement/Search",
        "tender_section_url": "https://next.ejn.gov.ba/Announcement/Search",
        "http_status": "Working",
        "search_keywords": "glasačka mašina,elektronsko glasanje,CIK,Centralna izborna komisija",
        "notes": "ejn.gov.ba → next.ejn.gov.ba로 이전 중. 신규 URL 사용",
        "verified_date": VERIFIED_DATE,
    }),
    ("BIH", "CIK BiH", {
        "http_status": "Info_only",
        "notes": "izbori.ba는 선거결과 사이트. CIK 조달은 eJN에서 'Centralna izborna komisija' 검색",
        "verified_date": VERIFIED_DATE,
    }),

    # ── GEORGIA ──────────────────────────────────────────────────────────
    ("GEO", "SPA Procurement Georgia", {
        "url": "https://tenders.procurement.gov.ge",
        "tender_section_url": "https://tenders.procurement.gov.ge/public/#/en/projects?type=tender",
        "http_status": "Working",
        "search_keywords": "ამომრჩეველი,election,voting machine,Smartmatic,CEC",
        "notes": "Hash URL (#/en/...) 정적 파싱 불가. 기본 URL 사용. 2026-06-01 신규 중앙조달청 ctd.cpb.gov.ge도 확인",
        "verified_date": VERIFIED_DATE,
    }),
    ("GEO", "CEC Georgia", {
        "http_status": "Dead",   # 403 from outside
        "notes": "403 반환. CEC 조달은 tenders.procurement.gov.ge에서 선거관리청 명칭으로 검색",
        "verified_date": VERIFIED_DATE,
    }),

    # ── ALBANIA ──────────────────────────────────────────────────────────
    ("ALB", "APP e-Procurement", {
        "tender_section_url": "https://app.gov.al/njoftimi-i-kontrates-se-shpallur/",
        "http_status": "Working",
        "search_keywords": "makinë votimi,zgjedhje,KQZ,Komisioni Qendror i Zgjedhjeve",
        "verified_date": VERIFIED_DATE,
    }),
    ("ALB", "KQZ", {
        "http_status": "Info_only",
        "notes": "Next.js 재구축. 조달 섹션 없음. APP e-Procurement에서 KQZ 기관명으로 검색",
        "verified_date": VERIFIED_DATE,
    }),

    # ── ESTONIA ──────────────────────────────────────────────────────────
    ("EST", "Riigihangete Register", {
        "http_status": "Working",
        "search_keywords": "hääletusmasin,elektrooniline hääletamine,Riigi Valimisteenistus,i-voting",
        "verified_date": VERIFIED_DATE,
    }),
    ("EST", "State Electoral Office", {
        "http_status": "Info_only",
        "notes": "선거 정보 사이트. 조달은 Riigihangete Register에서 Riigi Valimisteenistus 검색",
        "verified_date": VERIFIED_DATE,
    }),

    # ── SWITZERLAND ──────────────────────────────────────────────────────
    ("CHE", "SIMAP Switzerland", {
        "http_status": "Working",
        "search_keywords": "e-voting,Online-Stimmabgabe,Swiss Post,Bundeskanzlei",
        "notes": "2024-07 이후 입찰만 포함. /en/publications 경로 폐기됨. 홈페이지 검색 사용",
        "verified_date": VERIFIED_DATE,
    }),
    ("CHE", "Bundeskanzlei e-Voting", {
        "http_status": "Info_only",
        "notes": "정보 페이지. 입찰 없음. SIMAP 사용",
        "verified_date": VERIFIED_DATE,
    }),

    # ── USA ──────────────────────────────────────────────────────────────
    ("USA", "SAM.gov", {
        "tender_section_url": "https://sam.gov/search/?index=opp&is_active=true&q=voting+system",
        "http_status": "Working",
        "search_keywords": "voting system,election equipment,ballot tabulation,election management system",
        "notes": "연방 포털. 주(州) 입찰은 별도: CA=caleprocure.ca.gov, TX=txsmartbuy.gov, FL=vendor.myfloridamarketplace.com",
        "verified_date": VERIFIED_DATE,
    }),
    ("USA", "EAC", {
        "http_status": "Info_only",
        "notes": "인증/표준 기관. 조달 없음. EAC 자체 계약은 SAM.gov에 게재",
        "verified_date": VERIFIED_DATE,
    }),

    # ── DRC ──────────────────────────────────────────────────────────────
    ("COD", "ARMP", {
        "tender_section_url": "https://marchepublic.cd/",
        "http_status": "Working",
        "search_keywords": "machine de vote,DEV,dispositif electronique,CENI",
        "notes": "Form 기반 검색. CENI 기관명으로 필터. CENI 자체 사이트(ceni.cd)는 조달 없음",
        "verified_date": VERIFIED_DATE,
    }),
]


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # 1. Add new columns if not exist
    existing = {row[1] for row in cur.execute("PRAGMA table_info(machine_voting_portals)")}
    for col_name, col_type in NEW_COLS:
        if col_name not in existing:
            cur.execute(f"ALTER TABLE machine_voting_portals ADD COLUMN {col_name} {col_type}")
            print(f"  + column: {col_name}")

    # 2. Apply updates
    updated = 0
    not_found = []
    for iso3, name_fragment, fields in UPDATES:
        set_parts = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values())

        # Match by iso3 + portal_name LIKE '%fragment%'
        cur.execute(
            f"UPDATE machine_voting_portals SET {set_parts} "
            f"WHERE iso3 = ? AND portal_name LIKE ?",
            values + [iso3, f"%{name_fragment}%"],
        )
        if cur.rowcount == 0:
            not_found.append((iso3, name_fragment))
        else:
            updated += cur.rowcount

    conn.commit()

    # 3. Report
    print(f"\n업데이트 완료: {updated}개 포털")
    if not_found:
        print("\n매칭 실패 (포털명 확인 필요):")
        for iso3, frag in not_found:
            print(f"  {iso3}: '{frag}'")

    # 4. Status summary
    print("\n[http_status 분포]")
    for row in cur.execute(
        "SELECT http_status, COUNT(*) FROM machine_voting_portals "
        "WHERE iso3 IN (SELECT iso3 FROM countries WHERE machine_voting IN ('Yes','Pilot')) "
        "GROUP BY http_status ORDER BY COUNT(*) DESC"
    ):
        print(f"  {row[0] or 'null':20s} {row[1]}")

    # 5. Show Working primary portals
    print("\n[Working 기계투표국 주요 포털]")
    cur.execute("""
        SELECT p.iso3, p.country, p.portal_name, p.tender_section_url, p.http_status
        FROM machine_voting_portals p
        WHERE p.iso3 IN (SELECT iso3 FROM countries WHERE machine_voting IN ('Yes','Pilot'))
          AND p.priority = 'High'
          AND p.http_status = 'Working'
        ORDER BY p.iso3, p.portal_name
    """)
    for r in cur.fetchall():
        print(f"  {r[0]} | {r[2]:35s} | {r[3] or r[2]}")

    conn.close()


if __name__ == "__main__":
    main()
