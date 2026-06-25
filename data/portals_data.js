// Auto-generated from election_technology_world.db — do not edit manually.
// Run: python scripts/gen_portals_data_js.py

window.MIRU_PORTALS = [
  {
    "id": 1,
    "country": "Brazil",
    "country_ko": "브라질",
    "iso3": "BRA",
    "region": "Americas",
    "name": "Compras.gov.br (PNCP)",
    "url": "https://pncp.gov.br/app/editais",
    "portal_type": "국가조달",
    "lang": "pt",
    "crawl_id": "CRAWL-176",
    "priority": "High",
    "notes": "연방 전기관 의무게시. PNCP=Portal Nacional de Contratações Públicas",
    "isMiru": false,
    "vendors": [],
    "feasibility": "High",
    "site_type": "REST API (공개)",
    "crawl_method": "API 직접 호출",
    "api_endpoint": "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacoes?dataInicial=&dataFinal=&pagina=1"
  },
  {
    "id": 2,
    "country": "Brazil",
    "country_ko": "브라질",
    "iso3": "BRA",
    "region": "Americas",
    "name": "TSE 조달공고",
    "url": "https://www.tse.jus.br/transparencia-e-prestacao-de-contas/licitacoes-e-contratos/licitacoes",
    "portal_type": "EMB조달",
    "lang": "pt",
    "crawl_id": "CRAWL-104",
    "priority": "High",
    "notes": "URL 변경됨: /transparencia/gestao-de-contratacoes → /transparencia-e-prestacao-de-contas/...",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "JS-SPA + WAF",
    "crawl_method": "Playwright",
    "api_endpoint": "없음(XHR 탐색 필요)"
  },
  {
    "id": 3,
    "country": "Brazil",
    "country_ko": "브라질",
    "iso3": "BRA",
    "region": "Americas",
    "name": "ComprasNet",
    "url": "https://www.gov.br/compras/pt-br",
    "portal_type": "국가조달(구)",
    "lang": "pt",
    "crawl_id": "CRAWL-103",
    "priority": "Med",
    "notes": "구 ComprasNet → PNCP 전환 중. 병행 운영",
    "isMiru": false,
    "vendors": [],
    "feasibility": "High",
    "site_type": "REST API (공개)",
    "crawl_method": "API 직접 호출",
    "api_endpoint": "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacoes?dataInicial=&dataFinal=&pagina=1"
  },
  {
    "id": 4,
    "country": "Paraguay",
    "country_ko": "파라과이",
    "iso3": "PRY",
    "region": "Americas",
    "name": "DNCP (Contrataciones)",
    "url": "https://www.contrataciones.gov.py/",
    "portal_type": "국가조달",
    "lang": "es",
    "crawl_id": "CRAWL-146",
    "priority": "High",
    "notes": "OCDS 표준 API 제공. Miru 타깃 포털",
    "isMiru": false,
    "vendors": [],
    "feasibility": "High",
    "site_type": "REST API (OCDS)",
    "crawl_method": "API 직접 호출 (이미 구현)",
    "api_endpoint": "https://www.contrataciones.gov.py/datos/api/v3/doc/"
  },
  {
    "id": 5,
    "country": "Venezuela",
    "country_ko": "베네수엘라",
    "iso3": "VEN",
    "region": "Americas",
    "name": "SNC (Servicio Nacional de Contrataciones)",
    "url": "https://www.snc.gob.ve/",
    "portal_type": "국가조달",
    "lang": "es",
    "crawl_id": "",
    "priority": "Low",
    "notes": "직접 입찰 목록 없음. 홈페이지 Servicios en Línea 통해 접근. CNE는 비공개 조달",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Low",
    "site_type": "정적HTML",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음"
  },
  {
    "id": 6,
    "country": "Venezuela",
    "country_ko": "베네수엘라",
    "iso3": "VEN",
    "region": "Americas",
    "name": "CNE",
    "url": "https://www.cne.gob.ve/",
    "portal_type": "선거위",
    "lang": "es",
    "crawl_id": "",
    "priority": "Low",
    "notes": "사이트 접근 불가 (ECONNREFUSED). CNE는 공개 조달 없음. SNC로 대체",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Low",
    "site_type": "접근불가",
    "crawl_method": "불가",
    "api_endpoint": "없음"
  },
  {
    "id": 7,
    "country": "DRC",
    "country_ko": "콩고(DRC)",
    "iso3": "COD",
    "region": "Africa",
    "name": "ARMP (marchepublic.cd)",
    "url": "https://marchepublic.cd/",
    "portal_type": "국가조달",
    "lang": "fr",
    "crawl_id": "CRAWL-130",
    "priority": "High",
    "notes": "Form 기반 검색. CENI 기관명으로 필터. CENI 자체 사이트(ceni.cd)는 조달 없음",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "Med",
    "site_type": "서버 오류(일시적)",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음(복구 후 재확인)"
  },
  {
    "id": 8,
    "country": "Bhutan",
    "country_ko": "부탄",
    "iso3": "BTN",
    "region": "Asia-Pacific",
    "name": "e-GP Bhutan",
    "url": "https://www.egp.gov.bt/",
    "portal_type": "국가조달",
    "lang": "en",
    "crawl_id": "",
    "priority": "High",
    "notes": "재무부 전자조달. 전기관 의무 게시",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "정적HTML (서버사이드)",
    "crawl_method": "requests(정적)",
    "api_endpoint": "https://www.egp.gov.bt/resources/common/TenderListing.jsp?h=t"
  },
  {
    "id": 9,
    "country": "Bhutan",
    "country_ko": "부탄",
    "iso3": "BTN",
    "region": "Asia-Pacific",
    "name": "ECB Tender",
    "url": "https://www.ecb.bt/tender",
    "portal_type": "EMB조달",
    "lang": "en",
    "crawl_id": "",
    "priority": "High",
    "notes": "/tender-information/ 는 2017년 아카이브. 현행 URL: /tender",
    "isMiru": false,
    "vendors": [],
    "feasibility": "High",
    "site_type": "WordPress 정적HTML",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음(WordPress REST API 가능: /wp-json/wp/v2/posts?categories=tender)"
  },
  {
    "id": 10,
    "country": "India",
    "country_ko": "인도",
    "iso3": "IND",
    "region": "Asia-Pacific",
    "name": "eProcure (GeM/CPPP)",
    "url": "https://eprocure.gov.in/cppp/tendersearch",
    "portal_type": "국가조달",
    "lang": "en",
    "crawl_id": "CRAWL-050",
    "priority": "High",
    "notes": "ECI EVM 조달은 BEL·ECIL 직접계약(정부간). eProcure에 공고",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "정적HTML",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음(직접 파싱)"
  },
  {
    "id": 11,
    "country": "India",
    "country_ko": "인도",
    "iso3": "IND",
    "region": "Asia-Pacific",
    "name": "ECI Tender",
    "url": "https://www.eci.gov.in/notification/tenders",
    "portal_type": "EMB조달",
    "lang": "en",
    "crawl_id": "CRAWL-169",
    "priority": "High",
    "notes": "403 반환. eprocure.gov.in에서 ECI 기관 필터 사용 권장",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Low",
    "site_type": "Cloudflare/WAF 차단",
    "crawl_method": "Playwright (WAF 우회)",
    "api_endpoint": "없음"
  },
  {
    "id": 12,
    "country": "India",
    "country_ko": "인도",
    "iso3": "IND",
    "region": "Asia-Pacific",
    "name": "CPPP",
    "url": "https://eprocure.gov.in/cppp/tendersearch",
    "portal_type": "국가조달(부)",
    "lang": "en",
    "crawl_id": "CRAWL-052",
    "priority": "Med",
    "notes": "Central Public Procurement Portal",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "정적HTML",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음(직접 파싱)"
  },
  {
    "id": 13,
    "country": "Albania",
    "country_ko": "알바니아",
    "iso3": "ALB",
    "region": "Europe",
    "name": "APP e-Procurement",
    "url": "https://app.gov.al/e-procurement/",
    "portal_type": "국가조달",
    "lang": "sq",
    "crawl_id": "CRAWL-085",
    "priority": "High",
    "notes": "Public Procurement Agency. Smartmatic EVM 계약 공고",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "Med",
    "site_type": "JSF 정적HTML",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음(직접 파싱)"
  },
  {
    "id": 14,
    "country": "Albania",
    "country_ko": "알바니아",
    "iso3": "ALB",
    "region": "Europe",
    "name": "KQZ (CEC Albania)",
    "url": "https://kqz.gov.al/",
    "portal_type": "선거위",
    "lang": "sq/en",
    "crawl_id": "CRAWL-086",
    "priority": "High",
    "notes": "Next.js 재구축. 조달 섹션 없음. APP e-Procurement에서 KQZ 기관명으로 검색",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "High",
    "site_type": "WordPress 정적HTML",
    "crawl_method": "requests(정적)",
    "api_endpoint": "/wp-json/wp/v2/posts?search=prokurimi"
  },
  {
    "id": 15,
    "country": "Belgium",
    "country_ko": "벨기에",
    "iso3": "BEL",
    "region": "Europe",
    "name": "e-Notification (publicprocurement.be)",
    "url": "https://enot.publicprocurement.be/enot-war/searchNotice.do",
    "portal_type": "국가조달",
    "lang": "nl/fr",
    "crawl_id": "",
    "priority": "High",
    "notes": "EU 외부에서 연결 차단될 수 있음. BOSA eProcurement 시스템",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "Med",
    "site_type": "접근불가(방화벽)",
    "crawl_method": "TED EU API 대체",
    "api_endpoint": "TED API: https://ted.europa.eu/api/v3.0/notices/search (이미 구현)"
  },
  {
    "id": 16,
    "country": "Belgium",
    "country_ko": "벨기에",
    "iso3": "BEL",
    "region": "Europe",
    "name": "e-Tendering Belgium",
    "url": "https://www.publicprocurement.be/etendering/home.do",
    "portal_type": "국가조달(제출)",
    "lang": "nl/fr",
    "crawl_id": "",
    "priority": "Med",
    "notes": "입찰서 제출용",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "Med",
    "site_type": "접근불가(방화벽)",
    "crawl_method": "TED EU API 대체",
    "api_endpoint": "TED API: https://ted.europa.eu/api/v3.0/notices/search (이미 구현)"
  },
  {
    "id": 17,
    "country": "Oman",
    "country_ko": "오만",
    "iso3": "OMN",
    "region": "Middle East",
    "name": "Tender Board Oman",
    "url": "https://etendering.tenderboard.gov.om",
    "portal_type": "국가조달",
    "lang": "ar/en",
    "crawl_id": "",
    "priority": "High",
    "notes": "공개 대시보드 2,262개+ 공고. /ctm/Am/PublicSearchTender.html WAF 차단됨",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "정적HTML+JS",
    "crawl_method": "requests + JS탭처리",
    "api_endpoint": "없음(직접 파싱 또는 Playwright)"
  },
  {
    "id": 18,
    "country": "UAE",
    "country_ko": "아랍에미리트",
    "iso3": "ARE",
    "region": "Middle East",
    "name": "Federal e-Procurement UAE",
    "url": "https://mof.gov.ae/en/public-finance/government-procurement/current-business-opportunities/",
    "portal_type": "국가조달",
    "lang": "ar/en",
    "crawl_id": "",
    "priority": "Med",
    "notes": "procurement.gov.ae는 로그인 전용. MoF 공개 목록 페이지 사용",
    "isMiru": false,
    "vendors": [
      "Scytl"
    ],
    "feasibility": "Med",
    "site_type": "JS-SPA (Vue/React 추정)",
    "crawl_method": "Playwright",
    "api_endpoint": "없음(XHR 탐색 필요)"
  },
  {
    "id": 19,
    "country": "UAE",
    "country_ko": "아랍에미리트",
    "iso3": "ARE",
    "region": "Middle East",
    "name": "UAE NEC",
    "url": "https://uaenec.ae/en",
    "portal_type": "선거위",
    "lang": "ar/en",
    "crawl_id": "",
    "priority": "Med",
    "notes": "NEC 정보 사이트. 조달 없음. FNC 선거는 제한된 선거인단 방식",
    "isMiru": false,
    "vendors": [
      "Scytl"
    ],
    "feasibility": "N/A",
    "site_type": "정적HTML",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 20,
    "country": "Ghana",
    "country_ko": "가나",
    "iso3": "GHA",
    "region": "Africa",
    "name": "Ghana e-Procurement",
    "url": "https://www.ghaneps.gov.gh/epps/home.do",
    "portal_type": "국가조달",
    "lang": "en",
    "crawl_id": "CRAWL-025",
    "priority": "High",
    "notes": "PPA(Public Procurement Authority). EC Ghana 입찰도 여기 게시",
    "isMiru": false,
    "vendors": [],
    "feasibility": "High",
    "site_type": "Struts 정적HTML",
    "crawl_method": "requests(정적)",
    "api_endpoint": "https://www.ghaneps.gov.gh/epps/quickSearchAction.do?searchSelect=6"
  },
  {
    "id": 21,
    "country": "Ghana",
    "country_ko": "가나",
    "iso3": "GHA",
    "region": "Africa",
    "name": "EC Ghana",
    "url": "https://ec.gov.gh/",
    "portal_type": "선거위",
    "lang": "en",
    "crawl_id": "CRAWL-026",
    "priority": "High",
    "notes": "Electoral Commission. BVMS/OMR 조달공고 직접 게시",
    "isMiru": false,
    "vendors": [],
    "feasibility": "N/A",
    "site_type": "WordPress",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 22,
    "country": "South Africa",
    "country_ko": "남아공",
    "iso3": "ZAF",
    "region": "Africa",
    "name": "eTenders Treasury",
    "url": "https://etenders.treasury.gov.za/",
    "portal_type": "국가조달",
    "lang": "en",
    "crawl_id": "CRAWL-031",
    "priority": "High",
    "notes": "국고부 전자입찰. IEC 조달공고도 여기",
    "isMiru": false,
    "vendors": [
      "Ren-Form"
    ],
    "feasibility": "Low",
    "site_type": "접근불가",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 23,
    "country": "South Africa",
    "country_ko": "남아공",
    "iso3": "ZAF",
    "region": "Africa",
    "name": "IEC South Africa",
    "url": "https://www.elections.org.za/",
    "portal_type": "선거위",
    "lang": "en",
    "crawl_id": "CRAWL-032",
    "priority": "High",
    "notes": "VMD 입찰공고 직접 게시. Ren-Form Litho R566M 계약",
    "isMiru": false,
    "vendors": [
      "Ren-Form"
    ],
    "feasibility": "Low",
    "site_type": "Cloudflare 차단",
    "crawl_method": "Playwright+UA변경",
    "api_endpoint": "없음"
  },
  {
    "id": 24,
    "country": "Dominican Republic",
    "country_ko": "도미니카공화국",
    "iso3": "DOM",
    "region": "Americas",
    "name": "DGCP Dominican Republic",
    "url": "https://www.dgcp.gob.do/consultas/",
    "portal_type": "국가조달",
    "lang": "es",
    "crawl_id": "CRAWL-100",
    "priority": "High",
    "notes": "Dirección General de Contrataciones Públicas",
    "isMiru": false,
    "vendors": [
      "Indra"
    ],
    "feasibility": "Med",
    "site_type": "HTML+JS SPA",
    "crawl_method": "Playwright",
    "api_endpoint": "대안: https://datosabiertos.dgcp.gob.do/api/ (오픈API)"
  },
  {
    "id": 25,
    "country": "Dominican Republic",
    "country_ko": "도미니카공화국",
    "iso3": "DOM",
    "region": "Americas",
    "name": "JCE (Junta Central Electoral)",
    "url": "https://jce.gob.do/",
    "portal_type": "선거위",
    "lang": "es",
    "crawl_id": "CRAWL-101",
    "priority": "High",
    "notes": "JCE 직접 OMR+생체 장비 조달",
    "isMiru": false,
    "vendors": [
      "Indra"
    ],
    "feasibility": "Med",
    "site_type": "HTML+JS SPA",
    "crawl_method": "Playwright",
    "api_endpoint": "대안: https://datosabiertos.dgcp.gob.do/api/ (오픈API)"
  },
  {
    "id": 26,
    "country": "Mongolia",
    "country_ko": "몽골",
    "iso3": "MNG",
    "region": "Asia-Pacific",
    "name": "State Procurement Platform",
    "url": "https://www.tender.gov.mn/en",
    "portal_type": "국가조달",
    "lang": "mn/en",
    "crawl_id": "",
    "priority": "High",
    "notes": "403 Forbidden — 접근 불가. e-tender.mn 사용 권장",
    "isMiru": false,
    "vendors": [
      "Dominion"
    ],
    "feasibility": "Low",
    "site_type": "접근차단",
    "crawl_method": "우회(VPN/Playwright)",
    "api_endpoint": "대안: http://www.e-tender.mn/en/tenders/ (HTTP 허용)"
  },
  {
    "id": 27,
    "country": "Mongolia",
    "country_ko": "몽골",
    "iso3": "MNG",
    "region": "Asia-Pacific",
    "name": "GPA e-Tender",
    "url": "https://www.e-tender.mn/",
    "portal_type": "국가조달(부)",
    "lang": "mn/en",
    "crawl_id": "",
    "priority": "Med",
    "notes": "Government Procurement Agency",
    "isMiru": false,
    "vendors": [
      "Dominion"
    ],
    "feasibility": "Low",
    "site_type": "접근차단",
    "crawl_method": "우회(VPN/Playwright)",
    "api_endpoint": "대안: http://www.e-tender.mn/en/tenders/ (HTTP 허용)"
  },
  {
    "id": 28,
    "country": "Mongolia",
    "country_ko": "몽골",
    "iso3": "MNG",
    "region": "Asia-Pacific",
    "name": "GEC Mongolia",
    "url": "https://m-election.mn/en",
    "portal_type": "선거위",
    "lang": "mn/en",
    "crawl_id": "",
    "priority": "High",
    "notes": "선거위원회 정보 사이트. 조달 없음. e-tender.mn 사용",
    "isMiru": false,
    "vendors": [
      "Dominion"
    ],
    "feasibility": "N/A",
    "site_type": "정적HTML",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 29,
    "country": "Philippines",
    "country_ko": "필리핀",
    "iso3": "PHL",
    "region": "Asia-Pacific",
    "name": "PhilGEPS",
    "url": "https://notices.philgeps.gov.ph/",
    "portal_type": "국가조달",
    "lang": "en",
    "crawl_id": "CRAWL-053",
    "priority": "High",
    "notes": "Miru ACM 110,620대 ₱17.9B. 필리핀 전자조달 허브",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "Med",
    "site_type": "ASP.NET WebForms",
    "crawl_method": "Playwright",
    "api_endpoint": "없음(직접 파싱)"
  },
  {
    "id": 30,
    "country": "Philippines",
    "country_ko": "필리핀",
    "iso3": "PHL",
    "region": "Asia-Pacific",
    "name": "COMELEC Procurement",
    "url": "https://www.comelec.gov.ph/?r=Procurement",
    "portal_type": "EMB조달",
    "lang": "en",
    "crawl_id": "CRAWL-054",
    "priority": "High",
    "notes": "COMELEC 직접 입찰공고. Miru 계약 공개",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "Med",
    "site_type": "JS-SPA (?r= 라우팅)",
    "crawl_method": "Playwright",
    "api_endpoint": "백엔드 REST API 존재 가능(XHR 탐색 필요)"
  },
  {
    "id": 31,
    "country": "Philippines",
    "country_ko": "필리핀",
    "iso3": "PHL",
    "region": "Asia-Pacific",
    "name": "COMELEC Latest Updates",
    "url": "https://www.comelec.gov.ph/index.html?r=Procurement/LatestUpdates",
    "portal_type": "EMB조달",
    "lang": "en",
    "crawl_id": "CRAWL-172",
    "priority": "High",
    "notes": "최신 조달공고 직접 링크",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "Med",
    "site_type": "ASP.NET WebForms",
    "crawl_method": "Playwright",
    "api_endpoint": "없음(직접 파싱)"
  },
  {
    "id": 32,
    "country": "South Korea",
    "country_ko": "대한민국",
    "iso3": "KOR",
    "region": "Asia-Pacific",
    "name": "나라장터 (G2B)",
    "url": "https://www.g2b.go.kr/",
    "portal_type": "국가조달",
    "lang": "ko",
    "crawl_id": "CRAWL-153",
    "priority": "High",
    "notes": "SSO 로그인 필요 (OIDC). 공개 URL 없음. PPS OpenAPI 대안 검토 필요",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "Med",
    "site_type": "JS-SPA + OIDC 인증",
    "crawl_method": "공공데이터포털 API",
    "api_endpoint": "https://apis.data.go.kr/1230000/BidPublicInfoService04/getBidPblancListInfoServcPPSSrch01"
  },
  {
    "id": 33,
    "country": "South Korea",
    "country_ko": "대한민국",
    "iso3": "KOR",
    "region": "Asia-Pacific",
    "name": "EVA G2B",
    "url": "https://eva.g2b.go.kr/",
    "portal_type": "국가조달(구)",
    "lang": "ko",
    "crawl_id": "CRAWL-070",
    "priority": "High",
    "notes": "G2B 선거 전용 서브도메인",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "N/A",
    "site_type": "JS-SPA",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 34,
    "country": "South Korea",
    "country_ko": "대한민국",
    "iso3": "KOR",
    "region": "Asia-Pacific",
    "name": "중앙선거관리위원회",
    "url": "https://www.nec.go.kr/site/eng/main.do",
    "portal_type": "선거위",
    "lang": "ko/en",
    "crawl_id": "CRAWL-071",
    "priority": "High",
    "notes": "NEC는 자체 입찰 없음. 모든 조달은 G2B 통해 공고",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "N/A",
    "site_type": "정적HTML+JS",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 35,
    "country": "Bulgaria",
    "country_ko": "불가리아",
    "iso3": "BGR",
    "region": "Europe",
    "name": "eOP (app.eop.bg)",
    "url": "https://app.eop.bg/today",
    "portal_type": "국가조달",
    "lang": "bg",
    "crawl_id": "CRAWL-161",
    "priority": "High",
    "notes": "React/Angular SPA — 정적 파서 불가. Playwright 필요. Negometrix 기반",
    "isMiru": false,
    "vendors": [
      "Smartmatic",
      "Ciela Norma"
    ],
    "feasibility": "Low",
    "site_type": "접근차단",
    "crawl_method": "TED EU API 대체",
    "api_endpoint": "TED API (이미 구현)"
  },
  {
    "id": 36,
    "country": "Bulgaria",
    "country_ko": "불가리아",
    "iso3": "BGR",
    "region": "Europe",
    "name": "CIK Bulgaria",
    "url": "https://www.cik.bg/bg/zop",
    "portal_type": "선거위",
    "lang": "bg",
    "crawl_id": "CRAWL-160",
    "priority": "High",
    "notes": "403 반환. CIK 입찰은 app.eop.bg에서 ЦИК 기관명으로 검색",
    "isMiru": false,
    "vendors": [
      "Smartmatic",
      "Ciela Norma"
    ],
    "feasibility": "Med",
    "site_type": "SSL 인증서 문제",
    "crawl_method": "requests (verify=False)",
    "api_endpoint": "없음"
  },
  {
    "id": 37,
    "country": "Georgia",
    "country_ko": "조지아",
    "iso3": "GEO",
    "region": "Europe",
    "name": "SPA Procurement Georgia",
    "url": "https://tenders.procurement.gov.ge",
    "portal_type": "국가조달",
    "lang": "en/ka",
    "crawl_id": "CRAWL-166",
    "priority": "High",
    "notes": "Hash URL (#/en/...) 정적 파싱 불가. 기본 URL 사용. 2026-06-01 신규 중앙조달청 ctd.cpb.gov.ge도 확인",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "Low",
    "site_type": "JS-SPA + SSL 만료",
    "crawl_method": "접근불가(SSL)",
    "api_endpoint": "대안: https://opendata.spa.ge (오픈데이터)"
  },
  {
    "id": 38,
    "country": "Georgia",
    "country_ko": "조지아",
    "iso3": "GEO",
    "region": "Europe",
    "name": "CEC Georgia",
    "url": "https://cesko.ge/",
    "portal_type": "선거위",
    "lang": "ka",
    "crawl_id": "CRAWL-077",
    "priority": "High",
    "notes": "403 반환. CEC 조달은 tenders.procurement.gov.ge에서 선거관리청 명칭으로 검색",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "Low",
    "site_type": "JS-SPA + SSL 만료",
    "crawl_method": "접근불가(SSL)",
    "api_endpoint": "대안: https://opendata.spa.ge (오픈데이터)"
  },
  {
    "id": 39,
    "country": "Bahrain",
    "country_ko": "바레인",
    "iso3": "BHR",
    "region": "Middle East",
    "name": "Tender Board Bahrain",
    "url": "https://etendering.tenderboard.gov.bh",
    "portal_type": "국가조달",
    "lang": "ar/en",
    "crawl_id": "",
    "priority": "High",
    "notes": "OMR 스캐너 개표. 야당 배제 형식적 선거",
    "isMiru": false,
    "vendors": [],
    "feasibility": "High",
    "site_type": "정적HTML+JS 탭",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음(직접 파싱)"
  },
  {
    "id": 40,
    "country": "Bahrain",
    "country_ko": "바레인",
    "iso3": "BHR",
    "region": "Middle East",
    "name": "Tender Board Homepage",
    "url": "https://www.tenderboard.gov.bh",
    "portal_type": "국가조달(홈)",
    "lang": "ar/en",
    "crawl_id": "",
    "priority": "Med",
    "notes": "국가조달위원회 홈페이지",
    "isMiru": false,
    "vendors": [],
    "feasibility": "High",
    "site_type": "정적HTML+JS 탭",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음(직접 파싱)"
  },
  {
    "id": 41,
    "country": "Iraq",
    "country_ko": "이라크",
    "iso3": "IRQ",
    "region": "Middle East",
    "name": "IHEC Iraq",
    "url": "https://ihec.iq/en/",
    "portal_type": "선거위",
    "lang": "ar/en",
    "crawl_id": "",
    "priority": "High",
    "notes": "PDF 아카이브만 존재. 실시간 입찰 DB 없음. PDF 업로드 주기 모니터링 필요",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "Low",
    "site_type": "정적HTML (CMS)",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음"
  },
  {
    "id": 42,
    "country": "Iraq",
    "country_ko": "이라크",
    "iso3": "IRQ",
    "region": "Middle East",
    "name": "MoP Iraq (계획부)",
    "url": "https://mop.gov.iq/en/general-government-contracts-department",
    "portal_type": "국가조달",
    "lang": "ar/en",
    "crawl_id": "",
    "priority": "Med",
    "notes": "규제/감독 기관. 입찰 발주기관 아님. IHEC가 직접 조달",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "N/A",
    "site_type": "정적HTML",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 43,
    "country": "Kyrgyzstan",
    "country_ko": "키르기스스탄",
    "iso3": "KGZ",
    "region": "Central Asia",
    "name": "zakupki.gov.kg",
    "url": "http://zakupki.gov.kg/popp/view/order/list.xhtml",
    "portal_type": "국가조달",
    "lang": "ru/ky",
    "crawl_id": "",
    "priority": "High",
    "notes": "공개 검색 가능. OCDS API: http://ocds.zakupki.gov.kg/dashboard/weekly",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "High",
    "site_type": "JSF 정적HTML",
    "crawl_method": "requests(정적) + JSF ViewState",
    "api_endpoint": "OCDS 대시보드: https://ocds.zakupki.gov.kg"
  },
  {
    "id": 44,
    "country": "Kyrgyzstan",
    "country_ko": "키르기스스탄",
    "iso3": "KGZ",
    "region": "Central Asia",
    "name": "CEC Kyrgyzstan",
    "url": "https://www.shailoo.gov.kg",
    "portal_type": "선거위",
    "lang": "ky/ru",
    "crawl_id": "",
    "priority": "High",
    "notes": "선거 정보 사이트. 조달은 zakupki.gov.kg에서 ЦИК로 검색",
    "isMiru": true,
    "vendors": [
      "Miru"
    ],
    "feasibility": "High",
    "site_type": "JSF 정적HTML",
    "crawl_method": "requests(정적) + JSF ViewState",
    "api_endpoint": "OCDS 대시보드: https://ocds.zakupki.gov.kg"
  },
  {
    "id": 45,
    "country": "Kazakhstan",
    "country_ko": "카자흐스탄",
    "iso3": "KAZ",
    "region": "Central Asia",
    "name": "goszakup.gov.kz",
    "url": "https://www.goszakup.gov.kz/",
    "portal_type": "국가조달",
    "lang": "ru/kz",
    "crawl_id": "CRAWL-065",
    "priority": "High",
    "notes": "국가조달시스템. CEC 입찰도 여기 게시",
    "isMiru": false,
    "vendors": [],
    "feasibility": "High",
    "site_type": "REST API (v2/v3)",
    "crawl_method": "API 직접 호출",
    "api_endpoint": "https://ows.goszakup.gov.kz/v3/trd-buy?filter[name]=election&limit=50"
  },
  {
    "id": 46,
    "country": "Kazakhstan",
    "country_ko": "카자흐스탄",
    "iso3": "KAZ",
    "region": "Central Asia",
    "name": "CEC Kazakhstan",
    "url": "https://election.gov.kz/eng/",
    "portal_type": "선거위",
    "lang": "kz/ru/en",
    "crawl_id": "CRAWL-066",
    "priority": "High",
    "notes": "중앙선거위원회",
    "isMiru": false,
    "vendors": [],
    "feasibility": "N/A",
    "site_type": "정적HTML",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 47,
    "country": "Uzbekistan",
    "country_ko": "우즈베키스탄",
    "iso3": "UZB",
    "region": "Central Asia",
    "name": "xarid.uzex.uz",
    "url": "https://xarid.uzex.uz/",
    "portal_type": "국가조달",
    "lang": "uz/ru",
    "crawl_id": "CRAWL-062",
    "priority": "High",
    "notes": "JS 렌더링. 뷰: 공개. 입찰참여: 등록+EDS 필요. etender.uzex.uz도 확인",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "JS-SPA (React 추정)",
    "crawl_method": "Playwright",
    "api_endpoint": "XHR 탐색 필요"
  },
  {
    "id": 48,
    "country": "Uzbekistan",
    "country_ko": "우즈베키스탄",
    "iso3": "UZB",
    "region": "Central Asia",
    "name": "CEC Uzbekistan",
    "url": "https://saylov.uz/en",
    "portal_type": "선거위",
    "lang": "uz/ru/en",
    "crawl_id": "CRAWL-063",
    "priority": "High",
    "notes": "정보 사이트. 조달은 xarid.uzex.uz에서 CEC로 검색",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "JS-SPA (React 추정)",
    "crawl_method": "Playwright",
    "api_endpoint": "XHR 탐색 필요"
  },
  {
    "id": 49,
    "country": "Kenya",
    "country_ko": "케냐",
    "iso3": "KEN",
    "region": "Africa",
    "name": "Tenders.go.ke",
    "url": "https://tenders.go.ke/tenders",
    "portal_type": "국가조달",
    "lang": "en",
    "crawl_id": "CRAWL-022",
    "priority": "High",
    "notes": "Smartmatic KIEMS BVD+결과전송. PPRA 관할",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "Med",
    "site_type": "JS-SPA",
    "crawl_method": "Playwright",
    "api_endpoint": "XHR 탐색 필요 (REST API 가능성)"
  },
  {
    "id": 50,
    "country": "Kenya",
    "country_ko": "케냐",
    "iso3": "KEN",
    "region": "Africa",
    "name": "IEBC Kenya",
    "url": "https://www.iebc.or.ke/",
    "portal_type": "선거위",
    "lang": "en",
    "crawl_id": "CRAWL-023",
    "priority": "High",
    "notes": "독립선거경계위원회. 자체 입찰공고 게시",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "Med",
    "site_type": "SSL 인증서 오류",
    "crawl_method": "requests (verify=False)",
    "api_endpoint": "없음"
  },
  {
    "id": 51,
    "country": "Argentina",
    "country_ko": "아르헨티나",
    "iso3": "ARG",
    "region": "Americas",
    "name": "COMPR.AR",
    "url": "https://comprar.gob.ar",
    "portal_type": "국가조달",
    "lang": "es",
    "crawl_id": "",
    "priority": "High",
    "notes": "연방 전기관 의무. DINE 발주 공고",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "JS-SPA (GridView)",
    "crawl_method": "Playwright",
    "api_endpoint": "대안: https://datosabiertos.compraspublicas.gob.ar/PLIEG/"
  },
  {
    "id": 52,
    "country": "Argentina",
    "country_ko": "아르헨티나",
    "iso3": "ARG",
    "region": "Americas",
    "name": "Cámara Nacional Electoral",
    "url": "https://www.electoral.gob.ar",
    "portal_type": "선거위",
    "lang": "es",
    "crawl_id": "",
    "priority": "High",
    "notes": "사법기관. 자체 조달 없음. 내무부 Dirección Electoral이 조달. COMPR.AR 사용",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "JS-SPA (GridView)",
    "crawl_method": "Playwright",
    "api_endpoint": "대안: https://datosabiertos.compraspublicas.gob.ar/PLIEG/"
  },
  {
    "id": 53,
    "country": "El Salvador",
    "country_ko": "엘살바도르",
    "iso3": "SLV",
    "region": "Americas",
    "name": "COMPRASAL",
    "url": "https://www.comprasal.gob.sv/",
    "portal_type": "국가조달",
    "lang": "es",
    "crawl_id": "",
    "priority": "High",
    "notes": "재무부 국가조달. TSE 입찰 여기 게시",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "JSF 정적HTML",
    "crawl_method": "Playwright (JSF ViewState)",
    "api_endpoint": "없음"
  },
  {
    "id": 54,
    "country": "El Salvador",
    "country_ko": "엘살바도르",
    "iso3": "SLV",
    "region": "Americas",
    "name": "TSE El Salvador",
    "url": "https://tse.gob.sv/",
    "portal_type": "선거위",
    "lang": "es",
    "crawl_id": "",
    "priority": "High",
    "notes": "최고선거재판소. 생체DUI+결과전송",
    "isMiru": false,
    "vendors": [],
    "feasibility": "N/A",
    "site_type": "접근차단",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 55,
    "country": "Honduras",
    "country_ko": "온두라스",
    "iso3": "HND",
    "region": "Americas",
    "name": "Honducompras",
    "url": "https://honducompras.gob.hn/",
    "portal_type": "국가조달",
    "lang": "es",
    "crawl_id": "CRAWL-148",
    "priority": "High",
    "notes": "Smartmatic VIU 2만대. 2025 시스템다운 사고",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "Low",
    "site_type": "접근차단",
    "crawl_method": "Playwright + 헤더 조작",
    "api_endpoint": "없음"
  },
  {
    "id": 56,
    "country": "Jamaica",
    "country_ko": "자메이카",
    "iso3": "JAM",
    "region": "Americas",
    "name": "GOJEP",
    "url": "https://www.gojep.gov.jm/",
    "portal_type": "국가조달",
    "lang": "en",
    "crawl_id": "",
    "priority": "High",
    "notes": "Jamaica e-Procurement. EOJ id=1936",
    "isMiru": false,
    "vendors": [
      "Thales"
    ],
    "feasibility": "High",
    "site_type": "정적HTML (JSF)",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음"
  },
  {
    "id": 57,
    "country": "Jamaica",
    "country_ko": "자메이카",
    "iso3": "JAM",
    "region": "Americas",
    "name": "EOJ on GOJEP",
    "url": "https://www.gojep.gov.jm/epps/prepareViewCAOrganisation.do?id=1936",
    "portal_type": "EMB조달",
    "lang": "en",
    "crawl_id": "",
    "priority": "High",
    "notes": "GOJEP 내 Electoral Office of Jamaica 기관 페이지",
    "isMiru": false,
    "vendors": [
      "Thales"
    ],
    "feasibility": "High",
    "site_type": "정적HTML (JSF)",
    "crawl_method": "requests(정적)",
    "api_endpoint": "없음"
  },
  {
    "id": 58,
    "country": "Jamaica",
    "country_ko": "자메이카",
    "iso3": "JAM",
    "region": "Americas",
    "name": "EOJ Official",
    "url": "https://www.eoj.com.jm/",
    "portal_type": "선거위",
    "lang": "en",
    "crawl_id": "",
    "priority": "High",
    "notes": "Electoral Office of Jamaica",
    "isMiru": false,
    "vendors": [
      "Thales"
    ],
    "feasibility": "N/A",
    "site_type": "접근불가",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 59,
    "country": "Panama",
    "country_ko": "파나마",
    "iso3": "PAN",
    "region": "Americas",
    "name": "PanamaCompra",
    "url": "https://www.panamacompra.gob.pa/Inicio/",
    "portal_type": "국가조달",
    "lang": "es",
    "crawl_id": "CRAWL-147",
    "priority": "High",
    "notes": "전기관 의무. TE 조달도 여기",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "AngularJS SPA",
    "crawl_method": "Playwright",
    "api_endpoint": "XHR 탐색 후 REST API 직접 호출 가능성"
  },
  {
    "id": 60,
    "country": "United States",
    "country_ko": "미국",
    "iso3": "USA",
    "region": "Americas",
    "name": "SAM.gov",
    "url": "https://sam.gov/opportunities",
    "portal_type": "국가조달",
    "lang": "en",
    "crawl_id": "CRAWL-106",
    "priority": "High",
    "notes": "연방 포털. 주(州) 입찰은 별도: CA=caleprocure.ca.gov, TX=txsmartbuy.gov, FL=vendor.myfloridamarketplace.com",
    "isMiru": false,
    "vendors": [
      "Dominion",
      "ES&S",
      "Hart"
    ],
    "feasibility": "High",
    "site_type": "REST API (공개)",
    "crawl_method": "API 직접 호출 (이미 구현)",
    "api_endpoint": "https://api.sam.gov/opportunities/v2/search?title=election+equipment&limit=25&offset=0&postedFrom=&postedTo="
  },
  {
    "id": 61,
    "country": "United States",
    "country_ko": "미국",
    "iso3": "USA",
    "region": "Americas",
    "name": "EAC (Election Assistance Commission)",
    "url": "https://www.eac.gov/",
    "portal_type": "선거위",
    "lang": "en",
    "crawl_id": "CRAWL-107",
    "priority": "Med",
    "notes": "인증/표준 기관. 조달 없음. EAC 자체 계약은 SAM.gov에 게재",
    "isMiru": false,
    "vendors": [
      "Dominion",
      "ES&S",
      "Hart"
    ],
    "feasibility": "High",
    "site_type": "REST API (공개)",
    "crawl_method": "API 직접 호출 (이미 구현)",
    "api_endpoint": "https://api.sam.gov/opportunities/v2/search?title=election+equipment&limit=25&offset=0&postedFrom=&postedTo="
  },
  {
    "id": 62,
    "country": "Bosnia and Herzegovina",
    "country_ko": "보스니아",
    "iso3": "BIH",
    "region": "Europe",
    "name": "eJN Bosnia",
    "url": "https://next.ejn.gov.ba/Announcement/Search",
    "portal_type": "국가조달",
    "lang": "bs/sr/hr",
    "crawl_id": "CRAWL-164",
    "priority": "High",
    "notes": "ejn.gov.ba → next.ejn.gov.ba로 이전 중. 신규 URL 사용",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "Med",
    "site_type": "정적HTML + POST API",
    "crawl_method": "API 직접 호출 (POST)",
    "api_endpoint": "POST https://www.ejn.gov.ba/api/Announcement/Search {page:1,pageSize:20,sortBy:1}"
  },
  {
    "id": 63,
    "country": "Bosnia and Herzegovina",
    "country_ko": "보스니아",
    "iso3": "BIH",
    "region": "Europe",
    "name": "CIK BiH",
    "url": "https://www.izbori.ba/Default.aspx?Lang=8",
    "portal_type": "선거위",
    "lang": "bs/en",
    "crawl_id": "CRAWL-165",
    "priority": "High",
    "notes": "izbori.ba는 선거결과 사이트. CIK 조달은 eJN에서 'Centralna izborna komisija' 검색",
    "isMiru": false,
    "vendors": [
      "Smartmatic"
    ],
    "feasibility": "Med",
    "site_type": "정적HTML + POST API",
    "crawl_method": "API 직접 호출 (POST)",
    "api_endpoint": "POST https://www.ejn.gov.ba/api/Announcement/Search {page:1,pageSize:20,sortBy:1}"
  },
  {
    "id": 64,
    "country": "Estonia",
    "country_ko": "에스토니아",
    "iso3": "EST",
    "region": "Europe",
    "name": "Riigihangete Register",
    "url": "https://riigihanked.riik.ee",
    "portal_type": "국가조달",
    "lang": "et",
    "crawl_id": "",
    "priority": "High",
    "notes": "i-Voting 51.1%. RIK 조달도 여기",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "Open Data API 존재 가능",
    "crawl_method": "API 직접 호출",
    "api_endpoint": "대안: https://riigihanked.riik.ee/rhr/api/public/v3/procurements?searchText=valimine"
  },
  {
    "id": 65,
    "country": "Estonia",
    "country_ko": "에스토니아",
    "iso3": "EST",
    "region": "Europe",
    "name": "State Electoral Office",
    "url": "https://www.valimised.ee/en",
    "portal_type": "선거위",
    "lang": "et/en",
    "crawl_id": "",
    "priority": "High",
    "notes": "선거 정보 사이트. 조달은 Riigihangete Register에서 Riigi Valimisteenistus 검색",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "Open Data API 존재 가능",
    "crawl_method": "API 직접 호출",
    "api_endpoint": "대안: https://riigihanked.riik.ee/rhr/api/public/v3/procurements?searchText=valimine"
  },
  {
    "id": 66,
    "country": "North Macedonia",
    "country_ko": "북마케도니아",
    "iso3": "MKD",
    "region": "Europe",
    "name": "e-nabavki.gov.mk",
    "url": "https://www.e-nabavki.gov.mk/",
    "portal_type": "국가조달",
    "lang": "mk",
    "crawl_id": "CRAWL-143",
    "priority": "High",
    "notes": "전자조달 포털. SEC 조달 게시",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Low",
    "site_type": "접근차단",
    "crawl_method": "Playwright + 헤더",
    "api_endpoint": "없음"
  },
  {
    "id": 67,
    "country": "North Macedonia",
    "country_ko": "북마케도니아",
    "iso3": "MKD",
    "region": "Europe",
    "name": "SEC Macedonia",
    "url": "https://www.sec.mk/",
    "portal_type": "선거위",
    "lang": "mk/en",
    "crawl_id": "",
    "priority": "High",
    "notes": "State Electoral Commission",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Low",
    "site_type": "접근차단",
    "crawl_method": "Playwright + 헤더",
    "api_endpoint": "없음"
  },
  {
    "id": 68,
    "country": "Switzerland",
    "country_ko": "스위스",
    "iso3": "CHE",
    "region": "Europe",
    "name": "SIMAP Switzerland",
    "url": "https://www.simap.ch/en",
    "portal_type": "국가조달",
    "lang": "de/fr/it/en",
    "crawl_id": "",
    "priority": "High",
    "notes": "2024-07 이후 입찰만 포함. /en/publications 경로 폐기됨. 홈페이지 검색 사용",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Med",
    "site_type": "정적HTML+검색폼",
    "crawl_method": "Playwright (검색폼)",
    "api_endpoint": "없음(폼 기반)"
  },
  {
    "id": 69,
    "country": "Switzerland",
    "country_ko": "스위스",
    "iso3": "CHE",
    "region": "Europe",
    "name": "Bundeskanzlei e-Voting",
    "url": "https://www.bk.admin.ch/bk/en/home/politische-rechte/e-voting.html",
    "portal_type": "선거위(e-voting)",
    "lang": "de/fr/it/en",
    "crawl_id": "",
    "priority": "Med",
    "notes": "정보 페이지. 입찰 없음. SIMAP 사용",
    "isMiru": false,
    "vendors": [],
    "feasibility": "N/A",
    "site_type": "정적HTML",
    "crawl_method": "—",
    "api_endpoint": "없음"
  },
  {
    "id": 70,
    "country": "Iran",
    "country_ko": "이란",
    "iso3": "IRN",
    "region": "Middle East",
    "name": "SETAD Iran",
    "url": "https://setadiran.ir/setad/cms",
    "portal_type": "국가조달",
    "lang": "fa",
    "crawl_id": "",
    "priority": "Low",
    "notes": "이란 외부에서 geo-차단. Farsi 전용. irantenders.com 대리 모니터링 고려",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Low",
    "site_type": "접근불가",
    "crawl_method": "불가",
    "api_endpoint": "없음"
  },
  {
    "id": 71,
    "country": "Iran",
    "country_ko": "이란",
    "iso3": "IRN",
    "region": "Middle East",
    "name": "MoI Iran (내무부)",
    "url": "https://keshvar.moi.ir/",
    "portal_type": "선거주관",
    "lang": "fa",
    "crawl_id": "",
    "priority": "Low",
    "notes": "403 반환. 이란 외부 접근 불가",
    "isMiru": false,
    "vendors": [],
    "feasibility": "Low",
    "site_type": "접근차단",
    "crawl_method": "불가",
    "api_endpoint": "없음"
  }
];

