"""
Generate election_intel_report.html — Bloomberg-style 5-panel intelligence report
Miru brand palette (#05195E navy / #EB0414 red / #E9ECF4 fog)
"""
import sqlite3, sys, json, os, base64, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

DB  = "data/election_technology_world.db"
OUT = "data/election_intel_report.html"

# ─── 로고 base64 내장 (파일 공유 시 로고 깨짐 방지) ──────────────────────────
def _logo_src():
    logo_file = "miru_white_logo_enhanced_transparent.png"
    if os.path.exists(logo_file):
        with open(logo_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{b64}"
    return ""  # 파일 없으면 빈 문자열 (로고 숨김)

LOGO_SRC = _logo_src()

# ─── Chart.js 내장 (CDN 불필요 → 오프라인 동작) ──────────────────────────────
def _chartjs():
    cdn = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"
    cache = "data/_chartjs_cache.js"
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return f.read()
    try:
        print("Chart.js 다운로드 중...", end=" ")
        with urllib.request.urlopen(cdn, timeout=10) as r:
            js = r.read().decode()
        os.makedirs("data", exist_ok=True)
        with open(cache, "w", encoding="utf-8") as f:
            f.write(js)
        print("완료")
        return js
    except Exception as e:
        print(f"실패({e}) — CDN fallback 사용")
        return None  # None이면 HTML에서 CDN script 태그 사용

CHARTJS = _chartjs()

# ─── TopoJSON client library (국가 윤곽선 지도 렌더링) ────────────────────────
def _topojson_js():
    cdn   = "https://unpkg.com/topojson-client@3/dist/topojson-client.min.js"
    cache = "data/_topojson_cache.js"
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return f.read()
    try:
        print("topojson-client 다운로드 중...", end=" ")
        with urllib.request.urlopen(cdn, timeout=15) as r:
            js = r.read().decode()
        os.makedirs("data", exist_ok=True)
        with open(cache, "w", encoding="utf-8") as f:
            f.write(js)
        print("완료")
        return js
    except Exception as e:
        print(f"실패({e})")
        return None

def _world_atlas():
    cdn   = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
    cache = "data/_worldatlas_cache.json"
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return f.read()
    try:
        print("world-atlas TopoJSON 다운로드 중...", end=" ")
        with urllib.request.urlopen(cdn, timeout=15) as r:
            data = r.read().decode()
        os.makedirs("data", exist_ok=True)
        with open(cache, "w", encoding="utf-8") as f:
            f.write(data)
        print("완료")
        return data
    except Exception as e:
        print(f"실패({e})")
        return None

TOPOJSON_JS  = _topojson_js()
WORLD_ATLAS  = _world_atlas()

# ISO 3166-1 alpha-3 → numeric (TopoJSON world-atlas feature id 매핑용)
ISO3_NUM = {
    "KOR":410,"PHL":608,"IND":356,"BTN":64,"MNG":496,
    "BEL":56,"BGR":100,"BIH":70,"GEO":268,"ALB":8,"EST":233,"CHE":756,
    "BRA":76,"USA":840,"PRY":600,"ARG":32,"VEN":862,"COD":180,
    "IRQ":368,"OMN":512,"ARE":784,"IRN":364,"KGZ":417,"UZB":860,
    "KEN":404,"NGA":566,"ZAF":710,"GHA":288,"TZA":834,"UGA":800,
    "ZMB":894,"ZWE":716,"SEN":686,"CMR":120,"SLE":694,
    "DOM":214,"JAM":388,"BGD":50,"PAK":586,"MOZ":508,
}

# ─── Miru brand palette (from brand_save.py) ─────────────────────────────────
B = {
    "primary":  "#05195E",   # navy main
    "navy80":   "#0A2A6E",
    "accent":   "#123A9E",   # navy60
    "accent2":  "#AEB7D6",   # light blue-gray
    "red":      "#EB0414",
    "green":    "#24A148",
    "charcoal": "#161616",
    "slate":    "#525252",
    "steel":    "#8C8C8C",
    "fog":      "#E9ECF4",
    "fog2":     "#F4F5FA",
    "line":     "#C7CEDC",
    "white":    "#FFFFFF",
}

# Machine type → brand color (monochromatic navy + 1 red accent)
MTYPE_COLOR = {
    "OMR":      B["primary"],
    "EVM":      B["accent"],
    "DRE":      B["red"],
    "BMD":      B["navy80"],
    "Internet": B["steel"],
    "Mixed":    B["slate"],
}

STATUS_META = {
    "Working": (B["green"],  "●", "Working"),
    "Login":   (B["accent"], "●", "Login"),
    "JS":      ("#D4870A",   "●", "JS렌더링"),
    "Dead":    (B["red"],    "●", "접근불가"),
    "Blocked": (B["steel"],  "●", "차단"),
    "Info":    (B["steel"],  "○", "정보만"),
}

# ─── All 24 machine-voting countries ─────────────────────────────────────────
COUNTRIES = [
    # iso3  name              name_ko         panel       mv      mtype     model_short                  vendor                    year   scale    conf
    ("KOR","South Korea",    "대한민국",      "apac",  "Yes",  "OMR",  "투표지분류기",                "Miru Systems",           "2013","National","High"),
    ("PHL","Philippines",    "필리핀",        "apac",  "Yes",  "OMR",  "FASTrAC ACM",                 "Miru Systems",           "2024","National","High"),
    ("IND","India",          "인도",          "apac",  "Yes",  "EVM",  "M3 EVM + VVPAT",              "BEL + ECIL",             "2013","National","High"),
    ("BTN","Bhutan",         "부탄",          "apac",  "Yes",  "EVM",  "BEL/ECIL M2 EVM",             "BEL + ECIL",             "2008","National","High"),
    ("MNG","Mongolia",       "몽골",          "apac",  "Yes",  "OMR",  "Dominion ImageCast",           "Dominion Voting Systems","2012","National","High"),
    ("BEL","Belgium",        "벨기에",        "europe","Yes",  "EVM",  "bSmart500 / SAES-3370",        "Smartmatic",             "2024","Partial", "High"),
    ("BGR","Bulgaria",       "불가리아",      "europe","Yes",  "BMD",  "A4-517 (BMD mode since 2022)", "Smartmatic / Ciela Norma","2020","National","High"),
    ("BIH","Bosnia & Herz.", "보스니아",      "europe","Yes",  "OMR",  "SAES-1800Plus Scanner",        "Smartmatic",             "2026","National","High"),
    ("GEO","Georgia",        "조지아",        "europe","Yes",  "OMR",  "SAES-1800Plus bScan",          "Smartmatic",             "2023","National","High"),
    ("ALB","Albania",        "알바니아",      "europe","Pilot","EVM",  "Smartmatic A4-517",            "Smartmatic + Innovatrics","2025","Pilot",  "High"),
    ("EST","Estonia",        "에스토니아",    "europe","Yes",  "Internet","i-Voting Platform",          "RIA (state)",            "2005","National","High"),
    ("CHE","Switzerland",    "스위스",        "europe","Pilot","Internet","Swiss Post e-voting",        "Swiss Post",             "2023","Partial", "High"),
    ("BRA","Brazil",         "브라질",        "americas","Yes","DRE",  "Urna Eletrônica UE2022",       "Positivo Tecnologia",    "2021","National","High"),
    ("USA","United States",  "미국",          "americas","Yes","Mixed","ES&S / Dominion / Hart",       "ES&S / Dominion / Hart", None,  "National","High"),
    ("PRY","Paraguay",       "파라과이",      "americas","Yes","BMD",  "BUE Boleta Única Electrónica", "Consorcio Comitia-MSA",  "2023","National","High"),
    ("ARG","Argentina",      "아르헨티나",    "americas","Pilot","BMD","BUE Boleta Única Electrónica", "Grupo MSA",              "2025","Partial", "High"),
    ("VEN","Venezuela",      "베네수엘라",    "americas","Yes","DRE",  "Smartmatic SAES3000",          "Smartmatic / Ex-Clé",    "2020","National","High"),
    ("COD","DR Congo",       "콩고민주공화국","americas","Yes","BMD",  "DEV (Dispositif Elec. Vote)",  "Miru Systems",           "2023","National","High"),
    ("ZAF","South Africa",   "남아공",        "americas","Yes","OMR",  "Champtek VMD X-100 (DRE검토중)","Ren-Form / Champtek",   "2021","National","High"),
    ("IRQ","Iraq",           "이라크",        "mena",  "Yes",  "OMR",  "PCOS/CCOS Optical Scanner",   "Miru Systems",           "2017","National","High"),
    ("OMN","Oman",           "오만",          "mena",  "Yes",  "Internet","Intakhib Mobile App",       "uqudo / Oracle OCI",     "2023","National","High"),
    ("ARE","UAE",            "아랍에미리트",  "mena",  "Yes",  "Internet","Scytl Kiosk System",        "Scytl",                  "2023","Partial", "High"),
    ("IRN","Iran",           "이란",          "mena",  "Pilot","DRE",  "Domestic EVM (pilot)",         "Domestic",               "2024","Partial", "Med"),
    ("KGZ","Kyrgyzstan",     "키르기스스탄",  "mena",  "Yes",  "OMR",  "Miru PCOS 5-in-1",            "Miru Systems",           "2018","National","High"),
    ("UZB","Uzbekistan",     "우즈베키스탄",  "mena",  "Pilot","EVM",  "E-Saylov EVM (pilot)",         "Domestic",               "2024","Pilot",   "Med"),
]

# ─── Procurement portals ──────────────────────────────────────────────────────
PORTALS = {
    "KOR": [("나라장터 G2B","https://www.g2b.go.kr/","Login",True),
            ("NEC 선관위","https://www.nec.go.kr/","Info",False)],
    "PHL": [("PhilGEPS","https://notices.philgeps.gov.ph/GEPS/Tender/SplashOpportunitiesSearchUI.aspx?menuIndex=3&ClickFrom=OpenOpp","Working",True),
            ("COMELEC 조달","https://www.comelec.gov.ph/?r=Procurement","Working",True)],
    "IND": [("CPPP / eProcure","https://eprocure.gov.in/cppp/tendersearch","Working",True),
            ("ECI Tenders","https://www.eci.gov.in/notification/tenders","Dead",False)],
    "BTN": [("e-GP Bhutan","https://www.egp.gov.bt/resources/common/TenderListing.jsp?h=t","Working",True),
            ("ECB Tender","https://www.ecb.bt/tender","Working",True)],
    "MNG": [("tender.gov.mn","https://www.tender.gov.mn/en","Dead",True),
            ("e-Tender Mongolia","https://www.e-tender.mn/en/tenders/","Dead",False)],
    "BEL": [("BOSA eProcurement","https://www.publicprocurement.be/","Working",True),
            ("e-Notification BOSA","https://enot.publicprocurement.be/enot-war/searchNotice.do","Dead",False)],
    "BGR": [("eOP (ЦАИС ЕОП)","https://app.eop.bg/today","JS",True),
            ("CIK Bulgaria","https://www.cik.bg/bg/zop","Working",False)],
    "BIH": [("eJN Bosnia","https://next.ejn.gov.ba/en/announcements/procedure-notices?page=1&rows=10&searchByIsLatestVersion=True","Working",True),
            ("CIK BiH","https://www.izbori.ba/Default.aspx?Lang=8","Info",False)],
    "GEO": [("TenderMonitor GEO","https://tendermonitor.ge/en","Working",True),
            ("SPA 공식","https://tenders.procurement.gov.ge","Login",False)],
    "ALB": [("APP e-Procurement","https://app.gov.al/contract-notice/","Working",True),
            ("KQZ Albania","https://kqz.gov.al/","Info",False)],
    "EST": [("Riigihangete Reg.","https://riigihanked.riik.ee","Working",True),
            ("Valimised.ee","https://www.valimised.ee/en","Info",False)],
    "CHE": [("SIMAP Switzerland","https://www.simap.ch/en","Working",True)],
    "BRA": [("PNCP (compras.gov)","https://pncp.gov.br/app/editais","Working",True),
            ("TSE 조달","https://www.tse.jus.br/transparencia-e-prestacao-de-contas/licitacoes-e-contratos/licitacoes","Working",True)],
    "USA": [("SAM.gov","https://sam.gov/search/?index=opp&is_active=true&q=voting+system","Working",True),
            ("EAC","https://www.eac.gov/","Info",False)],
    "PRY": [("DNCP","https://www.contrataciones.gov.py/buscador/licitaciones.html","Working",True)],
    "ARG": [("COMPR.AR","https://comprar.gob.ar","Working",True),
            ("Cámara Electoral","https://www.electoral.gob.ar","Info",False)],
    "VEN": [("SNC Venezuela","https://www.snc.gob.ve/","Working",True),
            ("CNE","https://www.cne.gob.ve/","Dead",False)],
    "COD": [("ARMP / marchepublic","https://marchepublic.cd/","Working",True),
            ("CENI","https://www.ceni.cd/","Info",False)],
    "ZAF": [("IEC VotaQuotes","https://votaquotes.elections.org.za/","Working",True),
            ("e-Tenders IEC","https://www.etenders.gov.za/","Working",False)],
    "IRQ": [("IHEC Iraq","https://ihec.iq/tenders-and-contracts/","Working",True),
            ("MoP Iraq","https://mop.gov.iq/en/general-government-contracts-department","Info",False)],
    "OMN": [("Tender Board Oman","https://etendering.tenderboard.gov.om/product/publicDash?CTRL_STRDIRECTION=LTR","Working",True)],
    "ARE": [("MoF eProcurement","https://mof.gov.ae/en/public-finance/government-procurement/current-business-opportunities/","Working",True),
            ("UAE NEC","https://uaenec.ae/en","Info",False)],
    "IRN": [("SETAD Iran","https://setadiran.ir/setad/cms","Blocked",True),
            ("MoI Iran","https://keshvar.moi.ir/","Blocked",False)],
    "KGZ": [("zakupki.gov.kg","http://zakupki.gov.kg/popp/view/order/list.xhtml","Working",True),
            ("CEC Kyrgyzstan","https://www.shailoo.gov.kg","Info",False)],
    "UZB": [("xarid.uzex.uz","https://xarid.uzex.uz/","JS",True),
            ("CEC Uzbekistan","https://saylov.uz/en","Info",False)],
}

FLAGS = {
    "KOR":"🇰🇷","PHL":"🇵🇭","IND":"🇮🇳","BTN":"🇧🇹","MNG":"🇲🇳",
    "BEL":"🇧🇪","BGR":"🇧🇬","BIH":"🇧🇦","GEO":"🇬🇪","ALB":"🇦🇱","EST":"🇪🇪","CHE":"🇨🇭",
    "BRA":"🇧🇷","USA":"🇺🇸","PRY":"🇵🇾","ARG":"🇦🇷","VEN":"🇻🇪","COD":"🇨🇩","ZAF":"🇿🇦",
    "IRQ":"🇮🇶","OMN":"🇴🇲","ARE":"🇦🇪","IRN":"🇮🇷","KGZ":"🇰🇬","UZB":"🇺🇿",
}

PANEL_META = {
    "apac":    ("Asia-Pacific","아시아·태평양",5),
    "europe":  ("Europe","유럽",7),
    "americas":("Americas & Africa","아메리카·아프리카",7),
    "mena":    ("Middle East & Central Asia","중동·중앙아시아",6),
}

# ─── Biometric e-Pollbook / ERT countries (기계투표 미도입 조달 기회국) ──────────
BTYPE_COLOR = {
    "bio":     B["green"],     # 생체인식만
    "ert":     B["accent"],    # 결과전송만
    "bio+ert": B["navy80"],    # 둘 다
}
BTYPE_LABEL = {
    "bio":     "생체인식",
    "ert":     "결과전송",
    "bio+ert": "생체+결과전송",
}

COUNTRIES_BIO = [
    # iso3  name              name_ko         btype       vendor                  system                    year  scale      conf
    ("KEN","Kenya",          "케냐",          "bio+ert",  "Smartmatic / IDEMIA",  "KIEMS (BVD + RTS)",      "2022","National","High"),
    ("NGA","Nigeria",        "나이지리아",    "bio+ert",  "Laxton Group",         "BVAS + IREV",            "2023","National","High"),
    ("GHA","Ghana",          "가나",          "bio+ert",  "Thales / HID Global",  "BVD + MARS App",         "2020","National","High"),
    ("TZA","Tanzania",       "탄자니아",      "bio",      "Idemia",               "BVR Kit",                "2020","National","Med"),
    ("UGA","Uganda",         "우간다",        "bio",      "EKEMP / Idemia",       "Biometric VR",           "2020","National","Med"),
    ("ZMB","Zambia",         "잠비아",        "bio+ert",  "Idemia",               "BVR + ERT",              "2021","National","Med"),
    ("ZWE","Zimbabwe",       "짐바브웨",      "bio",      "Laxton Group",         "BVR Kit",                "2018","National","Med"),
    ("SEN","Senegal",        "세네갈",        "bio",      "Idemia",               "생체인식 선거인명부",      "2019","National","Med"),
    ("CMR","Cameroon",       "카메룬",        "bio+ert",  "Idemia / Sopra Steria","ELECAM BVD + ERT",       "2018","National","Med"),
    ("SLE","Sierra Leone",   "시에라리온",    "bio+ert",  "Idemia",               "BVR + 결과전송",          "2023","National","Med"),
    ("DOM","Dominican Rep.", "도미니카공화국","bio+ert",  "Idemia / Smartmatic",  "Padrón + TREP",          "2020","National","High"),
    ("JAM","Jamaica",        "자메이카",      "bio",      "Thales / Gemalto",     "EOJ 생체인식 시스템",     "2020","National","Med"),
    ("BGD","Bangladesh",     "방글라데시",    "bio",      "Samsung SDS",          "NID 기반 선거인 확인",    "2021","National","Med"),
    ("PAK","Pakistan",       "파키스탄",      "bio",      "NADRA / EKEMP",        "CNIC BVM",               "2018","National","High"),
    ("MOZ","Mozambique",     "모잠비크",      "bio",      "Idemia",               "CNE 생체인식 카드",       "2019","National","Med"),
]

FLAGS_BIO = {
    "KEN":"🇰🇪","NGA":"🇳🇬","GHA":"🇬🇭","TZA":"🇹🇿","UGA":"🇺🇬",
    "ZMB":"🇿🇲","ZWE":"🇿🇼","SEN":"🇸🇳","CMR":"🇨🇲","SLE":"🇸🇱",
    "DOM":"🇩🇴","JAM":"🇯🇲","BGD":"🇧🇩","PAK":"🇵🇰","MOZ":"🇲🇿",
}

PORTALS_BIO = {
    "KEN": [("IEBC Tenders","https://www.iebc.or.ke/work/?tenders=","Working",True),
            ("e-GP Kenya","https://egpkenya.go.ke/","Working",False)],
    "NGA": [("NOCOPO Nigeria","https://nocopo.bpp.gov.ng/","Working",True),
            ("INEC 조달","https://www.inecnigeria.org/","Dead",False)],
    "GHA": [("GHANEPS","https://www.ghaneps.gov.gh/","Working",True),
            ("PPA Ghana EC","https://tenders.ppa.gov.gh/agencies/111","Dead",False)],
    "TZA": [("NeST Procurement Plans","https://nest.go.tz/annual-procurement-plans","Working",True),
            ("NeST Published Tenders","https://nest.go.tz/tenders/published-tenders","Working",False)],
    "UGA": [("EC Uganda Tenders","https://ec.or.ug/tenders","Working",True),
            ("GPP Uganda","https://gpp.ppda.go.ug/","Info",False)],
    "ZMB": [("ZPPA ECZ","https://eprocure.zppa.org.zm/epps/prepareViewCAOrganisation.do?id=19914","Working",True),
            ("ECZ Tenders","https://www.elections.org.zm/","Working",False)],
    "ZWE": [("PRAZ eGP Zimbabwe","https://egp.praz.org.zw/","Working",True),
            ("ZEC Tenders","https://www.zec.org.zw/category/tenders/","Working",False)],
    "SEN": [("Marchés Publics Sénégal","https://www.marchespublics.sn/","Dead",True),
            ("DGE Sénégal","https://dge.sn/","Info",False)],
    "CMR": [("ARMP Cameroon","https://www.armp.cm/filtres?type=avis&val=1","Working",True),
            ("ELECAM","https://portail.elecam.cm/en/","Info",False)],
    "SLE": [("ECSL Procurement","https://ec.gov.sl/procurements/","Working",True),
            ("NPPA eGP","https://egp.nppa.gov.sl/","Info",False)],
    "DOM": [("DGCP Dominican Rep.","https://www.dgcp.gob.do/","Working",True),
            ("JCE Licitaciones","https://jce.gob.do/Noticias/category/licitaciones-nacionales-1","Blocked",False)],
    "JAM": [("ECJ Tenders","https://www.ecj.com.jm/opportunities/tenders/","Working",True),
            ("GOJEP EOJ","https://www.gojep.gov.jm/epps/prepareViewCAOrganisation.do?id=1936","JS",False)],
    "BGD": [("e-GP Bangladesh","https://www.eprocure.gov.bd/resources/common/StdTenderSearch.jsp?h=t","Working",True),
            ("ECS Bangladesh","https://ecs.gov.bd/category/tender-notice","Dead",False)],
    "PAK": [("PPRA Pakistan","https://epms.ppra.gov.pk/public/tenders/active-tenders","Working",True),
            ("ECP Tenders","https://ecp.gov.pk/tenders","Blocked",False)],
    "MOZ": [("UFSA Mozambique","https://www.ufsa.gov.mz/concursos.php","Dead",True),
            ("Portal Contratações","http://www.contratacoes.gov.mz/","Dead",False)],
}

# ─── Contract Intelligence (워크플로우 리서치 결과 2026-06-25) ────────────────
# tier: CRITICAL(≤2026) / WATCH(2027) / MONITOR(2028-2029) / LONG(2030+) / UNKNOWN
CONTRACT_DATA = {
    "PRY": {"tier":"CRITICAL", "next_tender":"2027",      "contract_end":"2026",          "contract_type":"lease",    "notes":"임대 계약 10월 종료 → 2028 총선 입찰 예정. Miru 기존 참여사."},
    "ARG": {"tier":"CRITICAL", "next_tender":"2027",      "contract_end":"2025",          "contract_type":"service",  "notes":"CABA 선거별 서비스 계약(MSA 단독입찰 ~$22M) → 2027 재입찰."},
    "ARE": {"tier":"CRITICAL", "next_tender":"2026-2027", "contract_end":"2023",          "contract_type":"service",  "notes":"FNC 선거별 계약 (Scytl 4연속) → 2027 FNC 선거 입찰 2026년 개시."},
    "OMN": {"tier":"CRITICAL", "next_tender":"2026-2027", "contract_end":"unknown",       "contract_type":"service",  "notes":"Shura 4년 주기 → 2027 선거 입찰 예상. Iraq 생체카메라 레퍼런스 활용 가능."},
    "PHL": {"tier":"WATCH",    "next_tender":"2027",      "contract_end":"2025",          "contract_type":"lease",    "notes":"Miru P17.99B 임대 완료 → COMELEC 2028 ACM 입찰 2027년 예정 (4월 기술전시회 완료)."},
    "BEL": {"tier":"WATCH",    "next_tender":"2026-2027", "contract_end":"2027",          "contract_type":"service",  "notes":"Smartmatic 15년 계약(2012) 만료 예정 → 2029 선거용 재입찰. EU 조달법 적용."},
    "BGR": {"tier":"WATCH",    "next_tender":"2026-2027", "contract_end":"2024",          "contract_type":"purchase", "notes":"소프트웨어 보증 만료 → Ciela Norma 단독계약 대체 입법 논의중."},
    "CHE": {"tier":"WATCH",    "next_tender":"2027-2028", "contract_end":"2027",          "contract_type":"pilot",    "notes":"Swiss Post 연방 라이선스 2027년 6월 만료 → 재심사. 경쟁입찰 없음."},
    "BRA": {"tier":"WATCH",    "next_tender":"2027",      "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"UE2028 공청회 진행중(2026.6) → 2027 공식 입찰. 22만대 규모. 국내 JV 필요."},
    "GEO": {"tier":"MONITOR",  "next_tender":"2027-2028", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"선거별 Smartmatic 조달(2025 $2.3M 추가) → 2028 의회선거 입찰."},
    "ALB": {"tier":"MONITOR",  "next_tender":"2027-2029", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"EU 자금 $20M EVM 파일럿 → 전국 확대 미결정. 2027 지방/2029 의회."},
    "MNG": {"tier":"MONITOR",  "next_tender":"2026-2028", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"2012년 Dominion 장비 14년 경과 → Liberty Vote 브랜드 변경이 진입 기회."},
    "KOR": {"tier":"MONITOR",  "next_tender":"2027-2030", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"10년 주기 교체 (2013→2022) → 다음 교체 2027-2030. KRW 32.5B 규모."},
    "COD": {"tier":"MONITOR",  "next_tender":"2027-2028", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"Miru $250M+ 장비 보유 → 2028 총선 교체/추가 조달. AS 계약 진행중."},
    "IRQ": {"tier":"MONITOR",  "next_tender":"2028-2029", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"Miru ~$135M 장비 보유 → 2025년 생체카메라 추가. 10년 주기 2028-2029."},
    "ZAF": {"tier":"MONITOR",  "next_tender":"2027-2030", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"VMD 2024 선거 오작동 → 교체 압박. DRE 도입 Green Paper 2026 결정 예정."},
    "KGZ": {"tier":"MONITOR",  "next_tender":"2028-2030", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"Miru KOICA 자금 PCOS 5-in-1 → 2025 선거 재사용. 10년 수명 2028-2030."},
    "BIH": {"tier":"LONG",     "next_tender":"2029-2030", "contract_end":"2030",          "contract_type":"purchase", "notes":"2026년 체결 4년 계약 74.5M BAM(38M EUR) → 2030 만료."},
    "IND": {"tier":"LONG",     "next_tender":"2027-2030", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"국영제조사(BEL/ECIL) 직발주 → 민간입찰 없음. M3A 도입중."},
    "BTN": {"tier":"LONG",     "next_tender":"2027-2028", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"2008/2013 BEL/ECIL 장비 18년 경과 → 2028 선거 전 교체. 인도 재조달 예상."},
    "EST": {"tier":"LONG",     "next_tender":"unknown",   "contract_end":"owned/ongoing", "contract_type":"service",  "notes":"국가직영 오픈소스 i-Voting → Miru 진입 불가."},
    "USA": {"tier":"LONG",     "next_tender":"2027-2030", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"카운티별 10년 교체 물결 2027-2030. GA Dominion(Liberty Vote) 2029 만료."},
    "VEN": {"tier":"LONG",     "next_tender":"2030-2031", "contract_end":"owned/ongoing", "contract_type":"purchase", "notes":"OFAC 제재 ExClé 운영 → 불투명 조달. 다음 대선 2031."},
    "IRN": {"tier":"UNKNOWN",  "next_tender":"unknown",   "contract_end":"unknown",       "contract_type":"pilot",    "notes":"소규모 파일럿 (4-8개 선거구) → 제재 환경. 진입 불가."},
    "UZB": {"tier":"UNKNOWN",  "next_tender":"2027-2028", "contract_end":"unknown",       "contract_type":"pilot",    "notes":"37대 파일럿(2024) → 2029 의회선거 전 본격 입찰 예상 2027-2028."},
}

TIER_META = {
    "CRITICAL": (B["red"],     "즉시 대응",  "🔴"),
    "WATCH":    ("#D4870A",    "제안 준비",  "🟠"),
    "MONITOR":  ("#4d9fff",    "모니터링",  "🔵"),
    "LONG":     (B["steel"],   "장기 관찰",  "⚫"),
    "UNKNOWN":  (B["accent2"], "정보 부족",  "⬜"),
}

# ─── Vendor Intelligence (워크플로우 리서치 결과 2026-06-25) ──────────────────
# overlap: Direct=경쟁사, Indirect=시장 겹침, None=비경쟁
VENDOR_DATA = [
    {
        "slug":"smartmatic","name":"Smartmatic","flag":"🇬🇧",
        "homepage":"https://www.smartmatic.com",
        "products_url":"https://www.smartmatic.com/elections/",
        "hq":"London, UK","type":"Private","parent":"SGO Corporation Limited",
        "founded":"2000","employees":"~600","revenue":"~$175M",
        "countries_count":24,
        "key_products":["bSmart BMD 100/155","SAES-1800plus VCM","EMS/EMP Platform","TIVI Internet Voting","VIU-500 Biometric Kit"],
        "categories":["BMD","DRE","OMR","Biometric","Internet","EMS"],
        "overlap":"Indirect","overlap_markets":["PHL"],
        "strengths":[
            "35+개국 65억 표 처리 — 세계 최대 선거기술 풋프린트",
            "BMD·OMR·생체인식·인터넷투표 엔드투엔드 포트폴리오",
            "VVSG 2.0 최초 제출 — EAC 인증 공신력",
        ],
        "weaknesses":[
            "SGO Corporation 형사기소(FCPA, 2025.10) — 필리핀 뇌물 혐의, 기각신청 계류중",
            "필리핀 시장 영구 상실 — COMELEC 2023 자격박탈 (Miru 2025 수주)",
            "미국 시장 Dominion 비경쟁 조항으로 사실상 LA카운티 단독만 가능",
        ],
        "news":"FCPA 기소(2025.10) 기각신청 계류 / Newsmax 명예훼손 $40M 합의(2024) / Fox News 재판 2026년 예정",
        "confidence":"High",
    },
    {
        "slug":"liberty_vote","name":"Liberty Vote (구 Dominion)","flag":"🇺🇸",
        "homepage":"https://libertyvote.com",
        "products_url":"https://libertyvote.com",
        "hq":"Denver, CO, USA","type":"Private","parent":None,
        "founded":"2003","employees":"~250","revenue":"~$100M",
        "countries_count":2,
        "key_products":["ImageCast X BMD","ImageCast Precinct 2 OMR","ImageCast Central","Democracy Suite EMS","Frontier 1.0 (VVSG 2.0 제출중)"],
        "categories":["OMR","BMD","DRE","EMS"],
        "overlap":"None","overlap_markets":[],
        "strengths":[
            "미국 등록유권자 25% 커버 — 27개 주 최대 설치기반",
            "KNOWiNK 인수로 e-pollbook 포함 40개 주 통합 플랫폼",
            "Frontier 1.0 VVSG 2.0 EAC 제출(2025.11) — 차기 조달 포지셔닝",
        ],
        "weaknesses":[
            "2020 음모론 $787.5M 합의 이후 브랜드 독성 여전",
            "국제시장 사실상 전무 — 필리핀 2025 응찰조차 못 함",
            "리브랜딩 후 신규계약 아직 없음",
        ],
        "news":"2025.10 Dominion → Liberty Vote 리브랜딩 / 2025.11 Frontier 1.0 EAC VVSG 2.0 제출 / 2026.2 전 WA 장관 Kim Wyman 영입",
        "confidence":"High",
    },
    {
        "slug":"ess","name":"ES&S (Election Systems & Software)","flag":"🇺🇸",
        "homepage":"https://www.essvote.com",
        "products_url":"https://www.essvote.com/products/",
        "hq":"Omaha, NE, USA","type":"Private","parent":"M-One Capital",
        "founded":"1979","employees":"~700","revenue":"~$120M",
        "countries_count":6,
        "key_products":["DS300/450/950 OMR 스캐너","ExpressVote BMD","ExpressVote XL","Electionware EMS","EVS 7.0 (VVSG 2.0 인증 2026.3)"],
        "categories":["OMR","BMD","DRE","e-Pollbook","EMS"],
        "overlap":"Indirect","overlap_markets":["PHL"],
        "strengths":[
            "미국 시장 점유율 50~60% — 42개 주 4,500개 지자체",
            "투표등록·e-pollbook·OMR·BMD·개표 풀스택 번들",
            "EVS 7.0 VVSG 2.0 EAC 인증(2026.3) — 최신 표준 최초 인증",
        ],
        "weaknesses":[
            "보안 취약점 지속 — 원격접속 프리인스톨(2018), 중국산 부품 우려",
            "텍사스 e-pollbook 인증 취소(2024.12) — 댈러스 오인쇄 사고",
            "보안 연구자 소송 — 독립감사 저해, 비당파 양쪽 비판 대상",
        ],
        "news":"2024.12 텍사스 e-pollbook 인증취소 / 2025.12 EVS 7.0 EAC 제출 / 2026.3 VVSG 2.0 인증 승인",
        "confidence":"High",
    },
    {
        "slug":"hart","name":"Hart InterCivic","flag":"🇺🇸",
        "homepage":"https://www.hartintercivic.com",
        "products_url":"https://www.hartintercivic.com/hybrid/",
        "hq":"Austin, TX, USA","type":"Private","parent":"Enlightenment Capital",
        "founded":"1912","employees":"~100~150","revenue":"~$30~43M",
        "countries_count":1,
        "key_products":["Verity Vanguard 1.0 (VVSG 2.0 최초 인증)","Vanguard Flex BMD","Vanguard Vault OMR","Verity Count 개표소프트웨어"],
        "categories":["OMR","BMD","DRE","EMS"],
        "overlap":"None","overlap_markets":[],
        "strengths":[
            "세계 최초 VVSG 2.0 EAC 인증(2025.7) — 규제 선점",
            "바코드 없는 완전 사람이 읽을 수 있는 용지 — EO 14248 완전 준수",
            "20개 주 100년+ 관계",
        ],
        "weaknesses":[
            "미국 단일 시장 — 국제 진출 없음",
            "매출 $30~43M 소형사 — R&D 투자 한계",
            "미국 시장 점유율 15% — ES&S/Dominion 대비 열세",
        ],
        "news":"2025.7 Vanguard VVSG 2.0 최초 인증 / 2026.1 워싱턴·미시시피 첫 배포 / 2026.4 텍사스 6번째 주 인증",
        "confidence":"High",
    },
    {
        "slug":"msa","name":"Grupo MSA / Comitia-MSA","flag":"🇦🇷",
        "homepage":"https://www.msa.com.ar",
        "products_url":"https://www.scytl.com",
        "hq":"Buenos Aires, Argentina","type":"Private","parent":None,
        "founded":"1995","employees":"~100+","revenue":"~$5.8M (계약 외)",
        "countries_count":3,
        "key_products":["Vot.ar / BUE 전자투표용지","Scytl InVote Gov 인터넷투표","sVote (스위스 e-voting)","선거결과 관리 플랫폼"],
        "categories":["BMD","Internet","Software"],
        "overlap":"Indirect","overlap_markets":["ARG","PRY"],
        "strengths":[
            "아르헨티나 BUE 시장 25년 지배 — CABA 등 11개 이상 주",
            "2024.6 Scytl 인수로 1,000+ 미국 고객, 4개 대륙 IP 확보",
            "RFID 칩+종이 혼합 BUE — 감사 내역서 제공, ISO 9001 인증",
        ],
        "weaknesses":[
            "기술 장애 반복 — 2023 CABA PASO '30년 최악' 판사 판정",
            "RFID 스마트폰 투표 증식 취약점, SSL 인증서 유출(2015)",
            "단독입찰 반복 패턴 — 파라과이 2025 불법시비 논란",
        ],
        "news":"2024.6 Scytl 인수 / 2025.5 CABA $22M 단독입찰 / 2025.12 파라과이 $35M 단독낙찰 논란",
        "confidence":"High",
    },
    {
        "slug":"scytl","name":"Scytl / Civica Election Services","flag":"🇪🇸",
        "homepage":"https://www.scytl.com",
        "products_url":"https://www.scytl.com/online-voting/invote/gov/",
        "hq":"Barcelona (Scytl) / London (Civica)","type":"Subsidiary","parent":"Comitia MSA / Civica Group (Blackstone)",
        "founded":"2001","employees":"~125+200","revenue":"~$44M+$35M",
        "countries_count":30,
        "key_products":["Invote Gov 인터넷투표","SOE Software ENR","CESvotes 온라인투표(Civica)","Xpress EMS(Civica)","eBallot Delivery"],
        "categories":["Internet","Software"],
        "overlap":"Indirect","overlap_markets":["ARE","PRY"],
        "strengths":[
            "암호화 인터넷투표 50+ 특허, 25년 R&D 선점",
            "SOE Software — 미국 24개 주 1,300개 선거구 ENR 제공",
            "UAE FNC 4연속(2006~) — 세계 최초 100% 디지털 국가선거 레퍼런스",
        ],
        "weaknesses":[
            "노르웨이 2013 이중투표 취약점, 호주 2015 iVote 취약점으로 계약 상실",
            "2020년 파산(채무 €75M) — 2번의 소유권 변경으로 신뢰도 손상",
            "유럽·미국에서 인터넷투표 감사가능성 반대 여론 확산",
        ],
        "news":"2024.6 COMITIA MSA에 인수 / 2025.12 파라과이 $35M 계약(BUE+인터넷투표)",
        "confidence":"Med",
    },
    {
        "slug":"positivo","name":"Positivo Tecnologia","flag":"🇧🇷",
        "homepage":"https://www.positivotecnologia.com.br/en/",
        "products_url":"https://www.positivotecnologia.com.br/en/about-us/",
        "hq":"Curitiba, Brazil","type":"Public","parent":"Grupo Positivo",
        "founded":"1989","employees":"~8,400","revenue":"~$700M",
        "countries_count":1,
        "key_products":["UE2022 DRE 투표기","UE2020 DRE","생체인식 리더 HID DP5360","메사리우 단말 키보드"],
        "categories":["DRE","EVM","Biometric"],
        "overlap":"None","overlap_markets":[],
        "strengths":[
            "브라질 TSE 유일 DRE 제조사 — 2020 이후 독점 (Smartmatic/Diebold 낙찰가 절반)",
            "국내 공장(Ilhéus·Manaus) 수직통합 — 가격경쟁력 + 국가안보 조달 우선",
            "TSE 공동개발 파트너십 — 하드웨어/펌웨어 Positivo, 앱소프트웨어 TSE",
        ],
        "weaknesses":[
            "브라질 단일 시장 — 국제 수출 없음",
            "순이익 R$85M(2024)→R$12M(2025) 급감, 공공기관 매출 34.7% 감소",
            "DRE 외 제품(OMR·BMD·인터넷투표) 없음",
        ],
        "news":"FY2025 매출 R$4.0B / 순이익 R$12M(86% 감소) / UE2026 신규입찰 미발표",
        "confidence":"High",
    },
    {
        "slug":"bel_india","name":"BEL (Bharat Electronics Limited)","flag":"🇮🇳",
        "homepage":"https://bel-india.in",
        "products_url":"https://bel-india.in/product/electronic-voting-machine/",
        "hq":"Bengaluru, India","type":"State-owned","parent":"Ministry of Defence (51.14%)",
        "founded":"1954","employees":"~9,000~11,200","revenue":"~$3.3B",
        "countries_count":7,
        "key_products":["EVM M3 Control Unit","EVM M3 Ballot Unit","VVPAT M3"],
        "categories":["EVM","DRE","VVPAT"],
        "overlap":"None","overlap_markets":[],
        "strengths":[
            "세계 최대 민주주의 인도 9억 유권자 선거 EVM 독점 공급",
            "국방부 산하 Navratna PSU — 진입장벽 극히 높음",
            "나미비아·네팔·부탄·피지·케냐·보츠와나 외교 채널 수출",
        ],
        "weaknesses":[
            "EVM 보안 투명성 비판 — 소프트웨어 감사보고서 공개 거부",
            "선거기술은 전체 매출 소수 — R&D·수출 인프라 취약",
            "국제 수출 전체 매출의 0.5% 미만 — 상업 영업력 부족",
        ],
        "news":"FY2026 매출 ₹27,480크로르(~$3.3B) 신기록 / 수출 33.65% 증가 $141.9M — 방산 위주",
        "confidence":"Med",
    },
    {
        "slug":"ecil","name":"ECIL (Electronics Corporation of India)","flag":"🇮🇳",
        "homepage":"https://www.ecil.co.in",
        "products_url":"https://www.ecil.co.in/iteg_evm",
        "hq":"Hyderabad, India","type":"State-owned","parent":"Dept. of Atomic Energy",
        "founded":"1967","employees":"~3,000~5,000","revenue":"~$290M",
        "countries_count":4,
        "key_products":["M3-EVM","VVPAT","Multi-Post EVM","EMS 2.0","S3-EVM (2025년 공개)"],
        "categories":["EVM","DRE","Software"],
        "overlap":"None","overlap_markets":[],
        "strengths":[
            "BEL과 50:50 인도 ECI 공급 독점 — 포획된 시장",
            "EMS 2.0 클라우드 네이티브 + SMF 2.0 보안제조 소프트웨어",
            "Miniratna Category-I 지위 부여(2025.5) — 재무 자율성 향상",
        ],
        "weaknesses":[
            "해외수출 인도-G2G 외교 채널 의존 — 독립 영업력 없음",
            "EVM 기술 특수 목적 설계 — OMR/BMD 국제 입찰 미적용",
            "S3-EVM 공개(2025.3) 외 국제 시장 진출 계획 없음",
        ],
        "news":"2025.3 S3-EVM 공개 / 2025.5 Miniratna Category-I 승격 / FY2025 매출 ₹2,426크로르",
        "confidence":"Med",
    },
    {
        "slug":"swiss_post","name":"Swiss Post e-voting","flag":"🇨🇭",
        "homepage":"https://swisspost-digital.ch/en/solutions/e-voting",
        "products_url":"https://swisspost-digital.ch/en/solutions/e-voting/the-e-voting-solution-for-cantons",
        "hq":"Bern, Switzerland","type":"State-owned","parent":"Swiss Post (스위스 연방 100%)",
        "founded":"2014","employees":"~45,000(그룹)/~12(e-voting팀)","revenue":"~$8.5B(그룹)",
        "countries_count":1,
        "key_products":["sVote 인터넷투표 시스템","Universal Verifiability 검증SW","eCH 캔톤 연동 API"],
        "categories":["Internet"],
        "overlap":"None","overlap_markets":[],
        "strengths":[
            "완전 오픈소스 공개 — 수학적 검증 가능 유일 국가급 시스템",
            "범용 검증가능성(Universal Verifiability) 최초 운용 — 연 Public Intrusion Test",
            "스위스 연방 소유 — 상업 압력 없음, CHF 25만 버그바운티",
        ],
        "weaknesses":[
            "스위스 단일 시장 — 4/26개 캔톤만 활성화, 국제 수출 없음",
            "2019~2023 중단 이력(암호화 결함) — 취리히·추크 등 주요 캔톤 불참",
            "인터넷투표 전용 — OMR·EVM·BMD·생체인식 없음",
        ],
        "news":"2025.6 연방 기본라이선스 4개 캔톤 2027까지 갱신 / 2025 PIT 4회 침투 성공 없음 / 2026.3 투르가우 주민투표 확대",
        "confidence":"High",
    },
    {
        "slug":"cybernetica","name":"Cybernetica AS","flag":"🇪🇪",
        "homepage":"https://cyber.ee",
        "products_url":"https://cyber.ee/resources/news/first-of-a-kind-global-centre-of-excellence-to-advance-internet-voting/",
        "hq":"Tallinn, Estonia","type":"Private","parent":None,
        "founded":"1997","employees":"~230","revenue":"~$16M",
        "countries_count":1,
        "key_products":["IVXV 인터넷투표 시스템(에스토니아)","m-Voting 모바일(2025 파일럿)","SplitKey+ 디지털 ID인증"],
        "categories":["Internet","Software"],
        "overlap":"None","overlap_markets":[],
        "strengths":[
            "20년 유일한 법적 구속력 국가 인터넷투표 운영(에스토니아, 2023년 51%)  ",
            "IVXV 오픈소스 투명성 — 독립 감사 가능",
            "40개국 UXP/X-Road 생태계 — i-voting 컨설팅 수출 파이프라인",
        ],
        "weaknesses":[
            "에스토니아 단일 국제 운용 — Smartmatic-Cybernetica JV 매출 €56만/년",
            "Springall/Halderman 2014 감사 절차적 취약 지적 / 2024 EP선거 첫 오류 발생",
            "~230명 소형사 — EU SME 보조금 유지를 위해 250명 상한 자체 제한",
        ],
        "news":"2025.5 m-Voting iOS/Android 공개 파일럿 / 2025.11 양자내성암호 전환 3개 계약 수주 / CEO '2026이 가장 기회 많은 해'",
        "confidence":"High",
    },
    {
        "slug":"idemia","name":"IDEMIA (→ IN Groupe / Amadeus)","flag":"🇫🇷",
        "homepage":"https://www.idemia.com",
        "products_url":"https://www.idemia.com/enrollment-and-authentication",
        "hq":"Courbevoie, France","type":"Private","parent":"Advent International (분할 중)",
        "founded":"2017","employees":"~15,000","revenue":"~$3.1B",
        "countries_count":9,
        "key_products":["MorphoTablet 2S 생체인식 태블릿","KIEMS(케냐 통합선거관리)","RAVEC(말리 시민ID/유권자등록)","BVR 키트","MSO 시리즈 지문스캐너"],
        "categories":["Biometric","Software","BVR"],
        "overlap":"Indirect","overlap_markets":["KEN","NGA","GHA","CIV","COD"],
        "strengths":[
            "아프리카 54개국 중 35개국+ 생체선거기술 — 최대 아프리카 풋프린트",
            "NIST 지문 전 벤치마크 1위(2025.3) — 정부조달 공신력",
            "ID스크린 태블릿 17만대 이상 배포 — 방대한 설치기반 락인",
        ],
        "weaknesses":[
            "케냐 IEBC '노예 상태' 발언 — 지식이전 거부 비판 / 2017 KIEMS 실패 → 대통령선거 무효",
            "프랑스 검찰 뇌물수사 진행중(2022~ 카메룬·DRC·가봉·니제르·세네갈·우간다)",
            "분사 진행 — Smart Identity→IN Groupe(2025.7), IPS→Amadeus(2026.4 발표)",
        ],
        "news":"2025.7 Smart Identity 부문 IN Groupe에 ~€1B 매각 / 2026.4 IPS 부문 Amadeus €1.2B 인수 발표(2027 완료 예정)",
        "confidence":"High",
    },
    {
        "slug":"thales","name":"Thales Group (DIS / 구 Gemalto)","flag":"🇫🇷",
        "homepage":"https://www.thalesgroup.com",
        "products_url":"https://www.thalesgroup.com/en/solutions-catalogue/public-security/civil-identity/election-suite",
        "hq":"La Défense, Paris, France","type":"Public (EPA:HO)","parent":None,
        "founded":"1893","employees":"~85,000","revenue":"~$24B",
        "countries_count":15,
        "key_products":["Thales Election Suite","Coesys Mobile Enrollment Station","Thales ABIS","DactyScan84c 생체인식 스캐너"],
        "categories":["Biometric","Software"],
        "overlap":"Indirect","overlap_markets":["COD","GHA","PHL"],
        "strengths":[
            "15개국+ 생체선거 배포 — 세계 최대 생체선거 벤더",
            "20년+ Gemalto 유산으로 프랑코폰 아프리카 깊은 관계",
            "€22B 그룹 규모 — 여권·국민ID→유권자등록 크로스셀",
        ],
        "weaknesses":[
            "Gemalto 자회사 프랑스 사법조사(2022~) — 카메룬·DRC 등 뇌물 혐의",
            "투표기계(OMR·EVM·BMD) 없음 — 생체인식/유권자등록만",
            "방산·항공·사이버 등 전방위 대기업 — 선거기술 전문 집중도 낮음",
        ],
        "news":"FY2025 €22.1B 매출 신기록 / Gemalto 프랑스 사법조사 지속(2022~) / HID Global 신분증 부문 Toppan에 매각(2025.1)",
        "confidence":"High",
    },
    {
        "slug":"laxton","name":"Laxton Group (→ DNP 자회사)","flag":"🇳🇱",
        "homepage":"https://www.laxton.com",
        "products_url":"https://www.laxton.com/solutions/biometric-voter-id",
        "hq":"The Hague, Netherlands","type":"Subsidiary","parent":"Dai Nippon Printing (75% 인수 2025.6)",
        "founded":"2004","employees":"~201","revenue":"~$35M",
        "countries_count":14,
        "key_products":["Chameleon D 다중생체인식 태블릿","BRK 생체인식 등록 키트","Athena 신원관리 플랫폼","ePoll Book","PVC 선거인 ID카드 즉시발급"],
        "categories":["Biometric","Software"],
        "overlap":"Indirect","overlap_markets":["MOZ","ZWE","GHA","TZA","LBR"],
        "strengths":[
            "20년+ 50개국 3억명+ 생체등록 — 아프리카 ECO 브랜드 인지도 1위",
            "하드웨어+소프트웨어 자체 설계/제조(2만㎡ 공장) — 공급망 통제",
            "DNP 인수($9.5B 부모사) + MOSIP SI 인증(2026.3) — 세계은행·UN 파이프라인",
        ],
        "weaknesses":[
            "투표집계 기계(OMR·EVM·BMD) 없음 — 유권자등록/인증만",
            "라이베리아 계약 논란(2022~2023 2회 거부 후 3번째 낙찰)",
            "DNP 인수 전 $35M 소형사 — 다국가 동시 대규모 배포 역량 제한",
        ],
        "news":"2025.6 DNP 75% 지분 인수 / 2026.3 MOSIP SI 파트너 인증 / 2026.4 마다가스카르 250만명 생체등록 풀배포",
        "confidence":"High",
    },
    {
        "slug":"innovatrics","name":"Innovatrics","flag":"🇸🇰",
        "homepage":"https://www.innovatrics.com",
        "products_url":"https://www.innovatrics.com/voter-registration/",
        "hq":"Bratislava, Slovakia","type":"Private","parent":None,
        "founded":"2004","employees":"~210","revenue":"~$18M",
        "countries_count":7,
        "key_products":["Innovatrics ABIS 자동생체식별","Voter Management Platform","DOT 디지털온보딩 SDK","SmartFace 안면인식"],
        "categories":["Biometric","ABIS","Software"],
        "overlap":"Indirect","overlap_markets":["GIN","UGA","ALB"],
        "strengths":[
            "NIST ELFT 잠재지문 정확도 1위(2025.1) + 안면인식 상위 3위",
            "하드웨어 무관 클라우드 ABIS — 1억 인구 단일 AWS 인스턴스 처리",
            "MOSIP 컴플라이언트 ABIS(2026.6) — 29개국 GovStack 파이프라인",
        ],
        "weaknesses":[
            "소프트웨어/생체인식 전용 — 시스템통합사(Smartmatic 등)에 납품 구조",
            "~210명 소형사 — 다국가 동시 배포 역량 제한",
            "투표기계 없음 — 고부가 하드웨어 계약 참여 불가",
        ],
        "news":"2025.1 NIST 지문 1위 탈환 / 2026.5 UIDAI 안면인식 챌린지 1위 / 2026.6 MOSIP 컴플라이언트 + 브라티슬라바 Biometrics House 신사옥",
        "confidence":"Med",
    },
    {
        "slug":"tech5","name":"uqudo / TECH5","flag":"🇨🇭",
        "homepage":"https://tech5.ai",
        "products_url":"https://tech5.ai/uqudo-tech5-free-fair-elections/",
        "hq":"Geneva (TECH5) / Manchester (uqudo)","type":"Private","parent":None,
        "founded":"2018","employees":"~120","revenue":"비공개",
        "countries_count":1,
        "key_products":["Antakhib/Intakhib 모바일 생체인증 선거앱","T5-OmniMatch ABIS","T5-AirSnap 비접촉 안면/지문캡처","NFC 생체ID 리더"],
        "categories":["Biometric","Internet","Software"],
        "overlap":"Indirect","overlap_markets":["OMN"],
        "strengths":[
            "NIST 최상위 생체인식 알고리즘(지문·안면·홍채)",
            "오만 2022/2023 국가선거 NFC+생체 원격투표 실증 — 유일 벤더",
            "창업자 Aadhaar(13억)/인도네시아 국민ID(1.93억) 경력 — 정부급 스케일 신뢰",
        ],
        "weaknesses":[
            "선거 레퍼런스 오만 단일 — 국제 확장 아직 없음",
            "~120명 소형사 — 대규모 동시 배포 역량 제한",
            "법집행(버지니아 $54M)·DPI가 주 사업 — 선거기술 2차적 포지셔닝",
        ],
        "news":"2026.1 Salica Investments 성장대출 확보 / 2026.3 NIST FRIF 지문 새 벤치마크 / 이라크 거주자 ID 지원(2025.8)",
        "confidence":"Med",
    },
    {
        "slug":"champtek","name":"Champtek Inc.","flag":"🇹🇼",
        "homepage":"https://www.champtek.com",
        "products_url":"https://www.champtek.com/en/product/136",
        "hq":"New Taipei City, Taiwan","type":"Private","parent":None,
        "founded":"1985","employees":"11~50","revenue":"비공개",
        "countries_count":1,
        "key_products":["X-100 10.1인치 VMD(유권자관리단말)","X-55/X-80/X-120/X-130 시리즈","Z Series 생체키트","십지문 롤스캐너"],
        "categories":["Biometric","OMR","Software"],
        "overlap":"Indirect","overlap_markets":["ZAF"],
        "strengths":[
            "하드웨어 전용 제조 — 모듈식 생체인식(NFC·홍채·안면·지문) 통합 가능",
            "CHAMPTEK·SCANTECH ID 이중 브랜드 30개국+ 유통망",
            "FBI 인증 지문, AFIS/ABIS 지원 — 정부 조달 공신력",
        ],
        "weaknesses":[
            "남아공 IEC X-100 VMD 2021·2024 선거 모두 현장 중단 — 레퍼런스 손상",
            "11~50명 극소형사 — 대규모 동시 배포 역량 극히 제한",
            "Ren-Form 유통사 의존 — 짐바브웨 스캔들 등 유통사 리스크 전이",
        ],
        "news":"2026.6 Computex 타이페이 / 2026.8 타이페이 물류·IoT 전시회 — 남아공 IEC 재입찰 결정 미발표",
        "confidence":"Med",
    },
    {
        "slug":"samsung_sds","name":"Samsung SDS","flag":"🇰🇷",
        "homepage":"https://www.samsungsds.com/en/index.html",
        "products_url":"https://www.samsungsds.com/us/en/solutions/bns/Digital/Identity-platform.html",
        "hq":"Seoul, South Korea","type":"Public (KRX:018260)","parent":"Samsung Group",
        "founded":"1985","employees":"~26,000","revenue":"~$10.1B",
        "countries_count":0,
        "key_products":["Nexsign 생체인증(기업/은행용)","Nexledger 블록체인","FabriX 생성AI","Samsung Cloud Platform"],
        "categories":["Software","Biometric"],
        "overlap":"None","overlap_markets":[],
        "strengths":[
            "삼성그룹 브랜드 + 계열사 안정 수요 — 한국 MSP 점유율 1위",
            "AI·클라우드 풀스택(SCP·FabriX·Brity Works) + KRX 1.22조원 KKR 투자(2026.4)",
            "방글라데시 NID 기반 선거인 확인 레퍼런스",
        ],
        "weaknesses":[
            "삼성 계열사 매출 의존도 — 독립 국제 경쟁력 제한",
            "선거기술 전용 포트폴리오 없음 — Nexsign은 기업/은행 용도",
            "아태 외 국제 브랜드 인지도 낮음",
        ],
        "news":"2026.4 KKR KRW 1.22조(~$820M) 전환사채 투자 / 2026.4 국회 AI 입법지원 플랫폼 / FY2025 매출 KRW 13.93조(+0.7%)",
        "confidence":"High",
    },
    {
        "slug":"sopra_steria","name":"Sopra Steria","flag":"🇫🇷",
        "homepage":"https://www.soprasteria.com",
        "products_url":"https://www.soprasteria.com/industries/government",
        "hq":"Paris, France","type":"Public (EPA:SOP)","parent":None,
        "founded":"2014","employees":"~51,000","revenue":"~$6.0B",
        "countries_count":1,
        "key_products":["EU Shared Biometric Matching System(sBMS·IDEMIA 협력)","FAED V3 프랑스 형사지문DB","선거야간 출구조사 플랫폼(Ipsos 협력)"],
        "categories":["Software","Biometric"],
        "overlap":"None","overlap_markets":[],
        "strengths":[
            "유럽 공공기관 IT 톱5 — 프랑스·영국·EU 기관 깊은 관계",
            "EU 국경 생체인식(SIS II·sBMS) 계약 — 정부 민감 ID 프로그램 공신력",
            "유럽 디지털 주권 포지셔닝 — ESTIA 클라우드 연합 공동창설",
        ],
        "weaknesses":[
            "선거기술 전용 제품 없음 — 프랑스 출구조사+국경 생체인식에 제한",
            "EDPS 감사(2025): SIS II 수천개 고심각도 취약점, 최대 5.5년 미패치 — 보안 신뢰도 손상",
            "프랑스 43%·영국 16% 매출 집중 — 신흥시장 선거기술 수요 지역 부재",
        ],
        "news":"Q1 2026 매출 +3.4% 반등 / sBMS 2025.8 eu-LISA와 가동 / EDPS 감사 고심각도 취약점 논란(2025.7)",
        "confidence":"High",
    },
]

OVERLAP_META = {
    "Direct":   (B["red"],    "직접 경쟁"),
    "Indirect": ("#D4870A",  "간접 경쟁"),
    "None":     (B["steel"], "비경쟁"),
}

# ─── KPI 팝업: 국가별 주요 조달 포털 URL 추출 ─────────────────────────────────
def _primary_url(iso3, portals):
    for name, url, status, primary in portals.get(iso3, []):
        if primary and status in ("Working","Login","JS"):
            return name, url
    for name, url, status, primary in portals.get(iso3, []):
        if status in ("Working","Login","JS"):
            return name, url
    return "", ""

def _kpi_items(rows, portals, flags, panel_key=None):
    items = []
    for r in rows:
        iso3 = r[0]; name_ko = r[2]
        flag = flags.get(iso3,"🏳️")
        pname, purl = _primary_url(iso3, portals)
        panel = panel_key or r[3]
        items.append({"flag":flag,"name":f"{name_ko}","portal":pname,"url":purl,"panel":panel})
    return items

KPI_PORTAL_JSON = json.dumps({
    "miru": {
        "title":"Miru 납품국 · 입찰 포털 바로가기",
        "items": _kpi_items(
            [r for r in COUNTRIES if "Miru" in r[7]], PORTALS, FLAGS)
    },
    "mv": {
        "title":"기계투표 사용국 25 · 입찰 포털 바로가기",
        "items": _kpi_items(COUNTRIES, PORTALS, FLAGS)
    },
    "bio": {
        "title":"생체인식·결과전송국 15 · 입찰 포털 바로가기",
        "items": _kpi_items(COUNTRIES_BIO, PORTALS_BIO, FLAGS_BIO, panel_key="bio")
    },
    "all": {
        "title":"전체 조달 대상국 40",
        "items": [
            {"flag":"🌏","name":"Asia-Pacific 5개국","portal":"","url":"","panel":"apac"},
            {"flag":"🌍","name":"Europe 7개국","portal":"","url":"","panel":"europe"},
            {"flag":"🌎","name":"Americas·Africa 7개국","portal":"","url":"","panel":"americas"},
            {"flag":"🕌","name":"Middle East·Central Asia 6개국","portal":"","url":"","panel":"mena"},
            {"flag":"💚","name":"생체인식·결과전송 15개국","portal":"","url":"","panel":"bio"},
        ]
    },
    "portals": {
        "title":"전체 조달 포털 바로가기",
        "items": (
            _kpi_items(COUNTRIES, PORTALS, FLAGS) +
            _kpi_items(COUNTRIES_BIO, PORTALS_BIO, FLAGS_BIO, panel_key="bio")
        )
    },
})

# ─── Chart data ───────────────────────────────────────────────────────────────
# Scope-M: 투표·개표 기계화 국가 / 미국 제외 23개국 직접 집계 (COUNTRIES 리스트 기준)
nonusa_vendor_chart = {
    "labels": ["Miru Systems","Smartmatic","BEL+ECIL","MSA 그룹","State/Public","기타·자체","Dominion","Positivo"],
    "data":   [5,              6,           2,          2,         2,             5,          1,         1],
    # Miru=5(KOR/PHL/IRQ/KGZ/COD) Smartmatic=6(BEL/BGR/BIH/GEO/ALB/VEN) BEL+ECIL=2(IND/BTN)
    # MSA=2(PRY/ARG) State=2(EST/CHE) 기타=5(OMN/ARE/IRN/UZB/ZAF) Dominion=1(MNG) Positivo=1(BRA)
    "colors": [B["primary"],B["slate"],B["accent"],B["navy80"],B["accent2"],"#BFC7D9",B["line"],B["steel"]],
}

# USA 주별 투표기기 공급사 (SOURCE: EAC EAVS 2022 + Verified Voting + Brennan Center 2022)
# statewide = 주 전체 사실상 단독 계약 / present = 1개 이상 카운티 배포 포함 (복수 공급사 중복)
US_VENDOR_DATA = [
    # (id,       name_short,    color,         statewide, present, share_pct)
    ("ESS",    "ES&S",         B["primary"],  20,        42,      50),
    ("DOM",    "Dominion",     B["red"],       2,        28,      30),
    ("HART",   "Hart",         B["green"],     2,        16,      15),
    ("CLEARB", "Clear Ballot", "#D4870A",      1,        11,       3),
]
us_vendor_chart = {
    "labels":    [d[1] for d in US_VENDOR_DATA],
    "statewide": [d[3] for d in US_VENDOR_DATA],
    "present":   [d[4] for d in US_VENDOR_DATA],
    "share_pct": [d[5] for d in US_VENDOR_DATA],
    "colors":    [d[2] for d in US_VENDOR_DATA],
}

# Machine type bars
type_chart = {
    "labels": ["OMR  광학스캐너","EVM  전자투표기","Internet  인터넷","DRE  직접기록","BMD  마킹장치","Mixed  혼합"],
    "data":   [8,5,4,3,4,1],
    "colors": [MTYPE_COLOR["OMR"],MTYPE_COLOR["EVM"],MTYPE_COLOR["Internet"],
               MTYPE_COLOR["DRE"],MTYPE_COLOR["BMD"],MTYPE_COLOR["Mixed"]],
}

# ─── World dot map (40개국 lat/lon → canvas 렌더링) ─────────────────────────────
_VC = {"Miru Systems":"#05195E","Smartmatic":"#525252","BEL+ECIL":"#123A9E",
       "MSA 그룹":"#0A2A6E","State/Public":"#8C8C8C","기타·자체":"#BFC7D9",
       "Dominion":"#AEB7D6","Positivo":"#C7CEDC","Bio/ERT":"#24A148"}
def _dot(iso,name,lat,lon,vendor,scope,product,flag):
    c = _VC.get(vendor, "#24A148" if scope!="M" else "#8C8C8C")
    return {"iso":iso,"name":name,"lat":lat,"lon":lon,"c":c,"scope":scope,"vendor":vendor,"product":product,"flag":flag}

WORLD_DOTS = json.dumps([
    _dot("KOR","대한민국",37.6,127.8,"Miru Systems","M","투표지분류기 OMR","🇰🇷"),
    _dot("PHL","필리핀",12.8,122.0,"Miru Systems","M","FASTrAC ACM OMR","🇵🇭"),
    _dot("IND","인도",20.6,78.9,"BEL+ECIL","M","M3 EVM+VVPAT","🇮🇳"),
    _dot("BTN","부탄",27.5,90.4,"BEL+ECIL","M","EVM","🇧🇹"),
    _dot("MNG","몽골",46.9,103.8,"Dominion","M","ImageCast OMR","🇲🇳"),
    _dot("BEL","벨기에",50.8,4.5,"Smartmatic","M","bSmart500 EVM","🇧🇪"),
    _dot("BGR","불가리아",42.7,25.5,"Smartmatic","M","A4-517 BMD","🇧🇬"),
    _dot("BIH","보스니아",44.2,17.9,"Smartmatic","M","SAES-1800 OMR","🇧🇦"),
    _dot("GEO","조지아",42.3,43.4,"Smartmatic","M","bScan OMR","🇬🇪"),
    _dot("ALB","알바니아",41.2,20.2,"Smartmatic","M","A4-517 Pilot","🇦🇱"),
    _dot("EST","에스토니아",58.6,25.0,"State/Public","M","i-Voting Internet","🇪🇪"),
    _dot("CHE","스위스",46.8,8.2,"State/Public","M","Swiss Post Internet","🇨🇭"),
    _dot("BRA","브라질",-10.8,-53.2,"Positivo","M","Urna Eletrônica DRE","🇧🇷"),
    _dot("USA","미국",38.8,-97.9,"기타·자체","M","ES&S·Dominion·Hart Mixed (EAC)","🇺🇸"),
    _dot("PRY","파라과이",-23.4,-58.4,"MSA 그룹","M","BUE BMD","🇵🇾"),
    _dot("ARG","아르헨티나",-34.6,-64.2,"MSA 그룹","M","BUE BMD Pilot","🇦🇷"),
    _dot("VEN","베네수엘라",8.0,-66.6,"Smartmatic","M","SAES3000 DRE","🇻🇪"),
    _dot("COD","콩고DRC",-4.0,24.5,"Miru Systems","M","DEV BMD","🇨🇩"),
    _dot("IRQ","이라크",33.2,43.7,"Miru Systems","M","PCOS/CCOS OMR","🇮🇶"),
    _dot("OMN","오만",21.5,57.0,"기타·자체","M","Intakhib Internet","🇴🇲"),
    _dot("ARE","UAE",24.4,54.4,"기타·자체","M","Scytl Kiosk Internet","🇦🇪"),
    _dot("IRN","이란",32.4,53.7,"기타·자체","M","Domestic EVM Pilot","🇮🇷"),
    _dot("KGZ","키르기스스탄",41.2,74.8,"Miru Systems","M","PCOS 5-in-1 OMR","🇰🇬"),
    _dot("UZB","우즈베키스탄",41.4,64.6,"기타·자체","M","E-Saylov EVM Pilot","🇺🇿"),
    _dot("KEN","케냐",-1.3,36.9,"Bio/ERT","B+R","KIEMS 생체인식+ERT","🇰🇪"),
    _dot("NGA","나이지리아",9.1,8.7,"Bio/ERT","B+R","BVAS+IREV 생체+ERT","🇳🇬"),
    _dot("ZAF","남아공",-28.7,24.7,"기타·자체","M","Champtek VMD X-100 OMR (DRE검토중)","🇿🇦"),
    _dot("GHA","가나",7.9,-1.0,"Bio/ERT","B+R","BVD+MARS 생체+ERT","🇬🇭"),
    _dot("TZA","탄자니아",-6.4,34.9,"Bio/ERT","B","BVR Kit 생체인식","🇹🇿"),
    _dot("UGA","우간다",1.4,32.3,"Bio/ERT","B","Biometric VR","🇺🇬"),
    _dot("ZMB","잠비아",-13.1,27.9,"Bio/ERT","B+R","BVR+ERT","🇿🇲"),
    _dot("ZWE","짐바브웨",-19.0,29.2,"Bio/ERT","B","BVR Kit 생체인식","🇿🇼"),
    _dot("SEN","세네갈",14.5,-14.4,"Bio/ERT","B","생체 선거인명부","🇸🇳"),
    _dot("CMR","카메룬",3.9,11.5,"Bio/ERT","B+R","ELECAM 생체+ERT","🇨🇲"),
    _dot("SLE","시에라리온",8.5,-11.8,"Bio/ERT","B+R","BVR+ERT","🇸🇱"),
    _dot("DOM","도미니카공화국",18.7,-70.2,"Bio/ERT","B+R","Padrón+TREP","🇩🇴"),
    _dot("JAM","자메이카",18.1,-77.3,"Bio/ERT","B","EOJ 생체인식","🇯🇲"),
    _dot("BGD","방글라데시",23.7,90.4,"Bio/ERT","B","NID 선거인 확인","🇧🇩"),
    _dot("PAK","파키스탄",30.4,69.3,"Bio/ERT","B","CNIC BVM","🇵🇰"),
    _dot("MOZ","모잠비크",-18.7,35.5,"Bio/ERT","B","CNE 생체 카드","🇲🇿"),
])

# ─── US tile map (EAC EAVS 2022 기준 · 12×8 그리드) ─────────────────────────────
# 벤더: ESS=ES&S, DOM=Dominion, HART=Hart, CLR=Clear Ballot, MIX=복수공급
_UT = {
    "AK":[0,0,"DOM"],"ME":[11,1,"ESS"],
    "WA":[0,1,"MIX"],"MT":[1,1,"ESS"],"ND":[2,1,"ESS"],"MN":[3,1,"ESS"],
    "WI":[4,1,"MIX"],"MI":[5,1,"MIX"],"NY":[8,1,"MIX"],"VT":[9,1,"MIX"],"NH":[10,1,"MIX"],
    "OR":[0,2,"MIX"],"ID":[1,2,"ESS"],"WY":[2,2,"ESS"],"SD":[3,2,"ESS"],
    "IA":[4,2,"ESS"],"IL":[5,2,"MIX"],"IN":[6,2,"ESS"],"OH":[7,2,"MIX"],
    "PA":[8,2,"MIX"],"NJ":[9,2,"ESS"],"MA":[10,2,"ESS"],"RI":[11,2,"ESS"],
    "CA":[0,3,"MIX"],"NV":[1,3,"MIX"],"CO":[2,3,"MIX"],"NE":[3,3,"ESS"],
    "MO":[4,3,"ESS"],"KY":[5,3,"MIX"],"WV":[6,3,"ESS"],"VA":[7,3,"ESS"],
    "MD":[8,3,"ESS"],"DC":[9,3,"ESS"],"CT":[10,3,"ESS"],"DE":[11,3,"ESS"],
    "AZ":[1,4,"MIX"],"UT":[2,4,"DOM"],"KS":[3,4,"CLR"],"AR":[4,4,"ESS"],
    "TN":[5,4,"ESS"],"NC":[6,4,"ESS"],"SC":[7,4,"ESS"],
    "NM":[2,5,"ESS"],"OK":[3,5,"HART"],"MS":[4,5,"ESS"],"AL":[5,5,"ESS"],"GA":[6,5,"DOM"],
    "TX":[3,6,"HART"],"LA":[4,6,"ESS"],"FL":[5,6,"ESS"],
    "HI":[0,7,"HART"],
}
_UT_VENDOR = {
    "ESS": {"label":"ES&S","color":"#05195E","note":"단독 Statewide 계약"},
    "DOM": {"label":"Dominion","color":"#EB0414","note":"단독 Statewide 계약"},
    "HART":{"label":"Hart","color":"#24A148","note":"단독 Statewide 계약"},
    "CLR": {"label":"Clear Ballot","color":"#D4870A","note":"주요 공급"},
    "MIX": {"label":"복수공급","color":"#8C8C8C","note":"복수 벤더 공존 (카운티별 상이)"},
}
_UT_NOTES = {
    "AK":"Dominion 전주 단독","GA":"Dominion $107M 전주 단독 BMD+ICC","HI":"Hart Verity 전주 단독",
    "OK":"Hart Verity 전주 단독","KS":"Clear Ballot 다수 카운티",
    "IN":"ES&S iVotronic DRE (무용지)","TN":"ES&S iVotronic DRE (무용지)",
    "NJ":"ES&S AVC Advantage DRE (무용지)","LA":"ES&S iVotronic DRE → 교체중",
    "MS":"ES&S iVotronic DRE (무용지)",
    "TX":"Hart 전통적 주도 (카운티별 선택)","FL":"ES&S 주도 (Miami-Dade=Dominion)",
}
US_TILES_JSON  = json.dumps(_UT)
US_TILE_VDR    = json.dumps(_UT_VENDOR)
US_TILE_NOTES  = json.dumps(_UT_NOTES)

# ─── HTML helpers ─────────────────────────────────────────────────────────────
def portal_html(iso3):
    lines = []
    for name, url, status, primary in PORTALS.get(iso3, []):
        col, dot, lbl = STATUS_META.get(status,(B["steel"],"○","?"))
        pri = " pl-primary" if primary else ""
        if status in ("Working","Login","JS"):
            o,c = f'<a href="{url}" target="_blank" class="portal-link{pri}">','</a>'
        else:
            o,c = f'<span class="portal-link pl-dead{pri}">','</span>'
        lines.append(f'{o}<span class="p-dot" style="color:{col}">{dot}</span>'
                     f'<span class="p-name">{name}</span>'
                     f'<span class="p-st">{lbl}</span>{c}')
    return "\n".join(lines)

def contract_badge(iso3):
    cd = CONTRACT_DATA.get(iso3)
    if not cd: return ""
    tier = cd["tier"]
    col, lbl, icon = TIER_META.get(tier, (B["steel"], "?", ""))
    nt = cd["next_tender"]
    return f'<div class="contract-badge" style="border-top:1px solid {col}22;margin-top:6px;padding-top:6px"><span style="font-size:9px;color:{col};font-weight:600;letter-spacing:.05em">{icon} 다음입찰 {nt}</span><span style="font-size:9px;color:{col};opacity:.8;margin-left:6px">{lbl}</span></div>'

def country_card(row):
    iso3,name,name_ko,panel,mv,mtype,model,vendor,year,scale,conf = row
    mc = MTYPE_COLOR.get(mtype, B["slate"])
    miru_cls = "miru-vendor" if "Miru" in vendor else ""
    pilot_badge = '<span class="pilot-badge">PILOT</span>' if mv=="Pilot" else ""
    year_str = year or "—"
    scale_ko = {"National":"전국","Partial":"부분","Pilot":"시범"}.get(scale,scale)
    cd = CONTRACT_DATA.get(iso3, {})
    tier = cd.get("tier","")
    tier_col = TIER_META.get(tier, (B["slate"],"",""))[0]
    tier_lbl = TIER_META.get(tier, (B["slate"],"",""))[1]
    tier_icon = TIER_META.get(tier, (B["slate"],"",""))[2]
    next_t = cd.get("next_tender","—")
    c_end  = cd.get("contract_end","—")
    c_note = cd.get("notes","")
    tier_badge = (f'<span class="tier-badge" style="background:{tier_col}18;color:{tier_col};border:1px solid {tier_col}44">'
                  f'{tier_icon} {tier_lbl}</span>') if tier else ""
    return f"""
<div class="ccard">
  <div class="ccard-head" style="border-left:3px solid {mc}">
    <div class="cc-flag">{FLAGS.get(iso3,'🏳️')}</div>
    <div class="cc-info">
      <div class="cc-name">{name_ko} <span class="cc-en">{name}</span> {pilot_badge}</div>
      <div class="cc-iso">{iso3}</div>
    </div>
    <span class="mtype-badge" style="background:{mc}">{mtype}</span>
  </div>
  <div class="ccard-body">
    <div class="cc-row"><span class="cc-lbl">공급사</span><span class="cc-val {miru_cls}">{vendor}</span></div>
    <div class="cc-row"><span class="cc-lbl">기기</span><span class="cc-val cc-model">{model}</span></div>
    <div class="cc-row"><span class="cc-lbl">계약연도</span><span class="cc-val">{year_str}</span></div>
    <div class="cc-row"><span class="cc-lbl">규모</span><span class="cc-val">{scale_ko}</span></div>
    <div class="cc-row" style="margin-top:4px;align-items:flex-start">
      <span class="cc-lbl" style="color:{tier_col}">다음입찰</span>
      <span class="cc-val" style="color:{tier_col};font-weight:600">{next_t} {tier_badge}</span>
    </div>
    <div class="cc-row" style="margin-top:1px">
      <span class="cc-lbl" style="font-size:9px;color:{B['steel']}">계약상태</span>
      <span class="cc-val" style="font-size:9px;color:{B['steel']}">{c_end}</span>
    </div>
  </div>
  <div style="padding:0 12px 6px;font-size:9px;color:{B['steel']};line-height:1.4;opacity:.85">{c_note}</div>
  <div class="ccard-portals">
    <div class="p-label">조달 포털</div>
    {portal_html(iso3)}
  </div>
</div>"""

def region_panel(pid):
    rows = [c for c in COUNTRIES if c[3]==pid]
    en, ko, cnt = PANEL_META[pid]
    yes   = sum(1 for r in rows if r[4]=="Yes")
    pilot = sum(1 for r in rows if r[4]=="Pilot")
    miru  = sum(1 for r in rows if "Miru" in r[7])
    types = {}
    for r in rows: types[r[5]] = types.get(r[5],0)+1
    type_pills = " ".join(
        f'<span class="tpill" style="background:{MTYPE_COLOR.get(t,B["slate"])}">{t} {n}</span>'
        for t,n in sorted(types.items(),key=lambda x:-x[1])
    )
    miru_note = (f'<span class="miru-note">✦ Miru Systems {miru}개국 납품</span>' if miru>0 else "")
    cards = "\n".join(country_card(r) for r in rows)
    return f"""
<div id="panel-{pid}" class="panel">
  <div class="ph">
    <div class="ph-inner">
      <div class="ph-left">
        <div class="ph-eye">Region Intelligence</div>
        <h2 class="ph-title">{ko}</h2>
        <p class="ph-sub">{en}</p>
      </div>
      <div class="ph-stats">
        <div class="ph-stat"><span class="ph-n">{cnt}</span><span class="ph-l">대상국</span></div>
        <div class="ph-stat"><span class="ph-n">{yes}</span><span class="ph-l">실도입</span></div>
        <div class="ph-stat"><span class="ph-n">{pilot}</span><span class="ph-l">파일럿</span></div>
        <div class="ph-stat" style="border-left:2px solid {B['red']};padding-left:16px">
          <span class="ph-n" style="color:#4d9fff">{miru}</span><span class="ph-l">Miru납품</span>
        </div>
      </div>
    </div>
    <div class="ph-pills">{type_pills} {miru_note}</div>
  </div>
  <div class="cards-grid">{cards}</div>
</div>"""


def opportunity_panel():
    tiers = [
        ("CRITICAL","즉시 대응 — 계약 만료 또는 입찰 진행중 (≤2026)"),
        ("WATCH",   "제안 준비 — 1~2년 내 입찰 예상 (2027)"),
        ("MONITOR", "모니터링 — 2~4년 내 입찰 예상 (2028–2029)"),
        ("LONG",    "장기 관찰 — 5년+ 또는 구조적 폐쇄 시장"),
        ("UNKNOWN", "정보 부족 — 파일럿·불투명 시장"),
    ]
    # country lookup
    cmap = {r[0]:r for r in COUNTRIES}
    def rows_for_tier(t):
        items = [(iso3, cd) for iso3,cd in CONTRACT_DATA.items() if cd["tier"]==t]
        rows_html = []
        for iso3, cd in items:
            cr = cmap.get(iso3)
            if not cr: continue
            name_ko = cr[2]; name = cr[1]; vendor = cr[7]; mtype = cr[5]
            mc = MTYPE_COLOR.get(mtype, B["slate"])
            flag = FLAGS.get(iso3,"🏳️")
            miru_cls = "font-weight:600;color:#4d9fff" if "Miru" in vendor else ""
            pname, purl = _primary_url(iso3, PORTALS)
            portal_link = (f'<a href="{purl}" target="_blank" style="color:{B["green"]};font-size:10px">{pname}</a>'
                           if purl else f'<span style="color:{B["steel"]};font-size:10px">—</span>')
            rows_html.append(f"""
<tr class="opp-row">
  <td style="padding:8px 12px;white-space:nowrap">{flag} <strong>{name_ko}</strong> <span style="color:{B['steel']};font-size:10px">{iso3}</span></td>
  <td style="padding:8px 12px"><span class="mtype-badge" style="background:{mc};font-size:9px">{mtype}</span></td>
  <td style="padding:8px 12px;{miru_cls}">{vendor}</td>
  <td style="padding:8px 12px;font-weight:600">{cd['next_tender']}</td>
  <td style="padding:8px 12px;color:{B['steel']};font-size:10px">{cd['contract_end']}</td>
  <td style="padding:8px 12px">{portal_link}</td>
  <td style="padding:8px 12px;font-size:10px;color:{B['slate']};max-width:260px;line-height:1.4">{cd['notes']}</td>
</tr>""")
        return "".join(rows_html)

    tier_sections = []
    for tier_key, tier_desc in tiers:
        col, lbl, icon = TIER_META[tier_key]
        body = rows_for_tier(tier_key)
        if not body: continue
        tier_sections.append(f"""
<div class="opp-tier" style="margin-bottom:24px">
  <div style="display:flex;align-items:center;gap:10px;padding:10px 16px;background:{col}12;border-left:3px solid {col};margin-bottom:0">
    <span style="font-size:14px">{icon}</span>
    <div>
      <div style="font-size:12px;font-weight:700;color:{col};letter-spacing:.06em">{tier_key} — {lbl}</div>
      <div style="font-size:10px;color:{B['steel']};margin-top:1px">{tier_desc}</div>
    </div>
  </div>
  <div style="overflow-x:auto">
  <table style="width:100%;border-collapse:collapse;font-size:11px">
    <thead>
      <tr style="background:{B['fog2']};color:{B['slate']}">
        <th style="padding:6px 12px;text-align:left;font-weight:600">국가</th>
        <th style="padding:6px 12px;text-align:left;font-weight:600">유형</th>
        <th style="padding:6px 12px;text-align:left;font-weight:600">현재 공급사</th>
        <th style="padding:6px 12px;text-align:left;font-weight:600">다음입찰 예상</th>
        <th style="padding:6px 12px;text-align:left;font-weight:600">계약상태</th>
        <th style="padding:6px 12px;text-align:left;font-weight:600">포털</th>
        <th style="padding:6px 12px;text-align:left;font-weight:600">메모</th>
      </tr>
    </thead>
    <tbody>{body}</tbody>
  </table>
  </div>
</div>""")

    critical_cnt = sum(1 for cd in CONTRACT_DATA.values() if cd["tier"]=="CRITICAL")
    watch_cnt    = sum(1 for cd in CONTRACT_DATA.values() if cd["tier"]=="WATCH")
    return f"""
<div id="panel-opportunity" class="panel">
  <div class="ph">
    <div class="ph-inner">
      <div class="ph-left">
        <div class="ph-eye">Business Development Intelligence</div>
        <h2 class="ph-title">계약 만료 · 입찰 기회 파이프라인</h2>
        <p class="ph-sub">25개 기계투표 국가 계약 리서치 기준 — 다음 입찰 예상 시점 긴급도별 분류 · 2026-06-25</p>
      </div>
      <div class="ph-stats">
        <div class="ph-stat"><span class="ph-n" style="color:{B['red']}">{critical_cnt}</span><span class="ph-l">즉시 대응</span></div>
        <div class="ph-stat"><span class="ph-n" style="color:#D4870A">{watch_cnt}</span><span class="ph-l">제안 준비</span></div>
        <div class="ph-stat"><span class="ph-n" style="color:#4d9fff">7</span><span class="ph-l">모니터링</span></div>
        <div class="ph-stat"><span class="ph-n" style="color:{B['steel']}">6</span><span class="ph-l">장기 관찰</span></div>
      </div>
    </div>
    <div class="ph-pills">
      <span style="font-size:10px;color:{B['steel']}">※ 리서치 신뢰도: High(공식발표) / Med(언론보도) / Low(추정) — 입찰 전 반드시 포털 재확인</span>
    </div>
  </div>
  <div style="padding:24px clamp(12px,3vw,40px)">
    {"".join(tier_sections)}
  </div>
</div>"""

def bio_portal_html(iso3):
    lines = []
    for name, url, status, primary in PORTALS_BIO.get(iso3, []):
        col, dot, lbl = STATUS_META.get(status,(B["steel"],"○","?"))
        pri = " pl-primary" if primary else ""
        if status in ("Working","Login","JS"):
            o,c = f'<a href="{url}" target="_blank" class="portal-link{pri}">','</a>'
        else:
            o,c = f'<span class="portal-link pl-dead{pri}">','</span>'
        lines.append(f'{o}<span class="p-dot" style="color:{col}">{dot}</span>'
                     f'<span class="p-name">{name}</span>'
                     f'<span class="p-st">{lbl}</span>{c}')
    return "\n".join(lines)

def bio_card(row):
    iso3,name,name_ko,btype,vendor,system,year,scale,conf = row
    bc = BTYPE_COLOR.get(btype, B["slate"])
    blbl = BTYPE_LABEL.get(btype, btype)
    flag = FLAGS_BIO.get(iso3, FLAGS.get(iso3, "🏳️"))
    scale_ko = {"National":"전국","Partial":"부분","Pilot":"시범"}.get(scale,scale)
    note = {"bio":"투표 집계는 수개표 — 본인확인 기기만 전자화",
            "ert":"수개표 후 결과만 전자 전송",
            "bio+ert":"본인확인 + 결과전송 모두 전자화, 투표·개표는 수개표"}
    return f"""
<div class="ccard">
  <div class="ccard-head" style="border-left:3px solid {bc}">
    <div class="cc-flag">{flag}</div>
    <div class="cc-info">
      <div class="cc-name">{name_ko} <span class="cc-en">{name}</span></div>
      <div class="cc-iso">{iso3}</div>
    </div>
    <span class="mtype-badge" style="background:{bc}">{blbl}</span>
  </div>
  <div class="ccard-body">
    <div class="cc-row"><span class="cc-lbl">공급사</span><span class="cc-val">{vendor}</span></div>
    <div class="cc-row"><span class="cc-lbl">시스템</span><span class="cc-val cc-model">{system}</span></div>
    <div class="cc-row"><span class="cc-lbl">도입연도</span><span class="cc-val">{year}</span></div>
    <div class="cc-row"><span class="cc-lbl">규모</span><span class="cc-val">{scale_ko}</span></div>
  </div>
  <div class="bio-note">{note.get(btype,"")}</div>
  <div class="ccard-portals">
    <div class="p-label">조달 포털</div>
    {bio_portal_html(iso3)}
  </div>
</div>"""

def bio_panel():
    total    = len(COUNTRIES_BIO)
    bio_cnt  = sum(1 for r in COUNTRIES_BIO if r[3]=="bio")
    both_cnt = sum(1 for r in COUNTRIES_BIO if r[3]=="bio+ert")
    cards = "\n".join(bio_card(r) for r in COUNTRIES_BIO)
    return f"""
<div id="panel-bio" class="panel">
  <div class="ph">
    <div class="ph-inner">
      <div class="ph-left">
        <div class="ph-eye">Market Expansion Intelligence</div>
        <h2 class="ph-title">생체인식 · 결과전송 시장</h2>
        <p class="ph-sub">Biometric e-Pollbook &amp; Electronic Results Transmission — 기계투표 미도입 · Miru 제품 적용 가능 조달 기회국</p>
      </div>
      <div class="ph-stats">
        <div class="ph-stat"><span class="ph-n">{total}</span><span class="ph-l">대상국</span></div>
        <div class="ph-stat"><span class="ph-n" style="color:{B['green']}">{bio_cnt}</span><span class="ph-l">생체인식 전용</span></div>
        <div class="ph-stat"><span class="ph-n" style="color:#7eb8ff">{both_cnt}</span><span class="ph-l">생체+결과전송</span></div>
      </div>
    </div>
    <div class="ph-pills">
      <span class="tpill" style="background:{BTYPE_COLOR['bio']}">생체인식 e-Pollbook</span>
      <span class="tpill" style="background:{BTYPE_COLOR['bio+ert']}">생체인식 + 결과전송</span>
      <span class="miru-note">✦ Miru 지문인식 · 결과전송 제품군 적용 가능 시장</span>
    </div>
  </div>
  <div class="cards-grid">{cards}</div>
</div>"""


def vendor_panel():
    total = len(VENDOR_DATA)
    direct_cnt   = sum(1 for v in VENDOR_DATA if v["overlap"]=="Direct")
    indirect_cnt = sum(1 for v in VENDOR_DATA if v["overlap"]=="Indirect")

    def vcard(v):
        oc, ol = OVERLAP_META.get(v["overlap"], (B["steel"],"비경쟁"))
        is_miru = v["slug"] == "miru_self"
        border_col = B["primary"] if is_miru else oc
        miru_flag  = " vcard-miru" if is_miru else ""
        markets_str = " · ".join(v.get("overlap_markets",[]))
        markets_html = (f'<div class="vc-markets">경쟁 시장: <strong>{markets_str}</strong></div>'
                        if markets_str else "")
        prods_html = "".join(f'<span class="vc-tag">{p}</span>'
                             for p in v["key_products"][:4])
        cats_html  = "".join(f'<span class="vc-cat">{c}</span>'
                             for c in v.get("categories",[])[:5])
        sw_html = ""
        for label, items in [("강점", v.get("strengths",[])), ("약점", v.get("weaknesses",[]))]:
            c2 = B["green"] if label=="강점" else B["red"]
            rows = "".join(f'<li style="color:{B["slate"]};margin-bottom:3px">{it}</li>' for it in items)
            sw_html += f'<div style="margin-top:6px"><span style="font-size:9px;font-weight:700;color:{c2};letter-spacing:.08em">{label}</span><ul style="margin:4px 0 0 14px;padding:0;font-size:10px;line-height:1.5">{rows}</ul></div>'
        conf_col = {"High":B["green"],"Med":"#D4870A","Low":B["red"]}.get(v.get("confidence",""),B["steel"])
        return f"""
<div class="vcard{miru_flag}">
  <div class="vcard-head" style="border-left:4px solid {border_col}">
    <div class="vc-flag">{v.get("flag","🏳️")}</div>
    <div class="vc-info">
      <div class="vc-name">{v["name"]}</div>
      <div class="vc-hq">{v["hq"]}</div>
    </div>
    <span class="vc-overlap" style="background:{oc}18;color:{oc};border:1px solid {oc}44">{ol}</span>
  </div>
  <div class="vcard-body">
    <div class="vc-row"><span class="vc-lbl">유형</span><span class="vc-val">{v["type"]}</span></div>
    <div class="vc-row"><span class="vc-lbl">설립</span><span class="vc-val">{v.get("founded","—")}</span></div>
    <div class="vc-row"><span class="vc-lbl">임직원</span><span class="vc-val">{v.get("employees","—")}</span></div>
    <div class="vc-row"><span class="vc-lbl">매출</span><span class="vc-val">{v.get("annual_revenue_usd","—")}</span></div>
    <div class="vc-row"><span class="vc-lbl">진출국</span><span class="vc-val">{v["countries_count"]}개국</span></div>
    <div style="margin-top:6px">{cats_html}</div>
    <div style="margin-top:5px">{prods_html}</div>
    {markets_html}
    {sw_html}
    <div class="vc-news">{v.get("news","")}</div>
  </div>
  <div class="vcard-footer">
    <a href="{v["homepage"]}" target="_blank" class="vc-link">홈페이지 ↗</a>
    {f'<a href="{v["products_url"]}" target="_blank" class="vc-link">선거제품 ↗</a>' if v.get("products_url") and v["products_url"] != v["homepage"] else ""}
    <span style="font-size:9px;color:{conf_col};margin-left:auto">신뢰도: {v.get("confidence","")}</span>
  </div>
</div>"""

    cards_direct   = "\n".join(vcard(v) for v in VENDOR_DATA if v["overlap"]=="Direct")
    cards_indirect = "\n".join(vcard(v) for v in VENDOR_DATA if v["overlap"]=="Indirect")
    cards_none     = "\n".join(vcard(v) for v in VENDOR_DATA if v["overlap"]=="None")

    def section(title, col, body, cnt):
        if not body: return ""
        return f"""
<div class="vendor-section">
  <div class="vs-header" style="border-left:3px solid {col};background:{col}0f">
    <span style="font-size:12px;font-weight:700;color:{col}">{title}</span>
    <span style="font-size:10px;color:{B['steel']};margin-left:8px">{cnt}개 사</span>
  </div>
  <div class="vcards-grid">{body}</div>
</div>"""

    return f"""
<div id="panel-vendor" class="panel">
  <div class="ph">
    <div class="ph-inner">
      <div class="ph-left">
        <div class="ph-eye">Competitive Intelligence</div>
        <h2 class="ph-title">공급사 인텔리전스</h2>
        <p class="ph-sub">전 세계 선거기술 벤더 {total}개사 심층 분석 — 홈페이지·제품·재무·Miru 경쟁관계 · 2026-06-25</p>
      </div>
      <div class="ph-stats">
        <div class="ph-stat"><span class="ph-n">{total}</span><span class="ph-l">분석 벤더</span></div>
        <div class="ph-stat"><span class="ph-n" style="color:{B['red']}">{direct_cnt}</span><span class="ph-l">직접 경쟁</span></div>
        <div class="ph-stat"><span class="ph-n" style="color:#D4870A">{indirect_cnt}</span><span class="ph-l">간접 경쟁</span></div>
        <div class="ph-stat"><span class="ph-n" style="color:{B['steel']}">{total-direct_cnt-indirect_cnt}</span><span class="ph-l">비경쟁</span></div>
      </div>
    </div>
    <div class="ph-pills">
      <span class="tpill" style="background:{B['red']}">직접 경쟁 — 동일 시장 입찰 경쟁</span>
      <span class="tpill" style="background:#D4870A">간접 경쟁 — 인접 시장 겹침</span>
      <span class="tpill" style="background:{B['steel']}">비경쟁 — 국가 독점 또는 다른 시장</span>
    </div>
  </div>
  <div style="padding:24px clamp(12px,3vw,40px)">
    {section("🔴 직접 경쟁사", B["red"], cards_direct, direct_cnt)}
    {section("🟠 간접 경쟁사 (시장 겹침)", "#D4870A", cards_indirect, indirect_cnt)}
    {section("⚫ 비경쟁 (국가 독점 또는 다른 세그먼트)", B["steel"], cards_none, total-direct_cnt-indirect_cnt)}
  </div>
</div>"""


def about_panel():
    crawler_rows = [
        ("카자흐스탄","KAZ","goszakup.gov.kz","⚠️","API 토큰 필요","GOSZAKUP_TOKEN 환경변수 설정 후 사용 가능"),
        ("브라질","BRA","pncp.gov.br","⚠️","ConnectionReset","TLS/WAF 이슈 — 엔드포인트 재확인 필요"),
        ("가나","GHA","ghaneps.gov.gh","⚠️","로그인 필요","/epps/notices/viewPublishedNotices.do 공개 경로 시도 중"),
        ("바레인","BHR","etendering.tenderboard.gov.bh","🔧","수정 중","루트 URL 수정 필요"),
        ("부탄·알바니아","BTN/ALB","ecb.bt / kqz.gov.al","⚠️","타임아웃 / Next.js 전환","KQZ — Next.js 재구축 후 경로 탐색 필요"),
        ("자메이카","JAM","gojep.gov.jm","⚠️","JS 렌더링 필요","Playwright 전환 예정"),
        ("키르기스스탄","KGZ","zakupki.gov.kg","🔧","미테스트","OCDS API 접근 확인 필요 — Miru 납품국"),
    ]
    crawler_html = "\n".join(f"""
      <tr>
        <td style="font-weight:500">{r[0]}</td>
        <td style="font-family:monospace;font-size:11px;color:{B['steel']}">{r[2]}</td>
        <td style="font-size:16px;text-align:center">{r[3]}</td>
        <td style="color:{B['red'] if r[3]=='⚠️' else '#D4870A'};font-size:12px">{r[4]}</td>
        <td style="color:{B['slate']};font-size:12px">{r[5]}</td>
      </tr>""" for r in crawler_rows)

    data_sources = [
        ("EAC EAVS 2022","미국 주별 투표기기 공급사 · 42개주 ES&S·Dominion·Hart·Clear Ballot 데이터","https://www.eac.gov/research-and-data/election-administration-voting-survey"),
        ("Verified Voting","미국 전역 투표 시스템 사용 현황 공개 DB","https://verifiedvoting.org/"),
        ("ACE Electoral Knowledge Network","각국 선거 시스템 학술 레퍼런스","https://aceproject.org/"),
        ("각국 선관위 공식 자료","Smartmatic·BEL/ECIL·Dominion·Miru 계약 발표 보도자료 및 공식 웹사이트",""),
        ("공개 조달 포털 (40개국)","SAM.gov·PhilGEPS·G2B·PNCP·DNCP 등 65개 포털 직접 검증",""),
    ]
    sources_html = "\n".join(f"""
      <div class="ab-src">
        <div class="ab-src-dot"></div>
        <div>
          <strong>{s[0]}</strong>{"<br>" if s[1] else ""}
          <span style="color:{B['slate']};font-size:12px">{s[1]}</span>
          {f'<a href="{s[2]}" target="_blank" style="color:{B["accent"]};font-size:11px;margin-left:6px">↗</a>' if s[2] else ""}
        </div>
      </div>""" for s in data_sources)

    tech_stack = [
        ("Python 3","generate_intel_report.py — HTML 자동 생성 · SQLite 레퍼런스 DB"),
        ("SQLite","election_technology_world.db — 206개국 레퍼런스 · election_intel_tenders.db — 크롤 결과"),
        ("Chart.js 4.4","공급사 점유율 도넛 차트 · 미국 주별 수평 바 차트 (인라인 내장)"),
        ("TopoJSON client 3","세계 지도 choropleth 렌더링 — Natural Earth 110m world-atlas 기반"),
        ("Claude Code","AI 페어 프로그래밍 — 데이터 검증 · 파서 개발 · HTML 생성 보조"),
    ]
    tech_html = "\n".join(f"""
      <div class="ab-tech">
        <div class="ab-tech-label">{t[0]}</div>
        <div class="ab-tech-desc">{t[1]}</div>
      </div>""" for t in tech_stack)

    return f"""
<div id="panel-about" class="panel">
  <div class="ph">
    <div class="ph-inner">
      <div class="ph-left">
        <div class="ph-eye">Methodology &amp; Data Sources</div>
        <h2 class="ph-title">리포트 제작 방법론</h2>
        <p class="ph-sub">Election Technology Intelligence — 데이터 출처 · 기술 스택 · 크롤러 개발 현황</p>
      </div>
      <div class="ph-stats">
        <div class="ph-stat"><span class="ph-n">40</span><span class="ph-l">조달 대상국</span></div>
        <div class="ph-stat"><span class="ph-n">65</span><span class="ph-l">검증 포털</span></div>
        <div class="ph-stat"><span class="ph-n" style="color:{B['green']}">206</span><span class="ph-l">레퍼런스 DB</span></div>
      </div>
    </div>
  </div>

  <div style="max-width:1080px;margin:0 auto;padding:32px clamp(16px,4vw,48px);display:grid;grid-template-columns:1fr 1fr;gap:28px;">

    <!-- 데이터 소스 -->
    <div class="ab-card" style="grid-column:1/-1">
      <h3 class="ab-h3">📊 데이터 소스</h3>
      <div style="display:flex;flex-direction:column;gap:12px">
        {sources_html}
      </div>
    </div>

    <!-- 기술 스택 -->
    <div class="ab-card">
      <h3 class="ab-h3">🔧 기술 스택</h3>
      <div style="display:flex;flex-direction:column;gap:10px">
        {tech_html}
      </div>
    </div>

    <!-- 업데이트 정보 -->
    <div class="ab-card">
      <h3 class="ab-h3">📅 업데이트 정보</h3>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div><span class="ab-badge" style="background:{B['green']}20;color:{B['green']}">데이터 검증</span>
          <span style="font-size:13px;color:{B['charcoal']}">2026-06-23</span>
        </div>
        <div style="font-size:13px;color:{B['slate']};line-height:1.6">
          레퍼런스 DB는 수동 업데이트<br>
          크롤러 가동 시 조달 공고 자동 누적 (election_intel_tenders.db)<br>
          목표: 주 1회 자동 갱신
        </div>
        <div style="margin-top:4px">
          <div style="font-size:11px;color:{B['steel']};margin-bottom:6px">포털 상태 검증 기준</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px">
            <span class="ab-badge" style="background:{B['green']}20;color:{B['green']}">● Working</span>
            <span class="ab-badge" style="background:{B['accent']}20;color:{B['accent']}">● Login 필요</span>
            <span class="ab-badge" style="background:#D4870A20;color:#D4870A">● JS 렌더링</span>
            <span class="ab-badge" style="background:{B['red']}20;color:{B['red']}">● 접근 불가</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 크롤러 개발 현황 -->
    <div class="ab-card" style="grid-column:1/-1">
      <h3 class="ab-h3">🕷️ 크롤러 개발 현황</h3>
      <p style="font-size:12px;color:{B['slate']};margin:0 0 14px">
        목표: 8개 포털 실시간 크롤 → election_intel_tenders.db 자동 누적 |
        <code style="font-size:11px;background:{B['fog2']};padding:2px 6px;border-radius:3px">python crawler/crawl.py</code>
      </p>
      <table style="width:100%;border-collapse:collapse;font-size:13px">
        <thead>
          <tr style="border-bottom:1px solid {B['line']}">
            <th style="text-align:left;padding:6px 8px;color:{B['slate']};font-weight:500">국가</th>
            <th style="text-align:left;padding:6px 8px;color:{B['slate']};font-weight:500">포털</th>
            <th style="text-align:center;padding:6px 8px;color:{B['slate']};font-weight:500">상태</th>
            <th style="text-align:left;padding:6px 8px;color:{B['slate']};font-weight:500">이슈</th>
            <th style="text-align:left;padding:6px 8px;color:{B['slate']};font-weight:500">비고</th>
          </tr>
        </thead>
        <tbody>
          {crawler_html}
        </tbody>
      </table>
    </div>

  </div>
</div>"""


# ─── CSS ──────────────────────────────────────────────────────────────────────
CSS = f"""
:root{{
  --navy:{B['primary']}; --navy2:{B['navy80']}; --accent:{B['accent']};
  --accent2:{B['accent2']}; --red:{B['red']}; --green:{B['green']};
  --charcoal:{B['charcoal']}; --slate:{B['slate']}; --steel:{B['steel']};
  --fog:{B['fog']}; --fog2:{B['fog2']}; --line:{B['line']}; --white:{B['white']};
  --font:'Inter','Pretendard','Noto Sans KR',sans-serif;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:var(--font);background:var(--fog2);color:var(--charcoal);font-size:14px;line-height:1.5;}}

/* ── NAV ───────────────────────────────────── */
.top-nav{{
  position:sticky;top:0;z-index:200;
  background:var(--navy);
  display:flex;align-items:stretch;height:56px;
  border-bottom:2px solid var(--red);
  box-shadow:0 2px 16px rgba(5,25,94,.25);
}}
.nav-brand{{
  display:flex;align-items:center;gap:12px;
  padding:0 24px;border-right:1px solid rgba(255,255,255,.1);flex-shrink:0;
}}
.nav-logo{{height:28px;width:auto;object-fit:contain;}}
.nav-divider{{width:1px;height:24px;background:rgba(255,255,255,.2);}}
.nav-title{{
  font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
  color:rgba(255,255,255,.55);
}}
.nav-tabs{{display:flex;align-items:stretch;flex:1;overflow-x:auto;scrollbar-width:none;}}
.nav-tabs::-webkit-scrollbar{{display:none;}}
.nav-tab{{
  display:flex;align-items:center;padding:0 20px;
  font-size:11.5px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;
  color:rgba(255,255,255,.45);cursor:pointer;border:none;background:none;
  border-bottom:2px solid transparent;transition:all .2s;white-space:nowrap;
  border-top:2px solid transparent;
}}
.nav-tab:hover{{color:rgba(255,255,255,.8);}}
.nav-tab.active{{color:var(--white);border-bottom-color:var(--red);}}
.nav-kpis{{
  display:flex;align-items:center;gap:0;
  border-left:1px solid rgba(255,255,255,.1);flex-shrink:0;
}}
.nk{{padding:0 18px;text-align:center;border-right:1px solid rgba(255,255,255,.1);}}
.nk-n{{font-size:18px;font-weight:800;color:var(--white);line-height:1;}}
.nk-l{{font-size:9px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.38);}}
.nk-miru .nk-n{{color:#7eb8ff;}}

/* ── OVERVIEW HERO ──────────────────────────── */
.ov-hero{{
  background:linear-gradient(135deg,#020e35 0%,{B['navy80']} 40%,{B['primary']} 70%,#020e35 100%);
  padding:52px clamp(20px,5vw,80px) 0;position:relative;overflow:hidden;
}}
.ov-hero::before{{
  content:"";position:absolute;top:-60px;right:-60px;
  width:480px;height:480px;
  background:radial-gradient(circle,rgba(235,4,20,.12) 0%,transparent 65%);
  pointer-events:none;
}}
.ov-inner{{max-width:1380px;margin:0 auto;}}
.ov-eye{{
  font-size:9.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;
  color:var(--red);margin-bottom:14px;display:flex;align-items:center;gap:8px;
}}
.ov-eye::before{{content:"";width:20px;height:1.5px;background:var(--red);}}
.ov-h1{{
  font-size:clamp(28px,4.5vw,50px);font-weight:800;color:var(--white);
  letter-spacing:-.03em;line-height:1.15;margin-bottom:8px;
}}
.ov-h1 em{{font-style:normal;color:#7eb8ff;}}
.ov-sub{{font-size:14px;color:rgba(255,255,255,.48);margin-bottom:36px;}}
.ov-kpis{{display:flex;gap:2px;flex-wrap:wrap;margin-bottom:0;}}
.kpi{{
  flex:1;min-width:130px;
  background:rgba(255,255,255,.055);
  border:1px solid rgba(255,255,255,.09);
  padding:20px 22px;transition:background .2s;
}}
.kpi:hover{{background:rgba(255,255,255,.1);}}
.kpi-n{{font-size:34px;font-weight:800;color:var(--white);line-height:1;letter-spacing:-.03em;}}
.kpi-l{{font-size:9.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.38);margin-top:6px;}}
.kpi-s{{font-size:11px;color:rgba(255,255,255,.28);margin-top:3px;}}
.kpi-miru .kpi-n{{color:#7eb8ff;}}

/* ticker INSIDE hero bottom strip */
.ticker-strip{{
  margin-top:28px;
  margin-left:calc(-1 * clamp(20px,5vw,80px));
  margin-right:calc(-1 * clamp(20px,5vw,80px));
  border-top:1px solid rgba(255,255,255,.08);
  background:rgba(0,0,0,.25);height:34px;
  display:flex;align-items:center;overflow:hidden;
}}
.ticker-lbl{{
  padding:0 16px;font-size:9px;font-weight:700;letter-spacing:.2em;
  text-transform:uppercase;color:var(--red);flex-shrink:0;
  border-right:1px solid rgba(255,255,255,.1);height:100%;display:flex;align-items:center;
}}
.ticker-wrap{{flex:1;overflow:hidden;position:relative;}}
.ticker-inner{{
  display:flex;white-space:nowrap;
  animation:tick 70s linear infinite;
}}
.ticker-item{{
  display:inline-flex;align-items:center;gap:5px;
  padding:0 20px;font-size:10.5px;color:rgba(255,255,255,.55);
  border-right:1px solid rgba(255,255,255,.07);
}}
.ticker-item strong{{color:rgba(255,255,255,.85);}}
@keyframes tick{{0%{{transform:translateX(0)}}100%{{transform:translateX(-50%)}}}}

/* ── CHART SECTION ──────────────────────────── */
.chart-sec{{max-width:1380px;margin:0 auto;padding:36px clamp(16px,4vw,80px);}}
.chart-row{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;}}
.chart-row.full{{grid-template-columns:1fr;}}
.cbox{{
  background:var(--white);border:1px solid var(--line);
  padding:28px;
}}
.cbox-eye{{
  font-size:9px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;
  color:var(--accent);margin-bottom:4px;
}}
.cbox-title{{font-size:17px;font-weight:700;color:var(--charcoal);margin-bottom:4px;letter-spacing:-.015em;}}
.cbox-desc{{font-size:12px;color:var(--slate);margin-bottom:20px;}}
.chart-wrap{{position:relative;height:260px;}}

/* vendor legend */
.v-legend{{display:flex;flex-wrap:wrap;gap:8px 16px;margin-top:16px;}}
.vl{{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--charcoal);}}
.vl-dot{{width:9px;height:9px;flex-shrink:0;}}

/* type bars */
.type-dist{{display:flex;flex-direction:column;gap:10px;}}
.td-row{{display:flex;align-items:center;gap:10px;}}
.td-lbl{{font-size:11px;font-weight:500;color:var(--charcoal);width:140px;flex-shrink:0;line-height:1.3;}}
.td-wrap{{flex:1;height:26px;background:var(--fog);position:relative;}}
.td-bar{{height:100%;display:flex;align-items:center;padding-left:9px;min-width:36px;}}
.td-n{{font-size:11px;font-weight:700;color:var(--white);}}
.td-pct{{font-size:10.5px;color:var(--slate);min-width:30px;}}

/* ── MIRU HIGHLIGHT ─────────────────────────── */
.miru-box{{
  background:var(--navy);color:var(--white);
  padding:32px;
}}
.mb-eye{{
  font-size:9px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;
  color:var(--red);margin-bottom:14px;display:flex;align-items:center;gap:8px;
}}
.mb-eye::before{{content:"";width:18px;height:1.5px;background:var(--red);}}
.mb-h2{{font-size:20px;font-weight:700;color:var(--white);margin-bottom:22px;letter-spacing:-.02em;}}
.miru-grid{{display:flex;gap:12px;flex-wrap:wrap;}}
.mc{{
  flex:1;min-width:155px;
  background:rgba(255,255,255,.055);
  border:1px solid rgba(255,255,255,.1);
  border-top:2px solid var(--red);
  padding:16px;
}}
.mc-flag{{font-size:24px;margin-bottom:8px;}}
.mc-name{{font-size:13px;font-weight:700;color:var(--white);}}
.mc-detail{{font-size:11px;color:rgba(255,255,255,.45);margin-top:4px;line-height:1.6;}}
.mc-mtype{{
  display:inline-block;margin-top:9px;
  padding:2px 8px;font-size:9px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;
  background:var(--red);color:var(--white);
}}

/* portal status summary box */
.status-box{{
  background:var(--white);border:1px solid var(--line);padding:28px;
}}
.st-grid{{display:flex;gap:2px;flex-wrap:wrap;margin-bottom:20px;}}
.st-item{{
  flex:1;min-width:100px;padding:16px;
  background:var(--fog2);border:1px solid var(--line);text-align:center;
}}
.st-n{{font-size:28px;font-weight:800;line-height:1;}}
.st-l{{font-size:9.5px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--slate);margin-top:5px;}}
.st-legend{{display:flex;flex-wrap:wrap;gap:8px 20px;}}
.sl{{display:flex;align-items:center;gap:6px;font-size:11.5px;color:var(--slate);}}
.sl-dot{{font-size:13px;}}

/* ── PANEL HEADER ───────────────────────────── */
.ph{{
  background:linear-gradient(135deg,{B['navy80']} 0%,{B['primary']} 100%);
  padding:36px clamp(16px,4vw,80px) 22px;
}}
.ph-inner{{
  max-width:1380px;margin:0 auto;
  display:flex;align-items:flex-end;justify-content:space-between;gap:20px;flex-wrap:wrap;
}}
.ph-eye{{
  font-size:9px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;
  color:rgba(255,255,255,.38);margin-bottom:6px;
}}
.ph-title{{font-size:26px;font-weight:800;color:var(--white);letter-spacing:-.02em;}}
.ph-sub{{font-size:12px;color:rgba(255,255,255,.38);margin-top:3px;}}
.ph-stats{{display:flex;gap:20px;flex-shrink:0;}}
.ph-stat{{text-align:center;}}
.ph-n{{display:block;font-size:26px;font-weight:800;color:var(--white);line-height:1;}}
.ph-l{{font-size:9px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.35);}}
.ph-pills{{
  max-width:1380px;margin:14px auto 0;
  display:flex;gap:8px;align-items:center;flex-wrap:wrap;
}}
.tpill{{
  padding:3px 11px;font-size:9.5px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:var(--white);
}}
.miru-note{{
  font-size:11px;font-weight:600;color:#7eb8ff;
  padding:3px 11px;border:1px solid rgba(126,184,255,.3);
}}

/* ── COUNTRY CARDS ──────────────────────────── */
.cards-grid{{
  max-width:1380px;margin:0 auto;
  padding:28px clamp(16px,4vw,80px) 40px;
  display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px;
}}
.ccard{{
  background:var(--white);border:1px solid var(--line);
  display:flex;flex-direction:column;
  transition:box-shadow .2s,transform .15s;
}}
.ccard:hover{{box-shadow:0 6px 24px rgba(5,25,94,.1);transform:translateY(-2px);}}
.ccard-head{{
  padding:14px 16px 11px;
  display:flex;align-items:center;gap:11px;
  border-bottom:1px solid var(--fog);
}}
.cc-flag{{font-size:26px;line-height:1;flex-shrink:0;}}
.cc-info{{flex:1;min-width:0;}}
.cc-name{{font-size:14.5px;font-weight:700;color:var(--charcoal);line-height:1.3;}}
.cc-en{{font-size:10.5px;font-weight:400;color:var(--slate);}}
.cc-iso{{font-size:9.5px;font-weight:700;letter-spacing:.14em;color:var(--accent2);margin-top:2px;}}
.mtype-badge{{
  padding:3px 9px;font-size:9.5px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:var(--white);flex-shrink:0;
}}
.pilot-badge{{
  margin-left:5px;padding:1px 5px;
  font-size:8px;font-weight:700;letter-spacing:.1em;
  background:var(--red);color:var(--white);vertical-align:middle;
}}
.tier-badge{{
  display:inline-block;padding:1px 6px;border-radius:3px;
  font-size:9px;font-weight:600;letter-spacing:.06em;vertical-align:middle;margin-left:4px;
}}
.opp-row:hover{{background:var(--fog2);}}
.ccard-body{{padding:11px 16px 10px;border-bottom:1px solid var(--fog);}}
.cc-row{{display:flex;align-items:baseline;gap:8px;padding:4px 0;}}
.cc-lbl{{
  font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:var(--accent2);flex-shrink:0;width:58px;
}}
.cc-val{{font-size:12px;font-weight:500;color:var(--charcoal);}}
.cc-val.miru-vendor{{color:var(--navy);font-weight:700;}}
.cc-val.cc-model{{font-size:11px;color:var(--slate);}}

/* portals */
.ccard-portals{{padding:10px 14px 12px;display:flex;flex-direction:column;gap:5px;flex:1;}}
.p-label{{
  font-size:8.5px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;
  color:var(--accent2);margin-bottom:4px;
}}
.portal-link{{
  display:flex;align-items:center;gap:7px;padding:6px 9px;
  border:1px solid var(--line);text-decoration:none;
  font-size:11px;font-weight:500;color:var(--charcoal);
  transition:border-color .18s,background .18s;
}}
.portal-link:not(.pl-dead):hover{{border-color:var(--navy);background:var(--fog2);}}
.pl-primary{{border-color:rgba(5,25,94,.2);background:var(--fog2);}}
.pl-dead{{color:var(--accent2);cursor:default;}}
.p-dot{{font-size:10px;flex-shrink:0;}}
.p-name{{flex:1;font-size:11px;}}
.p-st{{
  font-size:8.5px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
  color:var(--accent2);
}}
.pl-primary .p-st{{color:var(--accent);opacity:.7;}}

/* ── BIO/ERT CARD NOTE ─────────────────────────── */
.bio-note{{
  font-size:10px;color:var(--slate);
  padding:6px 14px 9px;border-top:1px solid var(--fog);
  font-style:italic;line-height:1.5;
}}

/* ── PANEL SWITCHING ─────────────────────────── */
.panel{{display:none;}}
.panel.active{{display:block;}}

/* ── KPI CLICKABLE ──────────────────────────── */
.kpi{{cursor:pointer;}}
.kpi:active{{transform:scale(.98);}}
.kpi-popup{{
  position:fixed;z-index:800;
  background:rgba(5,25,94,.97);color:var(--white);
  padding:0;min-width:260px;max-width:310px;
  box-shadow:0 8px 32px rgba(0,0,0,.35);
  border:1px solid rgba(255,255,255,.1);
  border-top:2px solid var(--red);
  display:none;overflow:hidden;
}}
.kpi-popup.open{{display:block;}}
.kpp-title{{font-size:9.5px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;
  color:var(--red);padding:12px 14px 8px;border-bottom:1px solid rgba(255,255,255,.08);}}
.kpp-scroll{{max-height:320px;overflow-y:auto;}}
.kpp-scroll::-webkit-scrollbar{{width:4px;}}
.kpp-scroll::-webkit-scrollbar-thumb{{background:rgba(255,255,255,.2);}}
.kpp-item{{display:flex;align-items:flex-start;gap:8px;padding:8px 14px;
  border-bottom:1px solid rgba(255,255,255,.06);cursor:pointer;transition:background .15s;}}
.kpp-item:hover{{background:rgba(255,255,255,.08);}}
.kpp-item:last-child{{border-bottom:none;}}
.kpp-flag{{font-size:16px;width:22px;text-align:center;flex-shrink:0;padding-top:1px;}}
.kpp-text{{flex:1;min-width:0;}}
.kpp-name{{font-size:12px;font-weight:600;line-height:1.3;}}
.kpp-portal{{font-size:10px;color:rgba(255,255,255,.45);margin-top:1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.kpp-go{{font-size:10px;color:rgba(255,255,255,.3);flex-shrink:0;padding-top:2px;}}

/* ── CATEGORY FILTER ────────────────────────── */
.cat-bar{{
  max-width:1380px;margin:28px auto 0;
  padding:0 clamp(16px,4vw,80px);
  display:flex;gap:6px;align-items:center;flex-wrap:wrap;
}}
.cat-btn{{
  padding:6px 18px;font-size:10.5px;font-weight:600;
  letter-spacing:.1em;text-transform:uppercase;
  cursor:pointer;border:1.5px solid var(--line);
  background:var(--white);color:var(--slate);transition:all .18s;
}}
.cat-btn.active{{background:var(--navy);color:var(--white);border-color:var(--navy);}}
.cat-btn:hover:not(.active){{border-color:var(--navy);color:var(--navy);}}
.cat-label{{font-size:10px;color:var(--accent2);font-weight:600;letter-spacing:.12em;
  text-transform:uppercase;margin-right:4px;}}

/* ── MAP TOOLTIP ────────────────────────────── */
.map-tip{{
  position:fixed;z-index:900;pointer-events:none;display:none;
  background:rgba(5,25,94,.97);color:var(--white);
  padding:11px 14px;max-width:260px;
  box-shadow:0 6px 24px rgba(0,0,0,.35);
  border:1px solid rgba(255,255,255,.1);
  border-top:2px solid var(--red);
}}
.mt-flag{{font-size:22px;margin-bottom:3px;display:block;}}
.mt-name{{font-size:13px;font-weight:700;}}
.mt-scope{{display:inline-block;padding:1px 7px;font-size:9px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;margin:4px 0;}}
.mt-vendor{{font-size:10.5px;color:rgba(255,255,255,.65);line-height:1.6;}}
.mt-product{{font-size:10.5px;color:rgba(255,255,255,.45);}}
.mt-note{{font-size:9.5px;color:#ffaa44;margin-top:4px;}}

/* ── WORLD MAP ──────────────────────────────── */
.world-map-wrap{{
  position:relative;width:100%;background:#112240;overflow:hidden;
  border:1px solid var(--line);
}}
.world-map-wrap canvas{{display:block;width:100%;}}

/* ── US TILE MAP ────────────────────────────── */
.us-flex{{display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap;}}
.us-tile-side{{flex:0 0 auto;}}
#usTileMap{{display:block;max-width:100%;}}
.us-chart-side{{flex:1;min-width:200px;}}
.us-legend-grid{{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:14px;}}
.usl{{display:flex;align-items:center;gap:6px;font-size:10.5px;}}
.usl-sq{{width:12px;height:12px;flex-shrink:0;}}
@media(max-width:960px){{.us-flex{{flex-direction:column;}}}}
@media(max-width:960px){{.chart-row{{grid-template-columns:1fr;}}}}

/* ── ABOUT PANEL ────────────────────────────── */
.ab-card{{
  background:var(--white);border:1px solid var(--line);border-radius:10px;
  padding:22px 24px;
}}
.ab-h3{{
  font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--navy);margin:0 0 16px;padding-bottom:10px;
  border-bottom:1px solid var(--line);
}}
.ab-src{{display:flex;align-items:flex-start;gap:10px;}}
.ab-src-dot{{
  width:7px;height:7px;border-radius:50%;background:var(--accent);
  flex-shrink:0;margin-top:4px;
}}
.ab-tech{{
  display:grid;grid-template-columns:160px 1fr;gap:8px;align-items:start;
  padding:6px 0;border-bottom:1px solid {B['fog2']};
}}
.ab-tech-label{{font-size:12px;font-weight:600;color:var(--navy);}}
.ab-tech-desc{{font-size:12px;color:var(--slate);}}
.ab-badge{{
  display:inline-block;padding:2px 8px;border-radius:20px;
  font-size:11px;font-weight:600;
}}

/* ── VENDOR CARDS ───────────────────────────── */
.vendor-section{{margin-bottom:32px;}}
.vs-header{{
  display:flex;align-items:center;padding:10px 16px;
  margin-bottom:16px;
}}
.vcards-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
  gap:16px;
}}
.vcard{{
  background:var(--white);border:1px solid var(--line);
  display:flex;flex-direction:column;
  transition:box-shadow .18s;
}}
.vcard:hover{{box-shadow:0 4px 20px rgba(5,25,94,.1);}}
.vcard-miru{{border-color:var(--navy);box-shadow:0 0 0 2px var(--navy)22;}}
.vcard-head{{
  display:flex;align-items:center;gap:10px;
  padding:12px 14px;border-bottom:1px solid var(--fog);
}}
.vc-flag{{font-size:22px;flex-shrink:0;}}
.vc-info{{flex:1;min-width:0;}}
.vc-name{{font-size:13px;font-weight:700;color:var(--charcoal);line-height:1.3;}}
.vc-hq{{font-size:10px;color:var(--steel);margin-top:2px;}}
.vc-overlap{{
  font-size:9px;font-weight:700;letter-spacing:.08em;
  padding:3px 8px;flex-shrink:0;white-space:nowrap;
}}
.vcard-body{{flex:1;padding:10px 14px;}}
.vc-row{{display:flex;align-items:baseline;gap:6px;margin-bottom:3px;}}
.vc-lbl{{font-size:9.5px;color:var(--accent2);font-weight:600;letter-spacing:.06em;width:46px;flex-shrink:0;}}
.vc-val{{font-size:11px;color:var(--charcoal);}}
.vc-tag{{
  display:inline-block;font-size:9px;padding:1px 7px;margin:2px 2px 0 0;
  background:var(--fog2);color:var(--slate);border:1px solid var(--line);
}}
.vc-cat{{
  display:inline-block;font-size:9px;padding:1px 7px;margin:2px 2px 0 0;
  background:var(--navy);color:#fff;
}}
.vc-markets{{
  margin-top:6px;font-size:10px;color:var(--slate);
  padding:4px 8px;background:var(--fog2);border-left:2px solid var(--red);
}}
.vc-news{{
  margin-top:8px;font-size:10px;color:var(--slate);line-height:1.5;
  border-top:1px solid var(--fog);padding-top:6px;font-style:italic;
}}
.vcard-footer{{
  display:flex;align-items:center;gap:8px;flex-wrap:wrap;
  padding:8px 14px;border-top:1px solid var(--fog);background:var(--fog2);
}}
.vc-link{{
  font-size:10px;font-weight:600;color:var(--navy);
  text-decoration:none;padding:3px 8px;border:1px solid var(--line);
  background:var(--white);
}}
.vc-link:hover{{background:var(--navy);color:#fff;}}

/* ── RESPONSIVE ─────────────────────────────── */
@media(max-width:960px){{.chart-row{{grid-template-columns:1fr;}}}}
@media(max-width:700px){{
  .ov-kpis{{flex-direction:column;}}
  .cards-grid{{grid-template-columns:1fr;}}
  .nav-kpis{{display:none;}}
  .ph-inner{{flex-direction:column;align-items:flex-start;}}
  .vcards-grid{{grid-template-columns:1fr;}}
}}
"""

# ─── Ticker items ──────────────────────────────────────────────────────────────
TICKER_ITEMS = [
    ("<strong>PHL 필리핀</strong>", "Miru FASTrAC ACM · 2024 COMELEC 계약"),
    ("<strong>COD 콩고DRC</strong>", "Miru DEV BMD · 2023 국가총선"),
    ("<strong>IRQ 이라크</strong>", "Miru PCOS/CCOS · 2017∼현재 IHEC"),
    ("<strong>KGZ 키르기스</strong>", "Miru PCOS 5-in-1 · 2018 CEC"),
    ("<strong>KOR 한국</strong>", "Miru 투표지분류기 · 2013∼현재"),
    ("<strong>BIH 보스니아</strong>", "Smartmatic SAES-1800 · 2026 신규"),
    ("<strong>ALB 알바니아</strong>", "Smartmatic A4-517 · 2025 파일럿"),
    ("<strong>BEL 벨기에</strong>", "Smartmatic bSmart500 · 2024"),
    ("<strong>GEO 조지아</strong>", "Smartmatic SAES-1800Plus · 2023"),
    ("<strong>BRA 브라질</strong>", "Positivo Urna Eletrônica UE2022 · 2021"),
    ("<strong>PRY 파라과이</strong>", "MSA BUE Boleta Única · 2023"),
    ("<strong>IND 인도</strong>", "BEL+ECIL M3 EVM+VVPAT · 전국"),
    ("<strong>MNG 몽골</strong>", "Dominion ImageCast · 2012"),
    ("<strong>EST 에스토니아</strong>", "i-Voting · 2005∼현재 전세계 최초"),
    ("<strong>OMN 오만</strong>", "Intakhib 모바일 · 2023"),
    ("<strong>검증완료</strong>", "25개국 53개 포털 · 2026-06-25 기준"),
]
def ticker_html():
    items = "".join(
        f'<div class="ticker-item">{a} · {b}</div>'
        for a,b in TICKER_ITEMS*2  # duplicate for seamless loop
    )
    return f"""
<div class="ticker-strip">
  <div class="ticker-lbl">Intel</div>
  <div class="ticker-wrap">
    <div class="ticker-inner">{items}</div>
  </div>
</div>"""

# ─── Assemble HTML ────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Election Technology Intelligence · Miru Systems</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
{"<script>" + CHARTJS + "</script>" if CHARTJS else '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'}
{"<script>" + TOPOJSON_JS + "</script>" if TOPOJSON_JS else '<script src="https://unpkg.com/topojson-client@3/dist/topojson-client.min.js"></script>'}
<style>{CSS}</style>
</head>
<body>

<!-- NAV -->
<nav class="top-nav">
  <div class="nav-brand">
    {"<img src='" + LOGO_SRC + "' alt='Miru Systems' class='nav-logo'>" if LOGO_SRC else ""}
    <div class="nav-divider"></div>
    <span class="nav-title">Election Intelligence</span>
  </div>
  <div class="nav-tabs">
    <button class="nav-tab active" data-panel="overview">🌐 Global Overview</button>
    <button class="nav-tab" data-panel="apac">🌏 Asia-Pacific</button>
    <button class="nav-tab" data-panel="europe">Europe</button>
    <button class="nav-tab" data-panel="americas">Americas &amp; Africa</button>
    <button class="nav-tab" data-panel="mena">Middle East &amp; Central Asia</button>
    <button class="nav-tab" data-panel="bio" style="color:rgba(255,255,255,.55);border-bottom-color:transparent;">🔍 생체인식·결과전송</button>
    <button class="nav-tab" data-panel="opportunity" style="color:#D4870A;border-bottom-color:#D4870A44;font-weight:600">📊 입찰 파이프라인</button>
    <button class="nav-tab" data-panel="vendor" style="color:rgba(255,255,255,.7);border-bottom-color:transparent;">🏭 공급사 인텔리전스</button>
    <button class="nav-tab" data-panel="about" style="color:rgba(255,255,255,.4);border-bottom-color:transparent;font-size:11px;">ℹ️ About</button>
  </div>
  <div class="nav-kpis">
    <div class="nk"><div class="nk-n">40</div><div class="nk-l">조달대상국</div></div>
    <div class="nk nk-miru"><div class="nk-n">5</div><div class="nk-l">Miru 납품</div></div>
  </div>
</nav>

<!-- PANEL: OVERVIEW -->
<div id="panel-overview" class="panel active">

  <div class="ov-hero">
    <div class="ov-inner">
      <div class="ov-eye">Election Technology Intelligence</div>
      <h1 class="ov-h1">기계투표 <em>25개국</em><br>글로벌 조달 인텔리전스</h1>
      <p class="ov-sub">전 세계 선거 기계화 현황 · 공급사 · 기기 · 조달 포털 — 검증일 2026.06.23</p>
      <div class="ov-kpis">
        <div class="kpi kpi-miru" data-kpi="miru" title="클릭하면 Miru 납품국 목록">
          <div class="kpi-n">5</div>
          <div class="kpi-l">Miru 납품국</div>
          <div class="kpi-s">KOR · PHL · IRQ · KGZ · COD</div>
        </div>
        <div class="kpi" data-kpi="mv" title="클릭하면 기계투표 국가 목록">
          <div class="kpi-n">25</div>
          <div class="kpi-l">기계투표 사용국</div>
          <div class="kpi-s">실도입 18 · 파일럿 3 — 투표·개표 기계화</div>
        </div>
        <div class="kpi" style="border-left:2px solid {B['green']}" data-kpi="bio" title="클릭하면 생체인식·ERT 국가 목록">
          <div class="kpi-n" style="color:{B['green']}">15</div>
          <div class="kpi-l">생체인식·결과전송국</div>
          <div class="kpi-s">e-Pollbook 11 · 생체+ERT 4 — 기계투표 미도입</div>
        </div>
        <div class="kpi" data-kpi="all" title="클릭하면 전체 국가 목록">
          <div class="kpi-n">40</div>
          <div class="kpi-l">총 조달 대상국</div>
          <div class="kpi-s">기계투표 25 + 생체인식·ERT 15</div>
        </div>
        <div class="kpi" style="border-left:2px solid #D4870A;cursor:pointer" onclick="document.querySelector('[data-panel=opportunity]').click()" title="입찰 파이프라인으로 이동">
          <div class="kpi-n" style="color:#D4870A">4</div>
          <div class="kpi-l" style="color:#D4870A">즉시 대응국</div>
          <div class="kpi-s">PRY·ARG·ARE·OMN — 입찰 진행중/임박</div>
        </div>
        <div class="kpi" data-kpi="portals" title="클릭하면 포털 현황으로 이동">
          <div class="kpi-n">71</div>
          <div class="kpi-l">검증 포털</div>
          <div class="kpi-s">기계투표 51 + 생체인식·ERT 20</div>
        </div>
      </div>
    </div>
    {ticker_html()}
  </div>

  <div class="chart-sec">

    <!-- Row 1: Non-USA vendor donut + Machine type bars -->
    <div class="chart-row">
      <div class="cbox">
        <div class="cbox-eye">Vendor Intelligence · Scope-M (기계투표)</div>
        <div class="cbox-title">기계투표 공급사 현황 <span style="font-size:13px;font-weight:400;color:var(--slate)">(미국 제외 23개국)</span></div>
        <div class="cbox-desc">Scope-M 기준: 투표·개표 기계화 국가 · 국가 수 비중 — 미국은 별도 EAC 차트 참조</div>
        <div class="chart-wrap"><canvas id="vendorChart"></canvas></div>
        <div class="v-legend" id="vLegend"></div>
      </div>
      <div class="cbox">
        <div class="cbox-eye">Technology Breakdown · Scope-M</div>
        <div class="cbox-title">기술 유형별 국가 분포</div>
        <div class="cbox-desc">25개국 · 기계투표 방식별 분류</div>
        <div class="type-dist" id="typeDist"></div>
        <div style="margin-top:18px;display:flex;flex-wrap:wrap;gap:7px">
          {"".join(f'<span style="font-size:10px;padding:2px 9px;background:{MTYPE_COLOR[t]};color:#fff">{t}</span>' for t in ["OMR","EVM","Internet","DRE","BMD","Mixed"])}
        </div>
      </div>
    </div>

    <!-- Row 2: World map -->
    <div class="chart-row full">
      <div class="cbox">
        <div class="cbox-eye">Global Coverage Map · 40개국</div>
        <div class="cbox-title">전 세계 선거기술 공급 현황 지도</div>
        <div class="cbox-desc">기계투표(Scope-M) · 생체인식·결과전송(Scope-B/R) · 커서를 올리면 국가 상세 정보 표시</div>
        <div class="world-map-wrap"><canvas id="worldMapCanvas" height="420"></canvas></div>
        <div style="display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:12px;">
          <div class="usl"><div class="usl-sq" style="background:#05195E"></div>Miru Systems</div>
          <div class="usl"><div class="usl-sq" style="background:#525252"></div>Smartmatic</div>
          <div class="usl"><div class="usl-sq" style="background:#123A9E"></div>BEL+ECIL</div>
          <div class="usl"><div class="usl-sq" style="background:#0A2A6E"></div>MSA 그룹</div>
          <div class="usl"><div class="usl-sq" style="background:#AEB7D6"></div>Dominion</div>
          <div class="usl"><div class="usl-sq" style="background:#C7CEDC"></div>Positivo</div>
          <div class="usl"><div class="usl-sq" style="background:#8C8C8C"></div>State/Public·기타</div>
          <div class="usl"><div class="usl-sq" style="background:#24A148"></div>생체인식·결과전송(Scope-B/R)</div>
        </div>
      </div>
    </div>

    <!-- Row 3: USA tile map + bar chart -->
    <div class="chart-row full">
      <div class="cbox">
        <div class="cbox-eye">USA · EAC EAVS 2022 · State-Level Intelligence</div>
        <div class="cbox-title">미국 주별 투표기기 공급사 현황</div>
        <div class="cbox-desc">EAC EAVS 2022 기준 · 커서를 올리면 주별 상세 표시 · Statewide=단독 계약 / Mixed=복수 공급사</div>
        <div class="us-flex">
          <div class="us-tile-side">
            <svg id="usTileMap" viewBox="0 0 552 360" xmlns="http://www.w3.org/2000/svg"></svg>
            <div class="us-legend-grid" id="usTileLegend"></div>
          </div>
          <div class="us-chart-side">
            <div style="font-size:11px;font-weight:600;color:var(--slate);margin-bottom:8px;letter-spacing:.06em;">주(State) 수 기준</div>
            <div class="chart-wrap" style="height:200px"><canvas id="usVendorChart"></canvas></div>
            <div style="margin-top:12px;font-size:10px;color:var(--slate);line-height:1.8;border-top:1px solid var(--line);padding-top:10px;">
              <strong style="color:var(--charcoal)">Statewide</strong> = 주 전체 단독 계약 &nbsp;|&nbsp;
              <strong style="color:var(--charcoal)">Total Presence</strong> = 1개+ 카운티 배포 포함 (중복)
            </div>
          </div>
        </div>
        <div style="margin-top:12px;font-size:10px;color:var(--slate);border-top:1px solid var(--line);padding-top:10px;">
          출처: EAC EAVS 2022 · Verified Voting · Brennan Center 2022 &nbsp;·&nbsp; ⚠️ IN · TN · MS · NJ · LA = 무용지 DRE 잔존 (2022 기준)
        </div>
      </div>
    </div>

    <!-- Row 4: Miru position -->
    <div class="chart-row full">
      <div class="miru-box">
        <div class="mb-eye">Miru Systems · Competitive Position</div>
        <div class="mb-h2">아시아·아프리카·중동 5개국 OMR/BMD 기계투표 납품 중</div>
        <div class="miru-grid">
          <div class="mc"><div class="mc-flag">🇰🇷</div><div class="mc-name">대한민국 KOR</div><div class="mc-detail">투표지분류기 · 전국<br>2013∼현재</div><span class="mc-mtype">OMR</span></div>
          <div class="mc"><div class="mc-flag">🇵🇭</div><div class="mc-name">필리핀 PHL</div><div class="mc-detail">FASTrAC ACM · 전국<br>2024 최신계약</div><span class="mc-mtype">OMR</span></div>
          <div class="mc"><div class="mc-flag">🇮🇶</div><div class="mc-name">이라크 IRQ</div><div class="mc-detail">PCOS/CCOS · 전국<br>2017∼현재 IHEC</div><span class="mc-mtype">OMR</span></div>
          <div class="mc"><div class="mc-flag">🇰🇬</div><div class="mc-name">키르기스스탄 KGZ</div><div class="mc-detail">PCOS 5-in-1 · 전국<br>2018 CEC</div><span class="mc-mtype">OMR</span></div>
          <div class="mc"><div class="mc-flag">🇨🇩</div><div class="mc-name">콩고DRC COD</div><div class="mc-detail">DEV 마킹장치 · 전국<br>2023 총선 CENI</div><span class="mc-mtype">BMD</span></div>
        </div>
      </div>
    </div>

    <!-- Row 3: Portal status -->
    <div class="chart-row full">
      <div class="status-box">
        <div class="cbox-eye">Portal Intelligence</div>
        <div class="cbox-title">조달 포털 접근성 현황</div>
        <div class="cbox-desc">40개국 71개 포털 검증 결과 — 기계투표 51 + 생체인식·ERT 20 — 2026-06-23</div>
        <div class="st-grid">
          <div class="st-item"><div class="st-n" style="color:{B['green']}">27</div><div class="st-l">Working</div></div>
          <div class="st-item"><div class="st-n" style="color:{B['steel']}">12</div><div class="st-l">정보 전용</div></div>
          <div class="st-item"><div class="st-n" style="color:{B['red']}">5</div><div class="st-l">접근불가</div></div>
          <div class="st-item"><div class="st-n" style="color:{B['accent']}">2</div><div class="st-l">Login 필요</div></div>
          <div class="st-item"><div class="st-n" style="color:#D4870A">2</div><div class="st-l">JS 렌더링</div></div>
          <div class="st-item"><div class="st-n" style="color:{B['accent2']}">2</div><div class="st-l">지역차단</div></div>
        </div>
        <div class="st-legend">
          <div class="sl"><span class="sl-dot" style="color:{B['green']}">●</span> Working — 직접 접근 가능</div>
          <div class="sl"><span class="sl-dot" style="color:{B['accent']}">●</span> Login — 계정 필요 (한국 G2B 등)</div>
          <div class="sl"><span class="sl-dot" style="color:#D4870A">●</span> JS 렌더링 — Playwright 필요 (BGR eOP, UZB xarid)</div>
          <div class="sl"><span class="sl-dot" style="color:{B['accent2']}">●</span> 지역차단 — 이란 SETAD 외부 geo-block</div>
          <div class="sl"><span class="sl-dot" style="color:{B['red']}">●</span> 접근불가 — URL 변경 또는 종료</div>
          <div class="sl"><span class="sl-dot" style="color:{B['steel']}">○</span> 정보 전용 — 조달 없음</div>
        </div>
      </div>
    </div>

  </div>
</div>

<!-- PANELS 2–5: machine voting regions -->
{region_panel("apac")}
{region_panel("europe")}
{region_panel("americas")}
{region_panel("mena")}

<!-- PANEL 6: Biometric / ERT -->
{bio_panel()}

<!-- PANEL 7: Opportunity Pipeline -->
{opportunity_panel()}

<!-- PANEL 8: Vendor Intelligence -->
{vendor_panel()}

<!-- PANEL 9: About -->
{about_panel()}

<!-- FOOTER -->
<footer style="background:var(--navy);color:rgba(255,255,255,.35);
  padding:20px clamp(16px,4vw,80px);font-size:11px;
  display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;
  border-top:1px solid rgba(255,255,255,.08);">
  <div style="display:flex;align-items:center;gap:14px;">
    {"<img src='" + LOGO_SRC + "' alt='Miru' style='height:20px;opacity:.6'>" if LOGO_SRC else ""}
    <span>Election Technology Intelligence · 검증일 2026-06-25 · 40개국 (기계투표 25 + 생체인식·ERT 15) · 계약 파이프라인 25개국</span>
  </div>
  <div style="text-align:right">내부 전략 문서 — 외부 배포 금지 · bhkim@mirusystems.com</div>
</footer>

<div class="map-tip" id="mapTip">
  <span class="mt-flag" id="mtFlag"></span>
  <div class="mt-name" id="mtName"></div>
  <span class="mt-scope" id="mtScope"></span>
  <div class="mt-vendor" id="mtVendor"></div>
  <div class="mt-product" id="mtProduct"></div>
  <div class="mt-note" id="mtNote"></div>
</div>
<div class="kpi-popup" id="kpiPopup">
  <div class="kpp-title" id="kppTitle"></div>
  <div class="kpp-scroll" id="kppItems"></div>
</div>

<script>
// ══ Panel switching ══════════════════════════════════════════════════════════
function showPanel(panelId) {{
  document.querySelectorAll('.panel').forEach(p => {{
    p.classList.remove('active'); p.style.display = 'none';
  }});
  const t = document.getElementById('panel-' + panelId);
  if (t) {{ t.classList.add('active'); t.style.display = 'block'; }}
}}
document.addEventListener('DOMContentLoaded', () => showPanel('overview'));
document.querySelectorAll('.nav-tab').forEach(t => {{
  t.addEventListener('click', () => {{
    document.querySelectorAll('.nav-tab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    showPanel(t.dataset.panel);
    window.scrollTo({{top:0,behavior:'smooth'}});
  }});
}});

// ══ KPI block popup (입찰 포털 바로가기) ════════════════════════════════════
const KPI_DATA = {KPI_PORTAL_JSON};

const popup = document.getElementById('kpiPopup');
let popupOpen = false;
document.querySelectorAll('[data-kpi]').forEach(kpi => {{
  kpi.addEventListener('click', e => {{
    e.stopPropagation();
    const key = kpi.dataset.kpi;
    const d = KPI_DATA[key];
    if (!d) return;
    document.getElementById('kppTitle').textContent = d.title;
    const scrollEl = document.getElementById('kppItems');
    scrollEl.innerHTML = '';
    d.items.forEach(item => {{
      const div = document.createElement('div');
      div.className = 'kpp-item';
      const isLink = !!item.url;
      div.innerHTML = `
        <span class="kpp-flag">${{item.flag}}</span>
        <div class="kpp-text">
          <div class="kpp-name">${{item.name}}</div>
          <div class="kpp-portal">${{item.portal || (isLink ? '' : '패널 이동')}}</div>
        </div>
        <span class="kpp-go">${{isLink ? '🔗' : '▶'}}</span>`;
      div.addEventListener('click', e2 => {{
        e2.stopPropagation();
        popup.classList.remove('open'); popupOpen = false;
        if (isLink) {{
          window.open(item.url, '_blank', 'noopener,noreferrer');
        }} else if (item.panel) {{
          document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
          const tab = document.querySelector(`.nav-tab[data-panel="${{item.panel}}"]`);
          if (tab) tab.classList.add('active');
          showPanel(item.panel);
          window.scrollTo({{top:0,behavior:'smooth'}});
        }}
      }});
      scrollEl.appendChild(div);
    }});
    const rect = kpi.getBoundingClientRect();
    const left = Math.min(rect.left, window.innerWidth - 320);
    const top  = rect.bottom + 8;
    popup.style.left = left + 'px';
    popup.style.top  = top  + 'px';
    popup.classList.add('open'); popupOpen = true;
  }});
}});
document.addEventListener('click', () => {{
  if (popupOpen) {{ popup.classList.remove('open'); popupOpen = false; }}
}});

// ══ Vendor donut: 미국 제외 23개국 ════════════════════════════════════════════
const vd = {json.dumps(nonusa_vendor_chart)};
new Chart(document.getElementById('vendorChart').getContext('2d'), {{
  type:'doughnut',
  data:{{ labels:vd.labels, datasets:[{{data:vd.data,backgroundColor:vd.colors,borderWidth:2,borderColor:'#fff',hoverOffset:5}}] }},
  options:{{
    responsive:true,maintainAspectRatio:false,cutout:'60%',
    plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>` ${{c.label}}: ${{c.parsed}}개국`}}}}}}
  }}
}});
const leg = document.getElementById('vLegend');
vd.labels.forEach((l,i) => {{
  leg.innerHTML += `<div class="vl"><div class="vl-dot" style="background:${{vd.colors[i]}}"></div><span>${{l}} <b>${{vd.data[i]}}개국</b></span></div>`;
}});

