"""
Machine Voting Intelligence Migration (2026-06-23)

웹 리서치 검증 완료 후 실행:
  1. countries 테이블에 새 컬럼 7개 추가
  2. iso3 중복 10건 병합 (notes가 긴 행 보존)
  3. 기계투표 국가 데이터 정제 (주요 수정사항 포함)
  4. 종이투표 / 선거없음 국가 플래그 처리

주요 수정사항 (기존 DB 대비):
  BRA: vendor → Positivo Tecnologia (TSE 자체가 아님)
  PRY: machine_type → BMD (DRE 아님. RFID+종이 투표지 방식)
  VEN: vendor → Ex-Clé Soluciones Biométricas / model → EC-21
  ALB: machine_voting → Pilot (전국 아님. 75개 센터 파일럿만)
  BEL: deployment_scale → Partial (왈로니아는 종이투표)
  BIH: machine_voting → Yes / machine_type → OMR (종이투표지+스캐너 방식)
  ARG: machine_type → BMD (CABA 한정, 전국 아님)
  IRN: machine_type → DRE (테헤란 지역 의회선거 확인. 대통령선거는 종이)
  BTN: contract_year → 2008 (최초 도입 기준)
"""
import sqlite3, sys, io, pathlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
DB_PATH = pathlib.Path("data/election_technology_world.db")

# ─────────────────────────────────────────────
# 검증된 기계투표 국가 데이터
# ─────────────────────────────────────────────
# (machine_voting, machine_type, machine_model, vendor_name, vendor_country, contract_year, deployment_scale, confidence)
#
# 출처: TSE Brazil, COMELEC Philippines, IHEC Iraq, NEC Korea, ECI India,
#       CENI DRC, Smartmatic press releases, OSCE/ODIHR 2025 Albania,
#       Biometric Update, Carter Center Venezuela 2024, Brennan Center USA,
#       CEC Georgia, IEC South Africa, GEC Mongolia, EC Ghana