window.MIRU_COUNTRIES = [
  {
    "country": "Albania",
    "country_ko": "알바니아",
    "iso3": "ALB",
    "iso_num": "008",
    "region": "Europe",
    "method": "EVM",
    "vendors": [
      "Smartmatic"
    ],
    "isMiru": false,
    "count": 2,
    "portals": [
      13,
      14
    ]
  },
  {
    "country": "UAE",
    "country_ko": "아랍에미리트",
    "iso3": "ARE",
    "iso_num": "784",
    "region": "Middle East",
    "method": "EVM",
    "vendors": [
      "Scytl"
    ],
    "isMiru": false,
    "count": 2,
    "portals": [
      18,
      19
    ]
  },
  {
    "country": "Argentina",
    "country_ko": "아르헨티나",
    "iso3": "ARG",
    "iso_num": "032",
    "region": "Americas",
    "method": "DRE",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      51,
      52
    ]
  },
  {
    "country": "Belgium",
    "country_ko": "벨기에",
    "iso3": "BEL",
    "iso_num": "056",
    "region": "Europe",
    "method": "EVM",
    "vendors": [
      "Smartmatic"
    ],
    "isMiru": false,
    "count": 2,
    "portals": [
      15,
      16
    ]
  },
  {
    "country": "Bulgaria",
    "country_ko": "불가리아",
    "iso3": "BGR",
    "iso_num": "100",
    "region": "Europe",
    "method": "DRE",
    "vendors": [
      "Smartmatic",
      "Ciela Norma"
    ],
    "isMiru": false,
    "count": 2,
    "portals": [
      35,
      36
    ]
  },
  {
    "country": "Bahrain",
    "country_ko": "바레인",
    "iso3": "BHR",
    "iso_num": "048",
    "region": "Middle East",
    "method": "OMR",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      39,
      40
    ]
  },
  {
    "country": "Bosnia and Herzegovina",
    "country_ko": "보스니아",
    "iso3": "BIH",
    "iso_num": "070",
    "region": "Europe",
    "method": "OMR",
    "vendors": [
      "Smartmatic"
    ],
    "isMiru": false,
    "count": 2,
    "portals": [
      62,
      63
    ]
  },
  {
    "country": "Brazil",
    "country_ko": "브라질",
    "iso3": "BRA",
    "iso_num": "076",
    "region": "Americas",
    "method": "DRE",
    "vendors": [],
    "isMiru": false,
    "count": 3,
    "portals": [
      1,
      2,
      3
    ]
  },
  {
    "country": "Bhutan",
    "country_ko": "부탄",
    "iso3": "BTN",
    "iso_num": "064",
    "region": "Asia-Pacific",
    "method": "EVM",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      8,
      9
    ]
  },
  {
    "country": "Switzerland",
    "country_ko": "스위스",
    "iso3": "CHE",
    "iso_num": "756",
    "region": "Europe",
    "method": "EVM",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      68,
      69
    ]
  },
  {
    "country": "DRC",
    "country_ko": "콩고(DRC)",
    "iso3": "COD",
    "iso_num": "180",
    "region": "Africa",
    "method": "DRE",
    "vendors": [
      "Miru"
    ],
    "isMiru": true,
    "count": 1,
    "portals": [
      7
    ]
  },
  {
    "country": "Dominican Republic",
    "country_ko": "도미니카공화국",
    "iso3": "DOM",
    "iso_num": "214",
    "region": "Americas",
    "method": "OMR",
    "vendors": [
      "Indra"
    ],
    "isMiru": false,
    "count": 2,
    "portals": [
      24,
      25
    ]
  },
  {
    "country": "Estonia",
    "country_ko": "에스토니아",
    "iso3": "EST",
    "iso_num": "233",
    "region": "Europe",
    "method": "EVM",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      64,
      65
    ]
  },
  {
    "country": "Georgia",
    "country_ko": "조지아",
    "iso3": "GEO",
    "iso_num": "268",
    "region": "Europe",
    "method": "OMR",
    "vendors": [
      "Smartmatic"
    ],
    "isMiru": false,
    "count": 2,
    "portals": [
      37,
      38
    ]
  },
  {
    "country": "Ghana",
    "country_ko": "가나",
    "iso3": "GHA",
    "iso_num": "288",
    "region": "Africa",
    "method": "OMR",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      20,
      21
    ]
  },
  {
    "country": "Honduras",
    "country_ko": "온두라스",
    "iso3": "HND",
    "iso_num": "340",
    "region": "Americas",
    "method": "Mixed",
    "vendors": [
      "Smartmatic"
    ],
    "isMiru": false,
    "count": 1,
    "portals": [
      55
    ]
  },
  {
    "country": "India",
    "country_ko": "인도",
    "iso3": "IND",
    "iso_num": "356",
    "region": "Asia-Pacific",
    "method": "EVM",
    "vendors": [],
    "isMiru": false,
    "count": 3,
    "portals": [
      10,
      11,
      12
    ]
  },
  {
    "country": "Iran",
    "country_ko": "이란",
    "iso3": "IRN",
    "iso_num": "364",
    "region": "Middle East",
    "method": "DRE",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      70,
      71
    ]
  },
  {
    "country": "Iraq",
    "country_ko": "이라크",
    "iso3": "IRQ",
    "iso_num": "368",
    "region": "Middle East",
    "method": "OMR",
    "vendors": [
      "Miru"
    ],
    "isMiru": true,
    "count": 2,
    "portals": [
      41,
      42
    ]
  },
  {
    "country": "Jamaica",
    "country_ko": "자메이카",
    "iso3": "JAM",
    "iso_num": "388",
    "region": "Americas",
    "method": "Mixed",
    "vendors": [
      "Thales"
    ],
    "isMiru": false,
    "count": 3,
    "portals": [
      56,
      57,
      58
    ]
  },
  {
    "country": "Kazakhstan",
    "country_ko": "카자흐스탄",
    "iso3": "KAZ",
    "iso_num": "398",
    "region": "Central Asia",
    "method": "Mixed",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      45,
      46
    ]
  },
  {
    "country": "Kenya",
    "country_ko": "케냐",
    "iso3": "KEN",
    "iso_num": "404",
    "region": "Africa",
    "method": "Mixed",
    "vendors": [
      "Smartmatic"
    ],
    "isMiru": false,
    "count": 2,
    "portals": [
      49,
      50
    ]
  },
  {
    "country": "Kyrgyzstan",
    "country_ko": "키르기스스탄",
    "iso3": "KGZ",
    "iso_num": "417",
    "region": "Central Asia",
    "method": "OMR",
    "vendors": [
      "Miru"
    ],
    "isMiru": true,
    "count": 2,
    "portals": [
      43,
      44
    ]
  },
  {
    "country": "South Korea",
    "country_ko": "대한민국",
    "iso3": "KOR",
    "iso_num": "410",
    "region": "Asia-Pacific",
    "method": "OMR",
    "vendors": [
      "Miru"
    ],
    "isMiru": true,
    "count": 3,
    "portals": [
      32,
      33,
      34
    ]
  },
  {
    "country": "North Macedonia",
    "country_ko": "북마케도니아",
    "iso3": "MKD",
    "iso_num": "807",
    "region": "Europe",
    "method": "Mixed",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      66,
      67
    ]
  },
  {
    "country": "Mongolia",
    "country_ko": "몽골",
    "iso3": "MNG",
    "iso_num": "496",
    "region": "Asia-Pacific",
    "method": "OMR",
    "vendors": [
      "Dominion"
    ],
    "isMiru": false,
    "count": 3,
    "portals": [
      26,
      27,
      28
    ]
  },
  {
    "country": "Oman",
    "country_ko": "오만",
    "iso3": "OMN",
    "iso_num": "512",
    "region": "Middle East",
    "method": "EVM",
    "vendors": [],
    "isMiru": false,
    "count": 1,
    "portals": [
      17
    ]
  },
  {
    "country": "Panama",
    "country_ko": "파나마",
    "iso3": "PAN",
    "iso_num": "591",
    "region": "Americas",
    "method": "Mixed",
    "vendors": [],
    "isMiru": false,
    "count": 1,
    "portals": [
      59
    ]
  },
  {
    "country": "Philippines",
    "country_ko": "필리핀",
    "iso3": "PHL",
    "iso_num": "608",
    "region": "Asia-Pacific",
    "method": "OMR",
    "vendors": [
      "Miru"
    ],
    "isMiru": true,
    "count": 3,
    "portals": [
      29,
      30,
      31
    ]
  },
  {
    "country": "Paraguay",
    "country_ko": "파라과이",
    "iso3": "PRY",
    "iso_num": "600",
    "region": "Americas",
    "method": "DRE",
    "vendors": [],
    "isMiru": false,
    "count": 1,
    "portals": [
      4
    ]
  },
  {
    "country": "El Salvador",
    "country_ko": "엘살바도르",
    "iso3": "SLV",
    "iso_num": "222",
    "region": "Americas",
    "method": "Mixed",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      53,
      54
    ]
  },
  {
    "country": "United States",
    "country_ko": "미국",
    "iso3": "USA",
    "iso_num": "840",
    "region": "Americas",
    "method": "Mixed",
    "vendors": [
      "Dominion",
      "ES&S",
      "Hart"
    ],
    "isMiru": false,
    "count": 2,
    "portals": [
      60,
      61
    ]
  },
  {
    "country": "Uzbekistan",
    "country_ko": "우즈베키스탄",
    "iso3": "UZB",
    "iso_num": "860",
    "region": "Central Asia",
    "method": "EVM",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      47,
      48
    ]
  },
  {
    "country": "Venezuela",
    "country_ko": "베네수엘라",
    "iso3": "VEN",
    "iso_num": "862",
    "region": "Americas",
    "method": "DRE",
    "vendors": [],
    "isMiru": false,
    "count": 2,
    "portals": [
      5,
      6
    ]
  },
  {
    "country": "South Africa",
    "country_ko": "남아공",
    "iso3": "ZAF",
    "iso_num": "710",
    "region": "Africa",
    "method": "OMR",
    "vendors": [
      "Ren-Form"
    ],
    "isMiru": false,
    "count": 2,
    "portals": [
      22,
      23
    ]
  }
];