// ══ USA bar chart ════════════════════════════════════════════════════════════
const usvd = {json.dumps(us_vendor_chart)};
new Chart(document.getElementById('usVendorChart').getContext('2d'), {{
  type:'bar',
  data:{{ labels:usvd.labels, datasets:[
    {{label:'Total Presence (주)',data:usvd.present,backgroundColor:usvd.colors.map(c=>c+'55'),borderColor:usvd.colors,borderWidth:2}},
    {{label:'Statewide Contract (주)',data:usvd.statewide,backgroundColor:usvd.colors,borderColor:usvd.colors,borderWidth:0}}
  ]}},
  options:{{
    indexAxis:'y',responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{display:true,position:'bottom',labels:{{font:{{size:10}},boxWidth:12,padding:12}}}},tooltip:{{callbacks:{{label:c=>` ${{c.dataset.label}}: ${{c.parsed.x}}개 주`}}}}}},
    scales:{{x:{{max:55,grid:{{color:'rgba(0,0,0,0.05)'}},ticks:{{font:{{size:10}},callback:v=>v+'개'}}}},y:{{ticks:{{font:{{size:12,weight:'600'}}}}}}}}
  }}
}});

// ══ Type bars ════════════════════════════════════════════════════════════════
const td = {json.dumps(type_chart)};
const tot = td.data.reduce((a,b)=>a+b,0);
const el = document.getElementById('typeDist');
td.labels.forEach((l,i) => {{
  const pct = Math.round(td.data[i]/tot*100);
  el.innerHTML += `<div class="td-row"><div class="td-lbl">${{l}}</div><div class="td-wrap"><div class="td-bar" style="width:${{td.data[i]/tot*100}}%;background:${{td.colors[i]}}"><span class="td-n">${{td.data[i]}}개</span></div></div><span class="td-pct">${{pct}}%</span></div>`;
}});