MACHINE_VOTING_DATA = {
    # ── DRE (Direct Recording Electronic) ──────────────────────────────
    # 브라질: TSE 발주, Positivo Tecnologia 제조 (2021 입찰 낙찰)
    # UE2022 219,998대 생산(2024-04 완료). 2024 지방선거 571,024대 투입
    "BRA": ("Yes",   "DRE",     "Urna Eletrônica UE2022",
            "Positivo Tecnologia",      "BRA", "2021", "National", "High"),

    # 파라과이: 브라질 기기 아님. 아르헨티나 MSA 컨소시엄 계약
    # BUE = RFID칩 내장 종이투표지 + 터치스크린 마킹 → 실물 투표함에 투입 = BMD
    "PRY": ("Yes",   "BMD",     "BUE (Boleta Única Electrónica)",
            "Consorcio Comitia-MSA",    "ARG", "2023", "National", "High"),

    # 베네수엘라: Smartmatic 2018 철수 후 Ex-Clé(아르헨티나)가 운영
    # EC-21 DRE 약 30,000대. 2024 대선 사용 (결과 조작 의혹)
    "VEN": ("Yes",   "DRE",     "EC-21",
            "Ex-Clé Soluciones Biométricas", "ARG", "2020", "National", "High"),

    # 이란: 의회선거 테헤란 일부 지역 DRE 약 3,700대 확인 (2024)
    # 대통령선거는 종이. 제조사 미공개(국산 추정). 파일럿 수준
    "IRN": ("Pilot", "DRE",     "domestic EVM (type unconfirmed)",
            "domestic",                 "IRN", "2024", "Partial",  "Med"),

    # ── EVM (Electronic Voting Machine — 버튼식 또는 터치스크린) ──────────
    # 인도: M3 세대(2013~) BEL+ECIL 국산. 5.5M대 투입(2024 총선). VVPAT 의무화
    "IND": ("Yes",   "EVM",     "M3 EVM + VVPAT",
            "BEL + ECIL",               "IND", "2013", "National", "High"),

    # DRC: Miru Systems DEV(Dispositif Electronique de Vote) = BMD
    # 터치스크린으로 선택 → QR코드 종이투표지 인쇄 → 실물 투표함 투입
    # 2018: 105,257대. 2023: 26,000대 신규 + 80,000대 기존 refurb
    "COD": ("Yes",   "BMD",     "DEV (Dispositif Electronique de Vote)",
            "Miru Systems",             "KOR", "2023", "National", "High"),

    # 부탄: 인도산 EVM(ECIL Hyderabad + BEL Bangalore). M2세대 추정
    # 2024 총선 809개 투표소 전국 사용
    "BTN": ("Yes",   "EVM",     "BEL/ECIL EVM (M2-era)",
            "BEL + ECIL",               "IND", "2008", "National", "High"),

    # 벨기에: Smartmatic bSmart500 + SAES-3370 혼합 운영
    # 왈로니아(253개 자치단체)는 종이투표. 계약 2027년 만료. 2029 교체 논의 중
    # 2022년 이후 기계는 BMD 모드(인쇄된 종이를 수동 개표)로 운영
    "BEL": ("Yes",   "EVM",     "Smartmatic bSmart500 / SAES-3370",
            "Smartmatic",               "GBR", "2024", "Partial",  "High"),

    # 알바니아: 국가 생체인증(VIU-818 5,538대)은 전국, EVM 파일럿만
    # 2025 의회선거: 75개 센터 51,505명 대상 A4-517 파일럿
    "ALB": ("Pilot", "EVM",     "Smartmatic A4-517",
            "Smartmatic + Innovatrics", "GBR", "2025", "Pilot",    "High"),

    # 불가리아: Smartmatic A4-517 터치스크린 DRE. Ciela Norma는 현지 통합사
    # 2022년 이후 BMD 모드(종이 출력 후 수동 개표). OMR 아님
    # 2026-01 새 광학스캐너 조달 시작(4월 선거 대비)
    "BGR": ("Yes",   "DRE",     "Smartmatic A4-517 (BMD mode since 2022)",
            "Smartmatic / Ciela Norma", "GBR", "2020", "National", "High"),

    # ── OMR (Optical Mark Recognition — 종이투표지 광학스캔) ─────────────
    # 필리핀: Miru ACM 110,620대. PHP 17.99B 계약(2024-03-11). 2025 중간선거 사용
    # 99.997% 정확도(RMA). FASTrAC 프로젝트. Smartmatic 교체
    "PHL": ("Yes",   "OMR",     "ACM (FASTrAC project)",
            "Miru Systems",             "KOR", "2024", "National", "High"),

    # 한국: Miru 투표지분류기(광학 정렬+개표). 2025-06-03 대선 사용
    # 1,378대(2013 계약). 2023년 사전투표 운용장비 약 8,500대 신규 납품
    "KOR": ("Yes",   "OMR",     "투표지분류기 (ballot sorter/counter)",
            "Miru Systems",             "KOR", "2013", "National", "High"),

    # 이라크: Miru PCOS/CCOS 광학스캐너. 2018: 약 105,000대. 2025선거 사용
    # Thales는 내무부 국가 ID 데이터센터 담당 — 투표기계와 무관
    # 2025-05 Miru FRT 카메라 추가 계약(39,285개 투표소 전체)
    "IRQ": ("Yes",   "OMR",     "PCOS/CCOS optical scanner",
            "Miru Systems",             "KOR", "2017", "National", "High"),

    # 조지아: Smartmatic SAES-1800Plus(bScan Precinct 1800Plus) 4,876대
    # 2021 파일럿 → 2024-10-26 전국 첫 배포. 99.87% 가동률
    "GEO": ("Yes",   "OMR",     "Smartmatic SAES-1800Plus (bScan1800Plus)",
            "Smartmatic",               "GBR", "2023", "National", "High"),

    # 몽골: Dominion ImageCast(Precinct급). 2012 의회 승인. 3,300대/2,198개 투표소
    # 기계·수동 집계 완전 일치 확인. Dominion → Liberty Vote 2025년 인수
    "MNG": ("Yes",   "OMR",     "Dominion ImageCast (New ImageCast)",
            "Dominion Voting Systems",  "CAN", "2012", "National", "High"),

    # 남아공: Ren-Form VMD(X-100, Champtek제)는 유권자 신원확인 전용
    # 투표지 개표는 전면 수동(수동 분류→100장 묶음→결과지 작성). OMR 아님
    # IEC 공식 확인: "투표 집계에 기술 미도입" (2024 총선)
    "ZAF": ("No",   None, None, "Ren-Form VMD (voter ID only, manual count)", None, None, None, "High"),

    # 바레인: 국가 의회선거(CoR) 개표 방식 미확인(수동 추정)
    # OMR 스캐너는 BCCI(상공회의소) 민간선거에만 사용 — 국가선거 아님
    "BHR": ("No",   None, None, "Paper ballot, likely manual count (OMR only in private BCCI elections)", None, None, None, "Med"),

    # 보스니아: Smartmatic EUR38.1M(2026-05 체결). 생체 e-pollbook 6,000대
    # + 투표지 스캐너(OMR) 6,000대. 투표는 수기 종이투표지
    "BIH": ("Yes",   "OMR",     "Smartmatic ballot scanner",
            "Smartmatic",               "GBR", "2026", "National", "High"),

    # 키르기스스탄: Miru PCOS 5-in-1 (여권바이오+지문/얼굴+투표지인쇄+광학집계)
    # 2015(KOICA/A-WEB): 3,715대. 2018 CEC 직접계약. 2025-11-30 의회선거 사용
    "KGZ": ("Yes",   "OMR",     "Miru PCOS 5-in-1",
            "Miru Systems",             "KOR", "2018", "National", "High"),

    # ── 인터넷 투표 ──────────────────────────────────────────────────────
    # 오만: 2022 지방선거부터 Intakhib 앱 도입. 2023 Shura선거 100% 모바일앱 전환
    # 물리적 투표소/EVM 없음. 벤더: uqudo+Tech5(생체인증) + Oracle OCI(클라우드)
    "OMN": ("Yes",   "Internet", "Intakhib mobile app",
            "uqudo + Tech5 / Oracle OCI", "GBR", "2023", "National", "High"),

    # UAE: Scytl 인터넷 투표 플랫폼(2011~). 2023 기준 92.7% 원격투표
    # 키오스크는 인터넷 연결 단말기(독립형 EVM 아님). FNC 20석(제한 선거)
    "ARE": ("Yes",   "Internet", "Scytl internet voting kiosk",
            "Scytl",                    "ESP", "2023", "Partial",  "High"),

    # 에스토니아: i-Voting 2005년 최초. 2023년 51.1% 온라인투표
    "EST": ("Yes",   "Internet", "i-Voting platform",
            "RIA (state)",              "EST", "2005", "National", "High"),

    # 스위스: Swiss Post e-voting 파일럿. 4개 칸톤, 유권자 약 1.4% 수준
    "CHE": ("Pilot", "Internet", "Swiss Post e-voting",
            "Swiss Post",               "CHE", "2023", "Partial",  "High"),

    # ── Mixed — 주·지역별 상이 ────────────────────────────────────────────
    # 미국: OMR 지배적(~98% 종이기반), BMD, 잔여 DRE(2026 텍사스 전면 교체 예정)
    # ES&S ~50%, Dominion ~30%, Hart ~15%
    "USA": ("Yes",   "OMR/BMD/DRE", "varies by jurisdiction",
            "ES&S / Dominion / Hart",   "USA", None,   "National", "High"),

    # 아르헨티나: BUE는 CABA(부에노스아이레스시)에서만. 전국선거는 완전 종이(BUP)
    "ARG": ("Pilot", "BMD",     "BUE (Boleta Única Electrónica)",
            "Grupo MSA",                "ARG", "2025", "Partial",  "High"),

    # 우즈베키스탄: 타슈켄트 37대, 10개 투표소 파일럿(2024-10-27). 전국 확대 미결
    # E-Saylov. 국산 추정(러시아 기술 참여 보도). 제조사 미공개
    "UZB": ("Pilot", "EVM",     "E-Saylov domestic EVM",
            "domestic (unidentified)",  "UZB", "2024", "Pilot",    "Med"),

    # ── 기계투표 없음: 생체인증 또는 결과전송만 사용 ──────────────────────
    # 카자흐스탄: Sailau EVM 2011년 공식 폐기. 2026년 현재 완전 종이투표
    "KAZ": ("No",   None, None, "Paper ballot only (Sailau EVM discontinued 2011)", None, None, None, "High"),

    # 가나: BVD(생체인증기) 사용. 투표지 개표는 전면 수동(pink sheet 방식)
    # Thales는 2020년 평가에 참여했으나 주 계약자 아님. Laxton+Neurotechnology
    "GHA": ("No",   None, None, "Laxton BVD + manual count",      None, None, None, "High"),

    # 도미니카공화국: Indra 시스템 2020년 붕괴. 2023년 스캐너 공식 폐기
    # 2024년 선거 완전 수동 개표. EDET(노트북+프린터)는 결과전송 전용
    "DOM": ("No",   None, None, "Manual count (Indra/OMR system decommissioned 2023)", None, None, None, "High"),

    # 자메이카: EVIS 생체 e-pollbook(Thales 태블릿). 투표는 종이
    "JAM": ("No",   None, None, "EVIS biometric e-pollbook (Thales)", None, None, None, "High"),

    # 케냐: Smartmatic KIEMS BVD + 결과전송. 투표·개표는 종이 수동
    "KEN": ("No",   None, None, "Smartmatic KIEMS BVD",            None, None, None, "High"),

    # 온두라스: Smartmatic VIU 생체인증. 투표는 종이 3장(대통령/국회/지방)
    "HND": ("No",   None, None, "Smartmatic VIU biometric",        None, None, None, "High"),

    # 엘살바도르: 국내선거 생체인증 미도입. DUI(주민증)로 신원확인 후 종이투표
    "SLV": ("No",   None, None, "Paper ballot + DUI verification",  None, None, None, "High"),

    # 북마케도니아: 생체지문 e-pollbook. 투표·개표는 종이
    "MKD": ("No",   None, None, "Biometric fingerprint e-pollbook", None, None, None, "High"),

    # 파나마: 전자결과전송(TER). 투표·개표는 수동. DRE 파일럿 2024년 취소
    "PAN": ("No",   None, None, "TER (electronic results only)",   None, None, None, "High"),
}