window.MIRU_ANALYSIS_STATS = {
  "total_portals": 71,
  "total_countries": 35,
  "miru_countries": 5,
  "high_priority": 57,
  "crawlable_high": 15,
  "priority": {
    "P1": 11,
    "P2": 24,
    "P3": 10,
    "Skip": 21
  },
  "by_region": {
    "Americas": 19,
    "Africa": 7,
    "Asia-Pacific": 14,
    "Europe": 16,
    "Middle East": 9,
    "Central Asia": 6
  }
};

window.MIRU_VENDOR_DATA = [
  {
    "slug": "smartmatic",
    "name": "Smartmatic",
    "flag": "🇬🇧",
    "hq": "London, UK",
    "homepage": "https://www.smartmatic.com",
    "type": "Private",
    "founded": "2000",
    "employees": "~600",
    "revenue": "~$175M",
    "countries_count": 24,
    "key_products": [
      "bSmart BMD 100/155",
      "SAES-1800plus VCM",
      "EMS/EMP Platform",
      "TIVI Internet Voting",
      "VIU-500 Biometric Kit"
    ],
    "categories": [
      "BMD",
      "DRE",
      "OMR",
      "Biometric",
      "Internet",
      "EMS"
    ],
    "overlap": "Indirect",
    "overlap_markets": [
      "PHL"
    ],
    "strengths": [
      "35+개국 65억 표 처리 — 세계 최대 선거기술 풋프린트",
      "BMD·OMR·생체인식·인터넷투표 엔드투엔드 포트폴리오",
      "VVSG 2.0 최초 제출 — EAC 인증 공신력"
    ],
    "weaknesses": [
      "SGO Corporation 형사기소(FCPA, 2025.10) — 필리핀 뇌물 혐의, 기각신청 계류중",
      "필리핀 시장 영구 상실 — COMELEC 2023 자격박탈 (Miru 2025 수주)",
      "미국 시장 Dominion 비경쟁 조항으로 사실상 LA카운티 단독만 가능"
    ],
    "news": "FCPA 기소(2025.10) 기각신청 계류 / Newsmax $40M 합의(2024) / Fox News 재판 2026년 예정",
    "confidence": "High"
  },
  {
    "slug": "liberty_vote",
    "name": "Liberty Vote (구 Dominion)",
    "flag": "🇺🇸",
    "hq": "Denver, CO, USA",
    "homepage": "https://libertyvote.com",
    "type": "Private",
    "founded": "2003",
    "employees": "~250",
    "revenue": "~$100M",
    "countries_count": 2,
    "key_products": [
      "ImageCast X BMD",
      "ImageCast Precinct 2 OMR",
      "Democracy Suite EMS",
      "Frontier 1.0 (VVSG 2.0 제출중)"
    ],
    "categories": [
      "OMR",
      "BMD",
      "DRE",
      "EMS"
    ],
    "overlap": "None",
    "overlap_markets": [],
    "strengths": [
      "미국 등록유권자 25% 커버 — 27개 주 최대 설치기반",
      "KNOWiNK 인수로 e-pollbook 포함 40개 주 통합 플랫폼",
      "Frontier 1.0 VVSG 2.0 EAC 제출(2025.11)"
    ],
    "weaknesses": [
      "2020 음모론 $787.5M 합의 이후 브랜드 독성 여전",
      "국제시장 사실상 전무 — 필리핀 2025 응찰조차 못 함",
      "리브랜딩 후 신규계약 아직 없음"
    ],
    "news": "2025.10 Dominion → Liberty Vote 리브랜딩 / 2025.11 Frontier 1.0 EAC VVSG 2.0 제출",
    "confidence": "High"
  },
  {
    "slug": "ess",
    "name": "ES&S (Election Systems & Software)",
    "flag": "🇺🇸",
    "hq": "Omaha, NE, USA",
    "homepage": "https://www.essvote.com",
    "type": "Private",
    "founded": "1979",
    "employees": "~700",
    "revenue": "~$120M",
    "countries_count": 6,
    "key_products": [
      "DS300/450/950 OMR 스캐너",
      "ExpressVote BMD",
      "ExpressVote XL",
      "EVS 7.0 (VVSG 2.0 인증 2026.3)"
    ],
    "categories": [
      "OMR",
      "BMD",
      "DRE",
      "e-Pollbook",
      "EMS"
    ],
    "overlap": "Indirect",
    "overlap_markets": [
      "PHL"
    ],
    "strengths": [
      "미국 시장 점유율 50~60% — 42개 주 4,500개 지자체",
      "투표등록·e-pollbook·OMR·BMD·개표 풀스택 번들",
      "EVS 7.0 VVSG 2.0 EAC 인증(2026.3) — 최신 표준 최초 인증"
    ],
    "weaknesses": [
      "보안 취약점 지속 — 원격접속 프리인스톨(2018), 중국산 부품 우려",
      "텍사스 e-pollbook 인증 취소(2024.12) — 댈러스 오인쇄 사고",
      "보안 연구자 소송 — 독립감사 저해"
    ],
    "news": "2024.12 텍사스 e-pollbook 인증취소 / 2026.3 VVSG 2.0 인증 승인",
    "confidence": "High"
  },
  {
    "slug": "hart",
    "name": "Hart InterCivic",
    "flag": "🇺🇸",
    "hq": "Austin, TX, USA",
    "homepage": "https://www.hartintercivic.com",
    "type": "Private",
    "founded": "1912",
    "employees": "~100~150",
    "revenue": "~$30~43M",
    "countries_count": 1,
    "key_products": [
      "Verity Vanguard 1.0 (VVSG 2.0 최초 인증)",
      "Vanguard Flex BMD",
      "Vanguard Vault OMR"
    ],
    "categories": [
      "OMR",
      "BMD",
      "DRE",
      "EMS"
    ],
    "overlap": "None",
    "overlap_markets": [],
    "strengths": [
      "세계 최초 VVSG 2.0 EAC 인증(2025.7) — 규제 선점",
      "바코드 없는 완전 사람이 읽을 수 있는 용지 — EO 14248 완전 준수",
      "20개 주 100년+ 관계"
    ],
    "weaknesses": [
      "미국 단일 시장 — 국제 진출 없음",
      "매출 $30~43M 소형사 — R&D 투자 한계",
      "미국 시장 점유율 15%"
    ],
    "news": "2025.7 Vanguard VVSG 2.0 최초 인증 / 2026.4 텍사스 6번째 주 인증",
    "confidence": "High"
  },
  {
    "slug": "msa",
    "name": "Grupo MSA / Comitia-MSA",
    "flag": "🇦🇷",
    "hq": "Buenos Aires, Argentina",
    "homepage": "https://www.msa.com.ar",
    "type": "Private",
    "founded": "1995",
    "employees": "~100+",
    "revenue": "~$5.8M",
    "countries_count": 3,
    "key_products": [
      "Vot.ar / BUE 전자투표용지",
      "Scytl InVote Gov 인터넷투표",
      "sVote (스위스 e-voting)"
    ],
    "categories": [
      "BMD",
      "Internet",
      "Software"
    ],
    "overlap": "Indirect",
    "overlap_markets": [
      "ARG",
      "PRY"
    ],
    "strengths": [
      "아르헨티나 BUE 시장 25년 지배 — CABA 등 11개 이상 주",
      "2024.6 Scytl 인수로 1,000+ 미국 고객, 4개 대륙 IP 확보",
      "RFID 칩+종이 혼합 BUE — ISO 9001 인증"
    ],
    "weaknesses": [
      "기술 장애 반복 — 2023 CABA PASO 판사 판정",
      "단독입찰 반복 패턴 — 파라과이 2025 불법시비 논란",
      "파라과이 $35M 단독낙찰 논란"
    ],
    "news": "2024.6 Scytl 인수 / 2025.5 CABA $22M 단독입찰 / 2025.12 파라과이 $35M 단독낙찰 논란",
    "confidence": "High"
  },
  {
    "slug": "scytl",
    "name": "Scytl / Civica Election Services",
    "flag": "🇪🇸",
    "hq": "Barcelona / London",
    "homepage": "https://www.scytl.com",
    "type": "Subsidiary",
    "founded": "2001",
    "employees": "~125+200",
    "revenue": "~$44M+$35M",
    "countries_count": 30,
    "key_products": [
      "Invote Gov 인터넷투표",
      "SOE Software ENR",
      "CESvotes 온라인투표(Civica)"
    ],
    "categories": [
      "Internet",
      "Software"
    ],
    "overlap": "Indirect",
    "overlap_markets": [
      "ARE",
      "PRY"
    ],
    "strengths": [
      "암호화 인터넷투표 50+ 특허, 25년 R&D 선점",
      "SOE Software — 미국 24개 주 1,300개 선거구 ENR",
      "UAE FNC 4연속(2006~) — 세계 최초 100% 디지털 국가선거"
    ],
    "weaknesses": [
      "노르웨이·호주 인터넷투표 취약점으로 계약 상실",
      "2020년 파산(채무 €75M) — 2번의 소유권 변경",
      "유럽·미국 인터넷투표 감사가능성 반대 여론"
    ],
    "news": "2024.6 COMITIA MSA에 인수 / 2025.12 파라과이 $35M 계약",
    "confidence": "Med"
  },
  {
    "slug": "positivo",
    "name": "Positivo Tecnologia",
    "flag": "🇧🇷",
    "hq": "Curitiba, Brazil",
    "homepage": "https://www.positivotecnologia.com.br/en/",
    "type": "Public",
    "founded": "1989",
    "employees": "~8,400",
    "revenue": "~$700M",
    "countries_count": 1,
    "key_products": [
      "UE2022 DRE 투표기",
      "UE2020 DRE",
      "생체인식 리더 HID DP5360"
    ],
    "categories": [
      "DRE",
      "EVM",
      "Biometric"
    ],
    "overlap": "None",
    "overlap_markets": [],
    "strengths": [
      "브라질 TSE 유일 DRE 제조사 — 2020 이후 독점",
      "국내 공장 수직통합 — 가격경쟁력 + 국가안보 조달 우선",
      "TSE 공동개발 파트너십"
    ],
    "weaknesses": [
      "브라질 단일 시장 — 국제 수출 없음",
      "순이익 R$85M(2024)→R$12M(2025) 급감",
      "DRE 외 제품(OMR·BMD·인터넷투표) 없음"
    ],
    "news": "FY2025 매출 R$4.0B / 순이익 R$12M(86% 감소) / UE2026 신규입찰 미발표",
    "confidence": "High"
  },
  {
    "slug": "bel_india",
    "name": "BEL (Bharat Electronics Limited)",
    "flag": "🇮🇳",
    "hq": "Bengaluru, India",
    "homepage": "https://bel-india.in",
    "type": "State-owned",
    "founded": "1954",
    "employees": "~9,000~11,200",
    "revenue": "~$3.3B",
    "countries_count": 7,
    "key_products": [
      "EVM M3 Control Unit",
      "EVM M3 Ballot Unit",
      "VVPAT M3"
    ],
    "categories": [
      "EVM",
      "DRE",
      "VVPAT"
    ],
    "overlap": "None",
    "overlap_markets": [],
    "strengths": [
      "인도 9억 유권자 선거 EVM 독점 공급",
      "국방부 산하 Navratna PSU — 진입장벽 극히 높음",
      "나미비아·부탄·피지 등 외교 채널 수출"
    ],
    "weaknesses": [
      "EVM 보안 투명성 비판 — 소프트웨어 감사보고서 공개 거부",
      "선거기술은 전체 매출 소수 — R&D·수출 인프라 취약",
      "국제 수출 전체 매출의 0.5% 미만"
    ],
    "news": "FY2026 매출 ~$3.3B 신기록 / 수출 33.65% 증가 $141.9M — 방산 위주",
    "confidence": "Med"
  },
  {
    "slug": "ecil",
    "name": "ECIL (Electronics Corporation of India)",
    "flag": "🇮🇳",
    "hq": "Hyderabad, India",
    "homepage": "https://www.ecil.co.in",
    "type": "State-owned",
    "founded": "1967",
    "employees": "~3,000~5,000",
    "revenue": "~$290M",
    "countries_count": 4,
    "key_products": [
      "M3-EVM",
      "VVPAT",
      "S3-EVM (2025년 공개)"
    ],
    "categories": [
      "EVM",
      "DRE",
      "Software"
    ],
    "overlap": "None",
    "overlap_markets": [],
    "strengths": [
      "BEL과 50:50 인도 ECI 공급 독점",
      "EMS 2.0 클라우드 네이티브 + SMF 2.0 보안제조 소프트웨어",
      "Miniratna Category-I 지위 부여(2025.5)"
    ],
    "weaknesses": [
      "해외수출 인도-G2G 외교 채널 의존",
      "EVM 기술 특수 목적 설계 — OMR/BMD 국제 입찰 미적용",
      "S3-EVM 공개(2025.3) 외 국제 시장 진출 계획 없음"
    ],
    "news": "2025.3 S3-EVM 공개 / 2025.5 Miniratna Category-I 승격",
    "confidence": "Med"
  },
  {
    "slug": "swiss_post",
    "name": "Swiss Post e-voting",
    "flag": "🇨🇭",
    "hq": "Bern, Switzerland",
    "homepage": "https://swisspost-digital.ch/en/solutions/e-voting",
    "type": "State-owned",
    "founded": "2014",
    "employees": "~45(e-voting팀)",
    "revenue": "그룹 ~$8.5B",
    "countries_count": 1,
    "key_products": [
      "sVote 인터넷투표 시스템",
      "Universal Verifiability 검증SW"
    ],
    "categories": [
      "Internet"
    ],
    "overlap": "None",
    "overlap_markets": [],
    "strengths": [
      "완전 오픈소스 공개 — 수학적 검증 가능 유일 국가급 시스템",
      "범용 검증가능성 최초 운용",
      "스위스 연방 소유 — 상업 압력 없음"
    ],
    "weaknesses": [
      "스위스 단일 시장 — 4/26개 캔톤만 활성화",
      "2019~2023 중단 이력(암호화 결함)",
      "인터넷투표 전용 — OMR·EVM·BMD·생체인식 없음"
    ],
    "news": "2025.6 연방 기본라이선스 4개 캔톤 2027까지 갱신",
    "confidence": "High"
  },
  {
    "slug": "cybernetica",
    "name": "Cybernetica AS",
    "flag": "🇪🇪",
    "hq": "Tallinn, Estonia",
    "homepage": "https://cyber.ee",
    "type": "Private",
    "founded": "1997",
    "employees": "~230",
    "revenue": "~$16M",
    "countries_count": 1,
    "key_products": [
      "IVXV 인터넷투표 시스템",
      "m-Voting 모바일(2025 파일럿)"
    ],
    "categories": [
      "Internet",
      "Software"
    ],
    "overlap": "None",
    "overlap_markets": [],
    "strengths": [
      "20년 유일한 법적 구속력 국가 인터넷투표 운영(2023년 51%)",
      "IVXV 오픈소스 투명성",
      "40개국 UXP/X-Road 생태계"
    ],
    "weaknesses": [
      "에스토니아 단일 국제 운용",
      "~230명 소형사",
      "2024 EP선거 첫 오류 발생"
    ],
    "news": "2025.5 m-Voting iOS/Android 파일럿 / 2025.11 양자내성암호 전환 3개 계약",
    "confidence": "High"
  },
  {
    "slug": "idemia",
    "name": "IDEMIA (→ IN Groupe / Amadeus)",
    "flag": "🇫🇷",
    "hq": "Courbevoie, France",
    "homepage": "https://www.idemia.com",
    "type": "Private",
    "founded": "2017",
    "employees": "~15,000",
    "revenue": "~$3.1B",
    "countries_count": 9,
    "key_products": [
      "MorphoTablet 2S 생체인식 태블릿",
      "KIEMS(케냐 통합선거관리)",
      "RAVEC(말리 시민ID)"
    ],
    "categories": [
      "Biometric",
      "Software",
      "BVR"
    ],
    "overlap": "Indirect",
    "overlap_markets": [
      "KEN",
      "GHA",
      "COD"
    ],
    "strengths": [
      "아프리카 35개국+ 생체선거기술 — 최대 아프리카 풋프린트",
      "NIST 지문 전 벤치마크 1위(2025.3)",
      "ID스크린 태블릿 17만대+ 배포"
    ],
    "weaknesses": [
      "케냐 IEBC 지식이전 거부 비판 / 2017 KIEMS 실패",
      "프랑스 검찰 뇌물수사 진행중(2022~)",
      "분사 진행 — 사업 불확실성"
    ],
    "news": "2025.7 Smart Identity 부문 IN Groupe에 ~€1B 매각 / 2026.4 IPS 부문 Amadeus €1.2B 발표",
    "confidence": "High"
  },
  {
    "slug": "thales",
    "name": "Thales Group (DIS / 구 Gemalto)",
    "flag": "🇫🇷",
    "hq": "La Défense, Paris, France",
    "homepage": "https://www.thalesgroup.com",
    "type": "Public",
    "founded": "1893",
    "employees": "~85,000",
    "revenue": "~$24B",
    "countries_count": 15,
    "key_products": [
      "Thales Election Suite",
      "Coesys Mobile Enrollment Station",
      "DactyScan84c 생체인식 스캐너"
    ],
    "categories": [
      "Biometric",
      "Software"
    ],
    "overlap": "Indirect",
    "overlap_markets": [
      "COD",
      "GHA",
      "PHL"
    ],
    "strengths": [
      "15개국+ 생체선거 배포 — 세계 최대 생체선거 벤더",
      "20년+ Gemalto 유산으로 프랑코폰 아프리카 깊은 관계",
      "€22B 그룹 규모 — 여권·국민ID→유권자등록 크로스셀"
    ],
    "weaknesses": [
      "Gemalto 자회사 프랑스 사법조사(2022~) — 카메룬·DRC 뇌물 혐의",
      "투표기계(OMR·EVM·BMD) 없음",
      "방산·항공·사이버 등 전방위 대기업 — 선거기술 집중도 낮음"
    ],
    "news": "FY2025 €22.1B 매출 신기록 / Gemalto 프랑스 사법조사 지속",
    "confidence": "High"
  },
  {
    "slug": "laxton",
    "name": "Laxton Group (→ DNP 자회사)",
    "flag": "🇳🇱",
    "hq": "The Hague, Netherlands",
    "homepage": "https://www.laxton.com",
    "type": "Subsidiary",
    "founded": "2004",
    "employees": "~201",
    "revenue": "~$35M",
    "countries_count": 14,
    "key_products": [
      "Chameleon D 다중생체인식 태블릿",
      "BRK 생체인식 등록 키트",
      "Athena 신원관리 플랫폼"
    ],
    "categories": [
      "Biometric",
      "Software"
    ],
    "overlap": "Indirect",
    "overlap_markets": [
      "GHA",
      "TZA"
    ],
    "strengths": [
      "20년+ 50개국 3억명+ 생체등록",
      "하드웨어+소프트웨어 자체 설계/제조",
      "DNP 인수($9.5B 부모사) + MOSIP SI 인증(2026.3)"
    ],
    "weaknesses": [
      "투표집계 기계(OMR·EVM·BMD) 없음",
      "라이베리아 계약 논란(2022~2023 2회 거부 후 낙찰)",
      "DNP 인수 전 $35M 소형사"
    ],
    "news": "2025.6 DNP 75% 지분 인수 / 2026.3 MOSIP SI 파트너 인증",
    "confidence": "High"
  },
  {
    "slug": "innovatrics",
    "name": "Innovatrics",
    "flag": "🇸🇰",
    "hq": "Bratislava, Slovakia",
    "homepage": "https://www.innovatrics.com",
    "type": "Private",
    "founded": "2004",
    "employees": "~210",
    "revenue": "~$18M",
    "countries_count": 7,
    "key_products": [
      "Innovatrics ABIS 자동생체식별",
      "Voter Management Platform",
      "SmartFace 안면인식"
    ],
    "categories": [
      "Biometric",
      "ABIS",
      "Software"
    ],
    "overlap": "Indirect",
    "overlap_markets": [
      "ALB"
    ],
    "strengths": [
      "NIST ELFT 잠재지문 정확도 1위(2025.1)",
      "하드웨어 무관 클라우드 ABIS — 1억 인구 단일 AWS",
      "MOSIP 컴플라이언트 ABIS(2026.6) — 29개국 GovStack"
    ],
    "weaknesses": [
      "소프트웨어/생체인식 전용 — Smartmatic 등에 납품 구조",
      "~210명 소형사",
      "투표기계 없음 — 고부가 하드웨어 계약 참여 불가"
    ],
    "news": "2025.1 NIST 지문 1위 탈환 / 2026.5 UIDAI 안면인식 챌린지 1위",
    "confidence": "Med"
  },
  {
    "slug": "tech5",
    "name": "uqudo / TECH5",
    "flag": "🇨🇭",
    "hq": "Geneva / Manchester",
    "homepage": "https://tech5.ai",
    "type": "Private",
    "founded": "2018",
    "employees": "~120",
    "revenue": "비공개",
    "countries_count": 1,
    "key_products": [
      "Antakhib/Intakhib 모바일 생체인증 선거앱",
      "T5-OmniMatch ABIS"
    ],
    "categories": [
      "Biometric",
      "Internet",
      "Software"
    ],
    "overlap": "Indirect",
    "overlap_markets": [
      "OMN"
    ],
    "strengths": [
      "NIST 최상위 생체인식 알고리즘",
      "오만 2022/2023 국가선거 NFC+생체 원격투표 실증 — 유일 벤더",
      "창업자 Aadhaar(13억)/인도네시아 국민ID(1.93억) 경력"
    ],
    "weaknesses": [
      "선거 레퍼런스 오만 단일",
      "~120명 소형사",
      "법집행·DPI가 주 사업 — 선거기술 2차적"
    ],
    "news": "2026.1 Salica Investments 성장대출 확보 / 이라크 거주자 ID 지원(2025.8)",
    "confidence": "Med"
  },
  {
    "slug": "champtek",
    "name": "Champtek Inc.",
    "flag": "🇹🇼",
    "hq": "New Taipei City, Taiwan",
    "homepage": "https://www.champtek.com",
    "type": "Private",
    "founded": "1985",
    "employees": "11~50",
    "revenue": "비공개",
    "countries_count": 1,
    "key_products": [
      "X-100 10.1인치 VMD(유권자관리단말)",
      "Z Series 생체키트"
    ],
    "categories": [
      "Biometric",
      "OMR",
      "Software"
    ],
    "overlap": "Indirect",
    "overlap_markets": [
      "ZAF"
    ],
    "strengths": [
      "하드웨어 전용 제조 — 모듈식 생체인식 통합",
      "CHAMPTEK·SCANTECH ID 이중 브랜드 30개국+ 유통망",
      "FBI 인증 지문, AFIS/ABIS 지원"
    ],
    "weaknesses": [
      "남아공 IEC X-100 VMD 2021·2024 선거 모두 현장 중단",
      "11~50명 극소형사",
      "Ren-Form 유통사 의존"
    ],
    "news": "2026.6 Computex 타이페이 / 남아공 IEC 재입찰 결정 미발표",
    "confidence": "Med"
  },
  {
    "slug": "samsung_sds",
    "name": "Samsung SDS",
    "flag": "🇰🇷",
    "hq": "Seoul, South Korea",
    "homepage": "https://www.samsungsds.com/en/index.html",
    "type": "Public",
    "founded": "1985",
    "employees": "~26,000",
    "revenue": "~$10.1B",
    "countries_count": 0,
    "key_products": [
      "Nexsign 생체인증",
      "Nexledger 블록체인",
      "FabriX 생성AI"
    ],
    "categories": [
      "Software",
      "Biometric"
    ],
    "overlap": "None",
    "overlap_markets": [],
    "strengths": [
      "삼성그룹 브랜드 + 계열사 안정 수요",
      "AI·클라우드 풀스택(SCP·FabriX·Brity Works)",
      "방글라데시 NID 기반 선거인 확인 레퍼런스"
    ],
    "weaknesses": [
      "삼성 계열사 매출 의존도",
      "선거기술 전용 포트폴리오 없음",
      "아태 외 국제 브랜드 인지도 낮음"
    ],
    "news": "2026.4 KKR KRW 1.22조(~$820M) 전환사채 투자 / FY2025 매출 KRW 13.93조",
    "confidence": "High"
  },
  {
    "slug": "sopra_steria",
    "name": "Sopra Steria",
    "flag": "🇫🇷",
    "hq": "Paris, France",
    "homepage": "https://www.soprasteria.com",
    "type": "Public",
    "founded": "2014",
    "employees": "~51,000",
    "revenue": "~$6.0B",
    "countries_count": 1,
    "key_products": [
      "EU Shared Biometric Matching System(sBMS)",
      "FAED V3 프랑스 형사지문DB"
    ],
    "categories": [
      "Software",
      "Biometric"
    ],
    "overlap": "None",
    "overlap_markets": [],
    "strengths": [
      "유럽 공공기관 IT 톱5 — 프랑스·영국·EU 기관 깊은 관계",
      "EU 국경 생체인식(SIS II·sBMS) 계약",
      "유럽 디지털 주권 포지셔닝 — ESTIA 클라우드 연합"
    ],
    "weaknesses": [
      "선거기술 전용 제품 없음",
      "EDPS 감사(2025): SIS II 수천개 고심각도 취약점",
      "프랑스 43%·영국 16% 매출 집중"
    ],
    "news": "Q1 2026 매출 +3.4% 반등 / sBMS 2025.8 eu-LISA와 가동",
    "confidence": "High"
  }
];