// ══ World map — TopoJSON choropleth ══════════════════════════════════════════
(function() {{
  const canvas = document.getElementById('worldMapCanvas');
  if (!canvas) return;

  // 데이터
  const dots   = {WORLD_DOTS};
  const isoNum = {json.dumps(ISO3_NUM)};
  const tip    = document.getElementById('mapTip');

  // ISO numeric → dot lookup
  const numToDot = {{}};
  dots.forEach(d => {{
    const num = isoNum[d.iso];
    if (num !== undefined) numToDot[num] = d;
  }});

  // 캔버스 크기 — Natural Earth 고유 비율(2.04:1) 적용
  const W = canvas.width  = canvas.parentElement.clientWidth || 900;
  const H = canvas.height = Math.round(W * 0.49);

  // Natural Earth projection (D3 없이 구현)
  // xMax = π × 0.8707 ≈ 2.7353,  yMax = y at lat=85° ≈ 1.3401
  const NE_XMAX = 2.7353;
  const NE_YMAX = 1.3401;
  function project(lon, lat) {{
    const l   = lon * Math.PI / 180;
    const phi = Math.min(Math.max(lat, -85), 85) * Math.PI / 180;
    const k   = 0.8707 - 0.131979*phi*phi + phi*phi*phi*phi*(-0.013791 + phi*phi*(0.003971 - 0.001529*phi*phi));
    const x   = l * k;
    const y   = phi * (1.0074 + phi*phi*(-0.047713 + 0.000229*phi*phi));
    return [
      (x / NE_XMAX + 1) / 2 * W,
      (-y / NE_YMAX + 1) / 2 * H
    ];
  }}

  const ctx = canvas.getContext('2d');

  function drawMap(worldTopo) {{
    // 바다 배경
    ctx.fillStyle = '#1b3d5f';
    ctx.fillRect(0, 0, W, H);

    // 국가 면 채우기 (TopoJSON)
    if (worldTopo && typeof topojson !== 'undefined') {{
      const countries = topojson.feature(worldTopo, worldTopo.objects.countries);
      countries.features.forEach(feat => {{
        const numId = parseInt(feat.id);
        const dot   = numToDot[numId];
        const fill  = dot ? dot.c : '#2a4e30';
        const sw    = dot ? 0.8 : 0.3;
        const sc    = dot ? 'rgba(255,255,255,0.45)' : '#1d3d24';

        function ring(coords) {{
          ctx.beginPath();
          coords.forEach(([lo,la],i) => {{
            const [x,y] = project(lo,la);
            i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
          }});
          ctx.closePath();
          ctx.fillStyle = fill; ctx.fill('evenodd');
          ctx.strokeStyle = sc; ctx.lineWidth = sw; ctx.stroke();
        }}
        const g = feat.geometry;
        if (!g) return;
        if (g.type === 'Polygon')      ring(g.coordinates[0]);
        if (g.type === 'MultiPolygon') g.coordinates.forEach(p => ring(p[0]));
      }});

      // 내부 국경선
      const mesh = topojson.mesh(worldTopo, worldTopo.objects.countries, (a,b) => a!==b);
      ctx.beginPath();
      (function drawMesh(obj) {{
        if (obj.type==='LineString') {{
          obj.coordinates.forEach(([lo,la],i) => {{
            const [x,y]=project(lo,la); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
          }});
        }} else if (obj.type==='MultiLineString') {{
          obj.coordinates.forEach(line => line.forEach(([lo,la],i) => {{
            const [x,y]=project(lo,la); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
          }}));
        }}
      }})(mesh);
      ctx.strokeStyle='rgba(255,255,255,0.15)'; ctx.lineWidth=0.4; ctx.stroke();
    }} else {{
      // TopoJSON 없을 때 대륙 polygon fallback
      function fp(pts,fill) {{
        ctx.beginPath();
        pts.forEach(([lo,la],i) => {{ const [x,y]=project(lo,la); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); }});
        ctx.closePath(); ctx.fillStyle=fill; ctx.fill();
        ctx.strokeStyle='#1d3d24'; ctx.lineWidth=0.5; ctx.stroke();
      }}
      const CF='#2a4e30';
      fp([[-168,72],[-60,72],[-60,45],[-80,25],[-88,16],[-83,10],[-78,8],[-105,20],[-120,31],[-120,50],[-168,72]],CF);
      fp([[-80,12],[-62,8],[-35,-4],[-35,-56],[-68,-55],[-75,-35],[-80,12]],CF);
      fp([[-12,36],[36,37],[40,60],[30,70],[0,62],[-10,52],[-12,36]],CF);
      fp([[-18,37],[52,12],[50,-15],[36,-35],[16,-35],[-18,10],[-18,37]],CF);
      fp([[26,37],[145,37],[145,75],[60,75],[26,70],[26,37]],CF);
      fp([[113,-17],[154,-17],[154,-44],[113,-44],[113,-17]],CF);
    }}

    // 점 마커 (hover 타겟 + Miru 강조)
    dots.forEach(d => {{
      const [x,y] = project(d.lon, d.lat);
      const r = d.scope==='M' ? 6 : 4.5;
      ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2);
      ctx.fillStyle = d.c; ctx.fill();
      ctx.strokeStyle='rgba(255,255,255,0.85)'; ctx.lineWidth=1.2; ctx.stroke();
      if (d.vendor==='Miru Systems') {{
        ctx.beginPath(); ctx.arc(x,y,r+3.5,0,Math.PI*2);
        ctx.strokeStyle='rgba(235,4,20,0.7)'; ctx.lineWidth=1.8; ctx.stroke();
      }}
    }});
  }}

  // 지도 렌더링 — TopoJSON 데이터 주입 (인라인 JSON)
  const worldTopo = {WORLD_ATLAS if WORLD_ATLAS else 'null'};
  drawMap(worldTopo);

  // Hover (점 근접 감지)
  canvas.addEventListener('mousemove', e => {{
    const rect = canvas.getBoundingClientRect();
    const sx = W/rect.width, sy = H/rect.height;
    const mx = (e.clientX-rect.left)*sx, my = (e.clientY-rect.top)*sy;
    let found=null, minD=20;
    dots.forEach(d => {{
      const [x,y]=project(d.lon,d.lat);
      const dist=Math.sqrt((mx-x)**2+(my-y)**2);
      if (dist<minD) {{ minD=dist; found=d; }}
    }});
    if (found) {{
      document.getElementById('mtFlag').textContent    = found.flag;
      document.getElementById('mtName').textContent    = found.name;
      const se = document.getElementById('mtScope');
      se.textContent   = found.scope==='M'?'기계투표 Scope-M':'생체인식·ERT Scope-B/R';
      se.style.background = found.scope==='M'?'#05195E':'#24A148';
      document.getElementById('mtVendor').textContent  = '공급사: '+found.vendor;
      document.getElementById('mtProduct').textContent = found.product;
      document.getElementById('mtNote').textContent    = '';
      tip.style.display='block';
      tip.style.left=(e.clientX+16)+'px'; tip.style.top=(e.clientY-12)+'px';
      canvas.style.cursor='pointer';
    }} else {{
      tip.style.display='none'; canvas.style.cursor='default';
    }}
  }});
  canvas.addEventListener('mouseleave',()=>{{tip.style.display='none';}});
}})();