def run():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── 1. 새 컬럼 추가 ────────────────────────────────────────────────
    new_cols = [
        ("machine_voting",   "TEXT"),  # Yes / No / Pilot / N/A
        ("machine_type",     "TEXT"),  # OMR / EVM / DRE / BMD / Internet
        ("machine_model",    "TEXT"),  # 기기 모델명
        ("vendor_name",      "TEXT"),  # 표준화 업체명
        ("vendor_country",   "TEXT"),  # 업체 국가 ISO3
        ("contract_year",    "TEXT"),  # 현재 계약 기준 연도
        ("deployment_scale", "TEXT"),  # National / Partial / Pilot
    ]
    existing = {row[1] for row in cur.execute("PRAGMA table_info(countries)")}
    added = []
    for col, typ in new_cols:
        if col not in existing:
            cur.execute(f"ALTER TABLE countries ADD COLUMN {col} {typ}")
            added.append(col)
    if added:
        print(f"컬럼 추가: {', '.join(added)}")
    else:
        print("컬럼 이미 존재 — 스킵")

    # ── 2. 중복 iso3 병합 ──────────────────────────────────────────────
    print("\n[중복 제거]")
    dupes = cur.execute("""
        SELECT iso3, COUNT(*) as cnt FROM countries
        GROUP BY iso3 HAVING cnt > 1
    """).fetchall()

    for iso3, cnt in dupes:
        # notes가 더 길고 id가 낮은(먼저 입력된) 행 보존
        rows = cur.execute("""
            SELECT id, COALESCE(LENGTH(notes), 0) as nlen
            FROM countries WHERE iso3 = ?
            ORDER BY nlen DESC, id ASC
        """, (iso3,)).fetchall()
        keep_id = rows[0][0]
        del_ids = [r[0] for r in rows[1:]]
        cur.execute(
            f"DELETE FROM countries WHERE id IN ({','.join('?'*len(del_ids))})",
            del_ids
        )
        print(f"  [{iso3}] {cnt}행 → 1행 (id={keep_id} 보존, 삭제={del_ids})")

    # ── 3. 기계투표 데이터 업데이트 ───────────────────────────────────
    print("\n[기계투표 데이터 업데이트]")
    for iso3, vals in MACHINE_VOTING_DATA.items():
        mv, mt, mm, vn, vc, cy, ds, conf = vals
        cur.execute("""
            UPDATE countries
            SET machine_voting   = ?,
                machine_type     = ?,
                machine_model    = ?,
                vendor_name      = ?,
                vendor_country   = ?,
                contract_year    = ?,
                deployment_scale = ?,
                confidence       = ?,
                updated_date     = '2026-06-23'
            WHERE iso3 = ?
        """, (mv, mt, mm, vn, vc, cy, ds, conf, iso3))
        if cur.rowcount:
            print(f"  [{iso3}] {mv} | {mt or '-'} | {vn}")
        else:
            print(f"  [{iso3}] ⚠️  행 없음 — 스킵")

    # ── 4. 선거없는 국가 → N/A ─────────────────────────────────────────
    cur.execute("""
        UPDATE countries SET machine_voting = 'N/A'
        WHERE has_elections = 'N' AND machine_voting IS NULL
    """)
    print(f"\n선거없음 → N/A: {cur.rowcount}건")

    # ── 5. 나머지 종이투표 국가 → No ──────────────────────────────────
    cur.execute("""
        UPDATE countries SET machine_voting = 'No'
        WHERE machine_voting IS NULL
    """)
    print(f"종이투표 → No: {cur.rowcount}건")

    conn.commit()

    # ── 6. 결과 검증 ──────────────────────────────────────────────────
    print("\n" + "="*70)
    print("machine_voting 분포")
    print("="*70)
    for row in cur.execute("""
        SELECT machine_voting, COUNT(*) as cnt
        FROM countries GROUP BY machine_voting ORDER BY cnt DESC
    """):
        print(f"  {row[0]:10} : {row[1]}개국")

    print("\n" + "="*70)
    print("기계투표 Yes/Pilot 전체 목록")
    print("="*70)
    print(f"{'ISO3':<5} {'국가':<28} {'type':<12} {'벤더':<32} {'모델':<30} {'규모':<10} {'계약연도'}")
    print("-"*125)
    for row in cur.execute("""
        SELECT iso3, country, machine_type, vendor_name, machine_model,
               deployment_scale, contract_year
        FROM countries
        WHERE machine_voting IN ('Yes','Pilot')
        ORDER BY machine_type NULLS LAST, country
    """):
        print(
            f"[{row[0]:<4}] {row[1]:<28} {(row[2] or '-'):<12} "
            f"{(row[3] or '-'):<32} {(row[4] or '-'):<30} "
            f"{(row[5] or '-'):<10} {row[6] or '-'}"
        )

    print("\n" + "="*70)
    print("Miru Systems 납품 현황")
    print("="*70)
    for row in cur.execute("""
        SELECT iso3, country, machine_voting, machine_type, machine_model,
               contract_year, deployment_scale
        FROM countries
        WHERE vendor_name LIKE '%Miru%'
        ORDER BY country
    """):
        print(f"  [{row[0]}] {row[1]} | {row[2]} | {row[3]} | {row[4]} | 계약{row[5]} | {row[6]}")

    conn.close()
    print("\n✅ 마이그레이션 완료")


if __name__ == "__main__":
    run()