window.MIRU_CONTRACT_DATA = {
  "PRY": {
    "tier": "CRITICAL",
    "next_tender": "2027",
    "contract_end": "2026",
    "contract_type": "lease",
    "notes": "임대 계약 10월 종료 → 2028 총선 입찰 예정. Miru 기존 참여사."
  },
  "ARG": {
    "tier": "CRITICAL",
    "next_tender": "2027",
    "contract_end": "2025",
    "contract_type": "service",
    "notes": "CABA 선거별 서비스 계약(MSA 단독입찰 ~$22M) → 2027 재입찰."
  },
  "ARE": {
    "tier": "CRITICAL",
    "next_tender": "2026-2027",
    "contract_end": "2023",
    "contract_type": "service",
    "notes": "FNC 선거별 계약 (Scytl 4연속) → 2027 FNC 선거 입찰 2026년 개시."
  },
  "OMN": {
    "tier": "CRITICAL",
    "next_tender": "2026-2027",
    "contract_end": "unknown",
    "contract_type": "service",
    "notes": "Shura 4년 주기 → 2027 선거 입찰 예상. Iraq 생체카메라 레퍼런스 활용 가능."
  },
  "PHL": {
    "tier": "WATCH",
    "next_tender": "2027",
    "contract_end": "2025",
    "contract_type": "lease",
    "notes": "Miru P17.99B 임대 완료 → COMELEC 2028 ACM 입찰 2027년 예정 (4월 기술전시회 완료)."
  },
  "BEL": {
    "tier": "WATCH",
    "next_tender": "2026-2027",
    "contract_end": "2027",
    "contract_type": "service",
    "notes": "Smartmatic 15년 계약(2012) 만료 예정 → 2029 선거용 재입찰. EU 조달법 적용."
  },
  "BGR": {
    "tier": "WATCH",
    "next_tender": "2026-2027",
    "contract_end": "2024",
    "contract_type": "purchase",
    "notes": "소프트웨어 보증 만료 → Ciela Norma 단독계약 대체 입법 논의중."
  },
  "CHE": {
    "tier": "WATCH",
    "next_tender": "2027-2028",
    "contract_end": "2027",
    "contract_type": "pilot",
    "notes": "Swiss Post 연방 라이선스 2027년 6월 만료 → 재심사. 경쟁입찰 없음."
  },
  "BRA": {
    "tier": "WATCH",
    "next_tender": "2027",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "UE2028 공청회 진행중(2026.6) → 2027 공식 입찰. 22만대 규모. 국내 JV 필요."
  },
  "GEO": {
    "tier": "MONITOR",
    "next_tender": "2027-2028",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "선거별 Smartmatic 조달(2025 $2.3M 추가) → 2028 의회선거 입찰."
  },
  "ALB": {
    "tier": "MONITOR",
    "next_tender": "2027-2029",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "EU 자금 $20M EVM 파일럿 → 전국 확대 미결정. 2027 지방/2029 의회."
  },
  "MNG": {
    "tier": "MONITOR",
    "next_tender": "2026-2028",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "2012년 Dominion 장비 14년 경과 → Liberty Vote 브랜드 변경이 진입 기회."
  },
  "KOR": {
    "tier": "MONITOR",
    "next_tender": "2027-2030",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "10년 주기 교체 (2013→2022) → 다음 교체 2027-2030. KRW 32.5B 규모."
  },
  "COD": {
    "tier": "MONITOR",
    "next_tender": "2027-2028",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "Miru $250M+ 장비 보유 → 2028 총선 교체/추가 조달. AS 계약 진행중."
  },
  "IRQ": {
    "tier": "MONITOR",
    "next_tender": "2028-2029",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "Miru ~$135M 장비 보유 → 2025년 생체카메라 추가. 10년 주기 2028-2029."
  },
  "ZAF": {
    "tier": "MONITOR",
    "next_tender": "2027-2030",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "VMD 2024 선거 오작동 → 교체 압박. DRE 도입 Green Paper 2026 결정 예정."
  },
  "KGZ": {
    "tier": "MONITOR",
    "next_tender": "2028-2030",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "Miru KOICA 자금 PCOS 5-in-1 → 2025 선거 재사용. 10년 수명 2028-2030."
  },
  "BIH": {
    "tier": "LONG",
    "next_tender": "2029-2030",
    "contract_end": "2030",
    "contract_type": "purchase",
    "notes": "2026년 체결 4년 계약 74.5M BAM(38M EUR) → 2030 만료."
  },
  "IND": {
    "tier": "LONG",
    "next_tender": "2027-2030",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "국영제조사(BEL/ECIL) 직발주 → 민간입찰 없음. M3A 도입중."
  },
  "BTN": {
    "tier": "LONG",
    "next_tender": "2027-2028",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "2008/2013 BEL/ECIL 장비 18년 경과 → 2028 선거 전 교체. 인도 재조달 예상."
  },
  "EST": {
    "tier": "LONG",
    "next_tender": "unknown",
    "contract_end": "owned/ongoing",
    "contract_type": "service",
    "notes": "국가직영 오픈소스 i-Voting → Miru 진입 불가."
  },
  "USA": {
    "tier": "LONG",
    "next_tender": "2027-2030",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "카운티별 10년 교체 물결 2027-2030. GA Dominion(Liberty Vote) 2029 만료."
  },
  "VEN": {
    "tier": "LONG",
    "next_tender": "2030-2031",
    "contract_end": "owned/ongoing",
    "contract_type": "purchase",
    "notes": "OFAC 제재 ExClé 운영 → 불투명 조달. 다음 대선 2031."
  },
  "IRN": {
    "tier": "UNKNOWN",
    "next_tender": "unknown",
    "contract_end": "unknown",
    "contract_type": "pilot",
    "notes": "소규모 파일럿 (4-8개 선거구) → 제재 환경. 진입 불가."
  },
  "UZB": {
    "tier": "UNKNOWN",
    "next_tender": "2027-2028",
    "contract_end": "unknown",
    "contract_type": "pilot",
    "notes": "37대 파일럿(2024) → 2029 의회선거 전 본격 입찰 예상 2027-2028."
  }
};

window.MIRU_TIER_META = {
  "CRITICAL": {
    "color": "#EB0513",
    "label": "즉시 대응",
    "icon": "🔴"
  },
  "WATCH": {
    "color": "#D4870A",
    "label": "제안 준비",
    "icon": "🟠"
  },
  "MONITOR": {
    "color": "#4d9fff",
    "label": "모니터링",
    "icon": "🔵"
  },
  "LONG": {
    "color": "#8A94A6",
    "label": "장기 관찰",
    "icon": "⚫"
  },
  "UNKNOWN": {
    "color": "#C0C6D0",
    "label": "정보 부족",
    "icon": "⬜"
  }
};