// ══ US tile map SVG ══════════════════════════════════════════════════════════
(function() {{
  const tiles  = {US_TILES_JSON};
  const vdrs   = {US_TILE_VDR};
  const notes  = {US_TILE_NOTES};
  const svg    = document.getElementById('usTileMap');
  const tip    = document.getElementById('mapTip');
  if (!svg) return;

  const CW=44, CH=36, GAP=2, COLS=12, ROWS=8;
  const W = COLS*(CW+GAP), H = ROWS*(CH+GAP);
  svg.setAttribute('viewBox', `0 0 ${{W}} ${{H}}`);
  svg.setAttribute('width', W); svg.setAttribute('height', H);

  Object.entries(tiles).forEach(([state,[col,row,vkey]]) => {{
    const v = vdrs[vkey] || {{label:'?',color:'#ccc',note:''}};
    const x = col*(CW+GAP), y = row*(CH+GAP);
    const g = document.createElementNS('http://www.w3.org/2000/svg','g');
    g.style.cursor = 'pointer';

    const rect = document.createElementNS('http://www.w3.org/2000/svg','rect');
    rect.setAttribute('x', x); rect.setAttribute('y', y);
    rect.setAttribute('width', CW); rect.setAttribute('height', CH);
    rect.setAttribute('fill', v.color);
    rect.setAttribute('rx', '3');
    g.appendChild(rect);

    const txt = document.createElementNS('http://www.w3.org/2000/svg','text');
    txt.setAttribute('x', x + CW/2); txt.setAttribute('y', y + CH/2 + 4);
    txt.setAttribute('text-anchor','middle');
    txt.setAttribute('fill','rgba(255,255,255,0.9)');
    txt.setAttribute('font-size','10'); txt.setAttribute('font-weight','700');
    txt.setAttribute('font-family','Inter,sans-serif');
    txt.textContent = state;
    g.appendChild(txt);

    g.addEventListener('mouseenter', e => {{
      rect.setAttribute('opacity','0.8');
      document.getElementById('mtFlag').textContent = '';
      document.getElementById('mtName').textContent = state;
      const scopeEl = document.getElementById('mtScope');
      scopeEl.textContent = v.label; scopeEl.style.background = v.color;
      document.getElementById('mtVendor').textContent = v.note;
      document.getElementById('mtProduct').textContent = notes[state] || '';
      document.getElementById('mtNote').textContent = '';
      tip.style.display = 'block';
    }});
    g.addEventListener('mousemove', e => {{
      tip.style.left = (e.clientX + 14) + 'px';
      tip.style.top  = (e.clientY - 10) + 'px';
    }});
    g.addEventListener('mouseleave', () => {{
      rect.setAttribute('opacity','1');
      tip.style.display = 'none';
    }});
    svg.appendChild(g);
  }});

  // Legend
  const legEl = document.getElementById('usTileLegend');
  if (legEl) {{
    Object.entries(vdrs).forEach(([key,v]) => {{
      legEl.innerHTML += `<div class="usl"><div class="usl-sq" style="background:${{v.color}}"></div>${{v.label}}</div>`;
    }});
  }}
}})();
</script>
</body>
</html>"""

os.makedirs("data", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = len(HTML)//1024
print(f"생성 완료: {OUT}  ({size_kb} KB)")
print(f"국가 카드: {HTML.count('class=\"ccard\"')}개")
print(f"포털 링크: {HTML.count('class=\"portal-link')}개")
