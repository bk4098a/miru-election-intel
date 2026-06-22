"""
전 세계 선거 기술 현황 DB 구축
수집된 데이터를 기반으로 SQLite DB 생성
"""
import sqlite3, csv, io, sys, pathlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = pathlib.Path("data/election_technology_world.db")
CSV_PATH = pathlib.Path("data/election_technology_world.csv")

SCHEMA = """
CREATE TABLE IF NOT EXISTS countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,
    country_ko TEXT,
    iso3 TEXT,
    region TEXT,
    has_elections TEXT,          -- Y / Limited / N
    last_election_date TEXT,
    next_election_date TEXT,
    voting_method TEXT,          -- Paper / OMR / EVM / DRE / Internet / Mixed
    biometric_voter_reg TEXT,    -- Y / N / Partial
    biometric_voter_verify TEXT, -- Y / N / Partial
    electronic_results_tx TEXT,  -- Y / N / Partial
    evoting TEXT,                -- Y / N / Partial
    vendor TEXT,
    confidence TEXT,             -- High / Med / Low
    source TEXT,
    notes TEXT,
    updated_date TEXT DEFAULT '2026-06-22'
);
CREATE INDEX IF NOT EXISTS idx_region ON countries(region);
CREATE INDEX IF NOT EXISTS idx_has_elections ON countries(has_elections);
CREATE INDEX IF NOT EXISTS idx_evoting ON countries(evoting);
CREATE INDEX IF NOT EXISTS idx_biometric_voter_verify ON countries(biometric_voter_verify);
"""

# 전 세계 ~200개국 데이터
# 출처: International IDEA, IFES, ODIHR, EU EOM, NDI, 각국 선거위원회
DATA = [
    # ===== 중동·북아프리카 =====
    ("Iraq","이라크","IRQ","Middle East","Y","2025-11-11","2029","Mixed","Y","Y","Y","Y","Miru Systems/Thales","High","IHEC/biometricupdate.com","OMR 광학스캐너(Miru PCOS)+투표소 지문+FRT 본인확인. 2025선거 FRT 신규 추가"),
    ("Iran","이란","IRN","Middle East","Limited","2024-07-05","2028","Mixed","N","N","Y","Y","Smartmatic(보도)/국산","Med","mehrnews.com","의회선거 EVM 일부(테헤란 등). 대통령선거는 종이. 최고지도자 체제"),
    ("Israel","이스라엘","ISR","Middle East","Y","2022-11-01","2026","Paper","N","N","Y","N","CEC 자체 폐쇄망","High","knesset.gov.il","완전 종이+수개표. 인터넷 미연결 폐쇄망. 고의적 저기술 정책"),
    ("Jordan","요르단","JOR","Middle East","Limited","2024-09-10","2028","Paper","N","N","N","N","","High","IFES/EU EOM 2024","종이투표. 정당금지(무소속만). EU EOM 18개 권고"),
    ("Kuwait","쿠웨이트","KWT","Middle East","Limited","2024-04-04","2028","Paper","N","N","N","N","","High","IPU Parline","종이투표. 에미르 의회해산 후 2024-04 총선"),
    ("Lebanon","레바논","LBN","Middle East","Y","2022-05-15","2026","Paper","N","N","N","N","","Med","IFES/UNDP","종이투표. 이스라엘 전쟁 영향. 해외유권자 온라인등록 도입"),
    ("Libya","리비아","LBY","Middle East","N","","","","N","N","N","N","","High","HRW 2025","동·서부 분열. 국가선거 무기한 연기"),
    ("Morocco","모로코","MAR","Middle East","Limited","2021-09-08","2026-09-23","Paper","N","N","N","N","","Med","Wikipedia/IFES","종이투표. 2026선거 앞두고 생체유권자등록 개혁 논의"),
    ("Oman","오만","OMN","Middle East","Limited","2023-10-29","2027","EVM","Y","Y","Y","Y","MoI 자체 앱 Intakhib","High","Gulf International Forum","2023 완전 디지털화. AI 얼굴인식+NFC. 앱으로 온라인투표"),
    ("Palestine","팔레스타인","PSE","Middle East","N","2006-01-25","","","N","N","N","N","","High","USIP","2006 이후 국가선거 없음. 가자분쟁으로 전망 없음"),
    ("Qatar","카타르","QAT","Middle East","N","2021-10-02","","Paper","N","N","N","N","","Med","IPU Parline","슈라위원회 일부 선출. 국가선거 개념 없음"),
    ("Saudi Arabia","사우디아라비아","SAU","Middle East","N","","","","N","N","N","N","","High","my.gov.sa","국가선거 없음. 슈라위원회 전원 임명"),
    ("Syria","시리아","SYR","Middle East","N","","","","N","N","N","N","","Med","IDEA","2024-12 아사드 붕괴. 민주제도 미확립"),
    ("Tunisia","튀니지","TUN","Middle East","Limited","2024-10-06","2029","Paper","Y","N","N","N","ISIE 자체","High","IFES/ISIE","자동유권자등록. 사이에드 90.7% 압승. 2022 신헌법 민주후퇴"),
    ("Turkey","터키","TUR","Middle East","Y","2023-05-28","2028","Paper","N","N","Y","N","YSK 자체","High","Wikipedia/YSK","완전 종이+공개수개표. 생체e-ID 있으나 투표 미사용"),
    ("UAE","아랍에미리트","ARE","Middle East","Limited","2023-10-07","2027","EVM","Y","Y","Y","Y","ICA 자체 스마트카드","High","u.ae","FNC 40석 중 20석 선출. 스마트ID 생체인증+EVM"),
    ("Bahrain","바레인","BHR","Middle East","Limited","2022-11-12","2026","OMR","N","N","Y","N","전자스캐너","Med","zawya.com/IPU","종이투표지+OMR 스캐너 개표. 야당 배제"),
    ("Yemen","예멘","YEM","Middle East","N","","","","N","N","N","N","","High","Arab Center DC","내전. 2011 이후 실질선거 없음"),

    # ===== 중앙아시아 =====
    ("Kazakhstan","카자흐스탄","KAZ","Central Asia","Limited","2023-03-19","2027","Mixed","N","Y","Y","Y","Sailau(카자흐+벨라루스)","High","ODIHR/IFES","종이+EVM 병행. 2026-04 CEC 전자투표 도입 안 함 발표"),
    ("Kyrgyzstan","키르기스스탄","KGZ","Central Asia","Limited","2025-11-30","2027-01","Mixed","Y","Y","Y","Y","Miru Systems(한국)","High","ODIHR/OSCE PA","5-in-1 복합기: 여권바이오+지문/얼굴+투표지인쇄+집계. MIRU PCOS(2018)+AI-CCTV(2024/25)"),
    ("Tajikistan","타지키스탄","TJK","Central Asia","Limited","2025-03-02","2030","Paper","N","N","N","N","","High","ODIHR 취소","ODIHR 관찰단 자격증명 거부. 형식적 선거"),
    ("Turkmenistan","투르크메니스탄","TKM","Central Asia","Limited","2023-03-26","2028","Paper","N","N","N","N","","High","ODIHR EAM","세계 최폐쇄 선거 시스템 중 하나. ODIHR 국제기준 미달"),
    ("Uzbekistan","우즈베키스탄","UZB","Central Asia","Limited","2024-10-27","2029","Mixed","N","N","Y","Y","자체개발(파일럿)","High","ODIHR 2024/IFES","최초 EVM 파일럿(타슈켄트 37대). 종이+전자 선택"),
    ("Afghanistan","아프가니스탄","AFG","Central Asia","N","2019-09-28","","","N","N","N","N","Dermalog(과거)","High","Al Jazeera/Freedom House","탈레반 2021 집권. 선거위원회 해산. 모든 정당 금지"),
    ("Pakistan","파키스탄","PAK","Central Asia","Y","2024-02-08","2029","Paper","Y","N","Y","N","NADRA(등록/EMS)","High","ECP/NADRA","종이투표. EVM 계획 2022 폐기. NADRA 전산선거인부+EMS"),

    # ===== 아프리카 =====
    ("Algeria","알제리","DZA","Africa","Limited","2024-09-07","2029","Paper","Y","N","N","N","","High","IDEA/IFES","종이투표. 부테플리카 이후 권위주의 강화"),
    ("Angola","앙골라","AGO","Africa","Limited","2022-08-24","2027","Paper","Y","N","N","N","Minsait(Indra)","High","CNE/indracompany.com","종이투표. Minsait 총선 기술통합계약. 2008부터 연속"),
    ("Benin","베냉","BEN","Africa","Limited","2026-04-12","2031","Paper","Y","N","N","N","","Med","IDEA","야당 참가 제한"),
    ("Botswana","보츠와나","BWA","Africa","Y","2024-10-30","2029","Paper","Y","N","N","N","Ren-Form(용지인쇄)","High","IEC/VOA","종이투표. 2024 투표용지 해외인쇄 논란"),
    ("Burkina Faso","부르키나파소","BFA","Africa","N","2020-11-22","","","Y","N","N","N","Thales+Innovatrics","High","Freedom House","2022 쿠데타. 선거 중단"),
    ("Burundi","부룬디","BDI","Africa","Limited","2020-05-20","2025","Paper","Y","N","N","N","","High","IDEA","형식적 선거"),
    ("Cabo Verde","카보베르데","CPV","Africa","Y","2026-03-09","2030","Paper","Y","N","N","N","","High","IFES","아프리카 모범 민주주의"),
    ("Cameroon","카메룬","CMR","Africa","Limited","2025-10-06","2030","Paper","Y","N","N","N","G+D/GenKey/Veridos","High","ELECAM","ELECAM 생체유권자등록. 2012 G+D→2017 GenKey+Veridos"),
    ("Central African Republic","중앙아프리카공화국","CAF","Africa","Limited","2020-12-27","2025","Paper","Y","N","N","N","GenKey","Med","MINUSCA","내전 속 선거. GenKey BVR"),
    ("Chad","차드","TCD","Africa","Limited","2024-05-06","2028","Paper","Y","N","N","N","","Med","AU EOM","2024 첫 대선 투표. 군정 전환기"),
    ("Comoros","코모로","COM","Africa","Limited","2024-01-14","2029","Paper","Y","N","N","N","","Med","IDEA","쿠데타 역사. 형식적 선거"),
    ("Congo Republic","콩고(브라자빌)","COG","Africa","Limited","2024-03-21","2029","Paper","Y","N","N","N","","Med","IDEA","사수 장기집권"),
    ("DRC","콩고(킨샤사)","COD","Africa","Limited","2023-12-20","2028","EVM","Y","N","Y","Y","Miru Systems","High","CENI/biometricupdate.com","MIRU BMS 터치스크린+VSAT 결과전송. 2018·2023 공급"),
    ("Djibouti","지부티","DJI","Africa","Limited","2021-04-09","2026-04-10","Paper","N","N","N","N","","High","IDEA","일당 지배. 형식적 선거"),
    ("Egypt","이집트","EGY","Africa","Limited","2024-12-10","2029","Paper","Y","N","N","N","","High","IDEA","시시 90%+ 형식적 선거"),
    ("Equatorial Guinea","적도기니","GNQ","Africa","Limited","2022-11-20","2027","Paper","N","N","N","N","","Med","IDEA","오비앙 45년 집권"),
    ("Eritrea","에리트레아","ERI","Africa","N","","","","N","N","N","N","","High","Freedom House","1993년 이후 국가선거 전무"),
    ("Eswatini","에스와티니","SWZ","Africa","Limited","2023-09-29","2028","Paper","N","N","N","N","","High","IDEA","절대군주제. 정당 금지"),
    ("Ethiopia","에티오피아","ETH","Africa","Limited","2021-06-21","2026","Paper","Y","N","N","N","NEBE 자체앱","High","UNDP SEEDS","자체개발 모바일+웹 앱(6개언어). UNDP SEEDS USD 40M+"),
    ("Gabon","가봉","GAB","Africa","N","2023-08-26","","","N","N","N","N","","High","Freedom House","2023 쿠데타. 선거 중단"),
    ("Gambia","감비아","GMB","Africa","Y","2021-12-04","2026","Paper","Y","N","N","N","ESI(캐나다)","High","IEC Gambia","ESI USD 299.5만. GPPA 공개경쟁입찰. 2011·2016·2021 연속"),
    ("Ghana","가나","GHA","Africa","Y","2024-12-07","2028","OMR","Y","Y","Y","N","Thales+STL","High","EC Ghana/biometricupdate.com","BVD+OMR 광학스캐너. 2020 BVMS Thales 낙찰(Miru 입찰 참가)"),
    ("Guinea","기니","GIN","Africa","Limited","2024-12-22","2028","Paper","Y","N","N","N","Innovatrics(슬로바키아)","High","CENI/biometricupdate.com","2019 공개경쟁입찰 Innovatrics 수주. 4000대 모바일 스테이션"),
    ("Guinea-Bissau","기니비사우","GNB","Africa","Limited","2024-06-04","2028","Paper","Y","N","N","N","","Med","IDEA","정치 불안정. 쿠데타 역사"),
    ("Ivory Coast","코트디부아르","CIV","Africa","Limited","2025-10-25","2030","Paper","Y","N","N","N","IDEMIA+Albatross","High","CEI/biometricupdate.com","2020 USD 1700만 IDEMIA+Albatross. 2015 동일 컨소시엄 재계약"),
    ("Kenya","케냐","KEN","Africa","Y","2022-08-09","2027","Mixed","Y","Y","Y","N","Smartmatic(KIEMS)","High","IEBC/IFES","Smartmatic KIEMS BVD+전자결과전송. 2017 논란 후 유지"),
    ("Lesotho","레소토","LSO","Africa","Y","2022-10-07","2027","Paper","Y","N","N","N","Toppan Gravity","High","IEC Lesotho","Toppan Gravity(구 De La Rue) 2001~24년 파트너. 웹기반 VRMS"),
    ("Liberia","라이베리아","LBR","Africa","Y","2023-10-10","2028","Paper","Y","N","N","N","Neurotechnology","High","NEC Liberia/IFES","Neurotechnology BVR"),
    ("Libya","리비아","LBY","Africa","N","","","","N","N","N","N","","High","Security Council Report","동서 분열. 국가선거 무기한 연기"),
    ("Madagascar","마다가스카르","MDG","Africa","Limited","2023-11-16","2028","Paper","N","N","N","N","UNDP SACEM","High","UNDP/SACEM","UNDP SACEM USD 1369만. VSAT 결과전송(지원). 2018는 종이명부"),
    ("Malawi","말라위","MWI","Africa","Y","2020-06-23","2025-09-16","Paper","Y","N","N","N","Laxton","High","MEC/biometricupdate.com","Laxton BRK 2000대(UNDP NRB용 전용). 말라위 최초 생체인증 선거"),
    ("Mali","말리","MLI","Africa","N","2020-03-29","","","N","N","N","N","","High","Freedom House","2021 쿠데타. 선거 중단"),
    ("Mauritania","모리타니","MRT","Africa","Limited","2024-06-29","2029","Paper","Y","N","N","N","","Med","IDEA","권위주의. 형식적 선거"),
    ("Mauritius","모리셔스","MUS","Africa","Y","2024-11-10","2029","Paper","Y","N","N","N","","High","IEC Mauritius","모범 민주주의"),
    ("Mozambique","모잠비크","MOZ","Africa","Limited","2024-10-09","2029","Paper","Y","N","N","N","Laxton+Artes Gráficas","High","STAE/biometricupdate.com","Laxton+Artes Gráficas 수의계약. 16.8M명 등록(29%↑)"),
    ("Namibia","나미비아","NAM","Africa","Y","2024-11-27","2029","Paper","Y","N","N","N","Ren-Form CC(투표용지)","High","ECN/Namibian","Ren-Form CC N$6.26M 투표용지. 과거 EVM 대법원 판결로 폐기"),
    ("Niger","니제르","NER","Africa","N","2020-12-27","","","N","N","N","N","","High","Freedom House","2023 쿠데타. 선거 중단"),
    ("Nigeria","나이지리아","NGA","Africa","Y","2023-02-25","2027","Paper","Y","Y","Y","N","INEC BVAS","High","INEC/Vanguard","BVAS 생체인증+IReV 전자결과전송. 2023 최초 100% 국내인쇄"),
    ("Rwanda","르완다","RWA","Africa","Limited","2024-07-15","2029","Paper","Y","N","N","N","NIDA DB 공유","High","NEC Rwanda","NIDA 국가생체ID DB 공유 방식. 등록 9071157명"),
    ("Sao Tome and Principe","상투메프린시페","STP","Africa","Y","2024-09-25","2028","Paper","N","N","N","N","","High","IDEA","소규모 민주주의"),
    ("Senegal","세네갈","SEN","Africa","Y","2024-03-24","2029","Paper","Y","N","N","N","","High","CENA","2024 조기대선(4주 압박). CENA 감독, 조달은 내무부"),
    ("Sierra Leone","시에라리온","SLE","Africa","Y","2023-06-24","2028","Paper","Y","N","N","N","Laxton","High","IFES","Laxton BVR"),
    ("Somalia","소말리아","SOM","Africa","Limited","2022-05-15","2026","Paper","N","N","N","N","","High","IDEA","클랜 기반 간선. 완전직선 미실현"),
    ("South Africa","남아공","ZAF","Africa","Y","2024-05-29","2029","OMR","Y","N","N","N","Ren-Form Litho(BVD)","High","IEC/Daily Maverick","Ren-Form Litho R566.1M VMD 4만대. OMR 개표. 2024 해외인쇄"),
    ("South Sudan","남수단","SSD","Africa","N","2010-04-11","","","N","N","N","N","","High","IDEA","2010 이후 국가선거 미실시"),
    ("Sudan","수단","SDN","Africa","N","2023-04-15","","","N","N","N","N","","High","HRW","SAF-RSF 내전. 선거 불가"),
    ("Tanzania","탄자니아","TZA","Africa","Limited","2020-10-28","2025-10","Paper","Y","N","N","N","Laxton","High","NEC Tanzania","Laxton BRK 8000대. 22658247명(유권자 96%). 2015 최초도입"),
    ("Togo","토고","TGO","Africa","Limited","2024-04-20","2028","Paper","Y","N","N","N","Zetes","Med","CENI Togo","Zetes BVR"),
    ("Tunisia","튀니지(아프리카)","TUN","Africa","Limited","2024-10-06","2029","Paper","Y","N","N","N","ISIE","High","ISIE/IFES","자동유권자등록. 민주후퇴"),
    ("Uganda","우간다","UGA","Africa","Limited","2021-01-14","2026-01-15","Paper","Y","Y","Y","N","Smartmatic BVVK","High","EC Uganda/biometricupdate.com","BVVK(Simi Valley Tech) 109142대. 생체인증+결과전송"),
    ("Zambia","잠비아","ZMB","Africa","Y","2021-08-12","2026-08-13","Paper","Y","N","N","N","Smartmatic","High","ECZ/UNDP","Smartmatic BVR. 2026 Miru Systems BVR 수주 추진 논란"),
    ("Zimbabwe","짐바브웨","ZWE","Africa","Limited","2023-08-23","2028","Paper","Y","N","N","N","Fidelity Printers+Ren-Form CC","High","ZEC/CITE","Fidelity Printers 인쇄. Ren-Form CC 자재(ZEC/DP18/2023) 비리수사"),

    # ===== 유럽 =====
    ("Albania","알바니아","ALB","Europe","Y","2025-05-11","2029","EVM","N","Y","Y","Y","Smartmatic+Innovatrics","High","CEC Albania/ODIHR","Smartmatic EVM+Innovatrics 지문인증 전국확대 법제화"),
    ("Andorra","안도라","AND","Europe","Y","2023-04-02","2027","Paper","N","N","N","N","","High","IDEA","소규모 민주주의"),
    ("Armenia","아르메니아","ARM","Europe","Y","2021-06-20","2026","Paper","N","N","Y","N","","High","ODIHR","종이투표+전자집계"),
    ("Austria","오스트리아","AUT","Europe","Y","2024-09-29","2028","Paper","N","N","Y","N","","High","BMI Austria","종이투표. 우편투표 광범위"),
    ("Azerbaijan","아제르바이잔","AZE","Europe","Limited","2024-02-07","2028","Paper","N","N","N","N","","High","ODIHR","권위주의. 형식적 선거"),
    ("Belarus","벨라루스","BLR","Europe","Limited","2025-01-26","2030","Paper","N","N","N","N","","High","ODIHR","루카셴코 독재. 형식적 선거"),
    ("Belgium","벨기에","BEL","Europe","Y","2024-06-09","2028","EVM","N","N","Y","Y","Smartmatic bSmart500","High","IDEA/Smartmatic","Smartmatic bSmart500 EVM. 의무투표"),
    ("Bosnia and Herzegovina","보스니아헤르체고비나","BIH","Europe","Y","2022-10-02","2026-10-04","Mixed","N","Y","Y","Y","Smartmatic EUR38.1M","High","CIK/ODIHR","Smartmatic EUR 38.1M 계약. 2026 대선·총선"),
    ("Bulgaria","불가리아","BGR","Europe","Y","2024-10-27","2028","OMR","N","N","Y","N","Ciela Norma","High","CEC Bulgaria","Ciela Norma OMR. 전자투표 논쟁 중"),
    ("Croatia","크로아티아","HRV","Europe","Y","2024-04-17","2028","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Cyprus","키프로스","CYP","Europe","Y","2024-02-04","2029","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Czech Republic","체코","CZE","Europe","Y","2025-10-03","2029","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Denmark","덴마크","DNK","Europe","Y","2022-11-01","2026","Paper","N","N","Y","N","","High","IDEA","종이투표. 디지털 ID로 유권자 확인"),
    ("Estonia","에스토니아","EST","Europe","Y","2023-03-05","2027","Mixed","N","N","Y","Y","RIA(국가정보시스템청)","High","valimised.ee","i-Voting 2005년 세계 최초. 2023년 51.1% 온라인투표"),
    ("Finland","핀란드","FIN","Europe","Y","2023-04-02","2027","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("France","프랑스","FRA","Europe","Y","2022-04-24","2027","Paper","N","N","Y","N","","High","IDEA","EVM 2010년 이후 폐지. 재외국민 온라인투표 일부"),
    ("Georgia","조지아","GEO","Europe","Y","2024-10-26","2028","OMR","N","N","Y","N","Smartmatic bScan1800Plus","High","CEC Georgia/Smartmatic","bScan1800Plus 4876대. 계약 54215254 GEL"),
    ("Germany","독일","DEU","Europe","Y","2025-02-23","2029","Paper","N","N","Y","N","","High","Bundeswahlleiter","EVM 2009 위헌판결 후 종이복귀"),
    ("Greece","그리스","GRC","Europe","Y","2023-05-21","2027","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Hungary","헝가리","HUN","Europe","Y","2022-04-03","2026","Paper","N","N","Y","N","","High","IDEA","종이투표. 민주후퇴 논란"),
    ("Iceland","아이슬란드","ISL","Europe","Y","2024-11-30","2028","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Ireland","아일랜드","IRL","Europe","Y","2024-11-29","2029","Paper","N","N","Y","N","","High","IDEA","종이투표. EVM 2004~2009 시범후 폐기"),
    ("Italy","이탈리아","ITA","Europe","Y","2022-09-25","2027","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Kosovo","코소보","XKX","Europe","Y","2025-02-09","2029","Paper","N","N","Y","N","","High","ODIHR","종이투표"),
    ("Latvia","라트비아","LVA","Europe","Y","2022-10-01","2026-10-03","Paper","N","N","Y","N","","High","CVK Latvia","종이투표. OMR 도입 논의 중"),
    ("Liechtenstein","리히텐슈타인","LIE","Europe","Y","2025-02-09","2029","Paper","N","N","N","N","","High","IDEA","소규모 직접민주주의"),
    ("Lithuania","리투아니아","LTU","Europe","Y","2024-10-13","2028","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Luxembourg","룩셈부르크","LUX","Europe","Y","2023-10-08","2028","Paper","N","N","Y","N","","High","IDEA","종이투표. 의무투표"),
    ("Malta","몰타","MLT","Europe","Y","2022-03-26","2027","Paper","N","N","Y","N","","High","IDEA","STV 비례대표"),
    ("Moldova","몰도바","MDA","Europe","Y","2024-10-20","2028","Paper","N","N","Y","N","Combinatul Poligrafic+Tipografia","High","CEC Moldova/moldpres.md","Combinatul Poligrafic+Tipografia Centrală. 281만장. 400만+ 레이"),
    ("Monaco","모나코","MCO","Europe","Y","2023-02-05","2028","Paper","N","N","N","N","","High","IDEA","소규모 입헌군주제"),
    ("Montenegro","몬테네그로","MNE","Europe","Y","2023-06-11","2027","Paper","N","N","Y","N","","High","ODIHR","종이투표"),
    ("Netherlands","네덜란드","NLD","Europe","Y","2023-11-22","2027","Paper","N","N","Y","N","","High","IDEA","EVM 2008 폐기. 종이복귀"),
    ("North Macedonia","북마케도니아","MKD","Europe","Y","2024-04-24","2028","Mixed","N","Y","Y","N","SEC","High","SEC/ODIHR","생체지문확인. 혼합투표방식"),
    ("Norway","노르웨이","NOR","Europe","Y","2021-09-13","2025-09-08","Paper","N","N","Y","N","","High","IDEA","종이투표. 온라인투표 파일럿 중단"),
    ("Poland","폴란드","POL","Europe","Y","2023-10-15","2027","Paper","N","N","Y","N","","High","PKW","종이투표"),
    ("Portugal","포르투갈","PRT","Europe","Y","2024-03-10","2028","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Romania","루마니아","ROU","Europe","Y","2024-11-24","2028","Paper","N","N","Y","N","","High","BEC Romania","종이투표"),
    ("Russia","러시아","RUS","Europe","Limited","2024-03-17","2030","Paper","N","N","Y","N","CEC 자체","High","ODIHR","권위주의. 형식적 선거. 일부 전자투표 도입"),
    ("San Marino","산마리노","SMR","Europe","Y","2024-06-09","2028","Paper","N","N","N","N","","High","IDEA","소규모 공화국"),
    ("Serbia","세르비아","SRB","Europe","Y","2023-12-17","2027","Paper","N","N","Y","N","Službeni glasnik(국영)","High","RIK/rik.parlament.gov.rs","종이투표. Službeni glasnik 6500165장"),
    ("Slovakia","슬로바키아","SVK","Europe","Y","2023-09-30","2027","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Slovenia","슬로베니아","SVN","Europe","Y","2022-04-24","2026","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Spain","스페인","ESP","Europe","Y","2023-07-23","2027","Paper","N","N","Y","N","","High","JEC Spain","종이투표"),
    ("Sweden","스웨덴","SWE","Europe","Y","2022-09-11","2026","Paper","N","N","Y","N","","High","Valmyndigheten","종이투표"),
    ("Switzerland","스위스","CHE","Europe","Y","2023-10-22","2027","Mixed","N","N","Y","Y","Swiss Post","High","Bundeskanzlei","Post e-voting 파일럿. 제한적 온라인투표"),
    ("Turkey","터키(유럽)","TUR","Europe","Y","2023-05-28","2028","Paper","N","N","Y","N","YSK","High","YSK","종이투표+전자집계"),
    ("Ukraine","우크라이나","UKR","Europe","Limited","2019-04-21","","Paper","N","N","N","N","","High","ODIHR","계엄령으로 선거 중단. 전후 재건 수요 예상"),
    ("United Kingdom","영국","GBR","Europe","Y","2024-07-04","2029","Paper","N","N","Y","N","","High","Electoral Commission","FPTP 종이투표"),
    ("Vatican","바티칸","VAT","Europe","N","","","","N","N","N","N","","High","IDEA","교황 임명제. 선거 없음"),

    # ===== 아시아-태평양 =====
    ("Afghanistan","아프가니스탄(아시아)","AFG","Asia-Pacific","N","2019-09-28","","","N","N","N","N","Dermalog(과거)","High","Freedom House","탈레반 집권. 선거 없음"),
    ("Australia","호주","AUS","Asia-Pacific","Y","2025-05-03","2028","Paper","N","N","Y","N","AEC 자체","High","AEC","종이투표+수개표. 우편투표 광범위"),
    ("Bangladesh","방글라데시","BGD","Asia-Pacific","Limited","2024-01-07","2029","Paper","Y","N","N","N","Neurotechnology+Dohatec","High","EC Bangladesh","EVM 2025년 7월 영구폐기. BGP(국영) 종이인쇄"),
    ("Bhutan","부탄","BTN","Asia-Pacific","Y","2024-01-09","2028","EVM","Y","N","N","Y","BEL+ECIL(인도산)","High","ECB Bhutan","인도산 EVM 1618대. 809개 투표소"),
    ("Brunei","브루나이","BRN","Asia-Pacific","N","","","","N","N","N","N","","High","Freedom House","절대군주제. 국가선거 없음"),
    ("Cambodia","캄보디아","KHM","Asia-Pacific","Limited","2023-07-23","2028","Paper","N","N","N","N","Navin Printing House(용지)","High","NEC Cambodia","2016년 EU 지원 장비 재사용. Navin Printing House 투표용지"),
    ("China","중국","CHN","Asia-Pacific","N","","","","N","N","N","N","","High","Freedom House","인민대표대회 간선. 국가선거 없음"),
    ("Fiji","피지","FJI","Asia-Pacific","Y","2022-12-14","2026","Paper","Y","N","N","N","ESI(캐나다)","High","FEO/IFES","ESI BVR 2012+2024. 2026 선거 준비 중"),
    ("India","인도","IND","Asia-Pacific","Y","2024-04-19","2029","EVM","N","N","N","Y","BEL+ECIL","High","ECI India","M3 EVM 전국 사용. BVR=N(EPIC는 사진ID만)"),
    ("Indonesia","인도네시아","IDN","Asia-Pacific","Y","2024-02-14","2029","Paper","Y","N","Y","N","KPU 자체(Sirekap)","High","KPU/IFES","SIDALIH+Dukcapil e-KTP 연계. Sirekap 결과전송. 204807222명"),
    ("Japan","일본","JPN","Asia-Pacific","Y","2025-07-20","2028","Paper","N","N","Y","N","","High","Somusho/IPU","자필기명 종이투표. 참의원 2025-07-20. 여당 과반실패"),
    ("Kazakhstan","카자흐스탄(아시아)","KAZ","Asia-Pacific","Limited","2023-03-19","2027","Mixed","N","Y","Y","Y","Sailau(자체+벨라루스)","High","ODIHR/IFES","EVM+종이 병행. Sailau 시스템"),
    ("Kiribati","키리바시","KIR","Asia-Pacific","Y","2024-08-14","2028","Paper","N","N","N","N","","High","IFES/IPU","종이투표"),
    ("Kyrgyzstan","키르기스스탄(아시아)","KGZ","Asia-Pacific","Limited","2025-11-30","2027-01","Mixed","Y","Y","Y","Y","Miru Systems(한국)","High","ODIHR/OSCE","5-in-1 복합기. MIRU PCOS(2018)+AI-CCTV. 2027-01 대선"),
    ("Laos","라오스","LAO","Asia-Pacific","Limited","2026-02-22","2031","Paper","N","N","N","N","","High","IPU Parline","일당제. 2026-02 의회선거"),
    ("Malaysia","말레이시아","MYS","Asia-Pacific","Y","2023-11-19","2027","Paper","N","N","N","N","PNMB(국영)","High","SPR/Utusan","PNMB(국영,재무부 산하) 투표용지인쇄. 상시계약"),
    ("Maldives","몰디브","MDV","Asia-Pacific","Y","2024-04-21","2029","Paper","N","N","N","N","","High","ECM/IFES","종이투표"),
    ("Marshall Islands","마샬제도","MHL","Asia-Pacific","Y","2023-11-20","2027","Paper","N","N","N","N","","High","IFES/IDEA","종이투표+우편투표"),
    ("Micronesia","미크로네시아","FSM","Asia-Pacific","Y","2025-03-04","2027","Paper","N","N","N","N","","High","IFES/FSMEC","종이투표+부재자투표"),
    ("Mongolia","몽골","MNG","Asia-Pacific","Y","2024-06-28","2028","OMR","Y","N","Y","N","Dominion(ImageCast)","High","GEC Mongolia/IDEA","Dominion ImageCast OMR"),
    ("Myanmar","미얀마","MMR","Asia-Pacific","Limited","2020-11-08","","Paper","N","N","N","N","","High","Freedom House","2021 군부쿠데타. 마지막 공정선거 2020"),
    ("Nauru","나우루","NRU","Asia-Pacific","Y","2025-10-11","2028","Paper","N","N","N","N","","High","IPU Parline","Dowdall 순위투표제. 의무투표. 99% 참여율"),
    ("Nepal","네팔","NPL","Asia-Pacific","Y","2026-03-05","2030","Paper","Y","N","N","N","","High","EC Nepal","2025-11 NID 생체DB 선관위 연계. EVM 미사용(정당반대)"),
    ("New Zealand","뉴질랜드","NZL","Asia-Pacific","Y","2023-10-14","2026-11-07","Paper","N","N","Y","N","Electoral Commission 자체","High","elections.nz","MMP 종이투표. 2026-11-07 확정"),
    ("North Korea","북한","PRK","Asia-Pacific","N","2026-03-15","","Paper","N","N","N","N","","High","The Diplomat","SPA 단일후보. 사실상 선거 없음. 2026-03 실시"),
    ("Pakistan","파키스탄(아시아)","PAK","Asia-Pacific","Y","2024-02-08","2029","Paper","Y","N","Y","N","NADRA","High","ECP/NADRA","종이투표. EVM 2022 폐기. NADRA 전산선거인부"),
    ("Palau","팔라우","PLW","Asia-Pacific","Y","2024-11-05","2028","Paper","N","N","N","N","","High","IFES","종이투표"),
    ("Papua New Guinea","파푸아뉴기니","PNG","Asia-Pacific","Y","2022-07-04","2027","Paper","N","N","N","N","","Med","PNGEC/biometricupdate.com","BVR 2027 목표이나 예산 미집행. 준비 안 됨 공식 발표"),
    ("Philippines","필리핀","PHL","Asia-Pacific","Y","2025-05-12","2028","OMR","Y","N","Y","N","Miru Systems(ACM 11만대)","High","COMELEC/Rappler","Miru Systems ACM 110620대 ₱17.9B. Smartmatic 교체"),
    ("Samoa","사모아","WSM","Asia-Pacific","Y","2025-08-29","2030","Paper","N","N","N","N","","High","IDEA","조기총선. FAST 재집권"),
    ("Singapore","싱가포르","SGP","Asia-Pacific","Y","2025-05-03","2030","Paper","N","N","N","N","ELD 자체","High","ELD/Wikipedia","PAP 65.6% 압승. NRIC 기반 자동등록. 의무투표"),
    ("Solomon Islands","솔로몬제도","SLB","Asia-Pacific","Y","2024-04-17","2028","Paper","Y","N","N","N","ESI(캐나다)","High","SIEC/IFES","ESI BVR 2014·2018·2023/24"),
    ("South Korea","대한민국","KOR","Asia-Pacific","Y","2025-06-03","2027-03","OMR","N","N","Y","N","Miru Systems(개표기)","High","NEC Korea","OMR 개표기. 2025-06-03 대선. MIRU 공급"),
    ("Sri Lanka","스리랑카","LKA","Asia-Pacific","Y","2024-11-14","2029","Paper","N","N","Y","N","","High","EC Sri Lanka","종이투표. e-NIC 도입 지연중"),
    ("Taiwan","대만","TWN","Asia-Pacific","Y","2024-01-13","2028-01","Paper","N","N","N","N","","High","CEC Taiwan","전자투표 공식 거부. 완전 종이+수개표"),
    ("Tajikistan","타지키스탄(아시아)","TJK","Asia-Pacific","Limited","2025-03-02","2030","Paper","N","N","N","N","","High","ODIHR","ODIHR 불참. 형식적 선거"),
    ("Thailand","태국","THA","Asia-Pacific","Y","2023-05-14","2027","Paper","N","N","Y","N","ECT(소프트웨어만)","High","ANFREL","종이+수개표. ECT Report는 집계소프트웨어"),
    ("Timor-Leste","동티모르","TLS","Asia-Pacific","Y","2023-05-22","2027","Paper","Y","N","N","N","STAE 자체","High","STAE/IFES","BVRS 2024-07 착수(USD 60만). 2027 대선 적용목표"),
    ("Tonga","통가","TON","Asia-Pacific","Y","2025-11-20","2029","Paper","N","N","N","N","","High","IPU Parline","종이투표. 해외투표 없음"),
    ("Turkmenistan","투르크메니스탄(아시아)","TKM","Asia-Pacific","Limited","2023-03-26","2028","Paper","N","N","N","N","","High","ODIHR EAM","세계 최폐쇄 선거시스템"),
    ("Tuvalu","투발루","TUV","Asia-Pacific","Y","2024-01-26","2028","Paper","N","N","N","N","","High","IPU Parline","MNTV 방식. 소규모"),
    ("Uzbekistan","우즈베키스탄(아시아)","UZB","Asia-Pacific","Limited","2024-10-27","2029","Mixed","N","N","Y","Y","자체개발(파일럿)","High","ODIHR 2024","EVM 파일럿(타슈켄트 37대)"),
    ("Vanuatu","바누아투","VUT","Asia-Pacific","Y","2025-01-16","2028","Paper","N","N","N","N","","High","Vanuatu EO","SNTV+FPTP. NZD 5M UNDP/NZ 지원"),
    ("Vietnam","베트남","VNM","Asia-Pacific","Limited","2026-03-15","2031","Paper","Y","N","Y","N","내부개발(Project 06)","High","biometricupdate.com","VNeID 앱 기반 생체등록 2026 최초 적용. 일당제"),

    # ===== 아메리카 =====
    ("Antigua and Barbuda","앤티가바부다","ATG","Americas","Y","2023-01-18","2028","Paper","N","N","N","N","","High","IDEA","소규모 카리브 민주주의"),
    ("Argentina","아르헨티나","ARG","Americas","Y","2023-10-22","2027","Mixed","Y","N","Y","N","자체(BUE일부)","High","IDEA/OEA","BUE(Boleta Única Electrónica) 일부 주 사용. 전자결과전송"),
    ("Bahamas","바하마","BHS","Americas","Y","2021-09-16","2026","Paper","N","N","N","N","","High","IDEA","종이투표"),
    ("Barbados","바베이도스","BRB","Americas","Y","2022-01-19","2027","Paper","N","N","N","N","","High","IDEA","종이투표"),
    ("Belize","벨리즈","BLZ","Americas","Y","2025-03-12","2030","Paper","N","N","N","N","","High","IDEA","종이투표"),
    ("Bolivia","볼리비아","BOL","Americas","Y","2025-08-17","2030","Paper","Y","N","Y","N","DIREPRE(자체)","High","TSE Bolivia","종이+DIREPRE 전자결과전송. Carter Center 보고서"),
    ("Brazil","브라질","BRA","Americas","Y","2022-10-30","2026-10-04","DRE","Y","N","Y","Y","TSE(자체개발)","High","TSE Brazil","전국 DRE 1996년 도입. 1.4억 유권자"),
    ("Canada","캐나다","CAN","Americas","Y","2025-04-28","2029","Paper","N","N","Y","N","Elections Canada 자체","High","Elections Canada","종이투표+전자집계"),
    ("Chile","칠레","CHL","Americas","Y","2025-11-16","2029","Paper","Y","N","Y","N","","High","SERVEL","종이투표"),
    ("Colombia","콜롬비아","COL","Americas","Y","2022-05-29","2026","Paper","Y","N","Y","N","IDEMIA(등록)","High","CNE Colombia","종이투표. IDEMIA AFIS/ABIS 독점수의계약"),
    ("Costa Rica","코스타리카","CRI","Americas","Y","2022-02-06","2026","Paper","Y","N","Y","N","","High","TSE Costa Rica","종이투표"),
    ("Cuba","쿠바","CUB","Americas","Limited","2023-03-26","2028","Paper","N","N","N","N","","High","IDEA","일당제. 형식적 선거"),
    ("Dominica","도미니카","DMA","Americas","Y","2022-12-06","2027","Paper","N","N","N","N","","High","IDEA","소규모"),
    ("Dominican Republic","도미니카공화국","DOM","Americas","Y","2024-05-19","2028","OMR","Y","Y","Y","N","JCE(자체)+생체cédula","High","JCE","OMR 전국도입. 생체cédula 9.4M장"),
    ("Ecuador","에콰도르","ECU","Americas","Y","2025-04-13","2029","Paper","Y","N","Y","N","CNE 자체","High","CNE Ecuador","종이+전자결과전송. EU EOM 확인"),
    ("El Salvador","엘살바도르","SLV","Americas","Y","2024-02-04","2027","Mixed","Y","Y","Y","N","TSE SV","High","TSE El Salvador","생체DUI 인증+전자결과전송"),
    ("Grenada","그레나다","GRD","Americas","Y","2022-06-23","2027","Paper","N","N","N","N","","High","IDEA","소규모"),
    ("Guatemala","과테말라","GTM","Americas","Y","2023-06-25","2027","Paper","Y","N","Y","N","TSE Guatemala","High","TSE Guatemala","종이+전자결과전송"),
    ("Guyana","가이아나","GUY","Americas","Y","2025-09-01","2030","Paper","Y","N","Y","N","GECOM","High","GECOM","생체BVR+전자결과전송"),
    ("Haiti","아이티","HTI","Americas","Limited","2016-11-20","","Paper","N","N","N","N","","High","IDEA","2016 이후 선거 공백. 치안불안"),
    ("Honduras","온두라스","HND","Americas","Y","2021-11-28","2025","Mixed","Y","Y","Y","N","Smartmatic VIU 2만대","High","TSE Honduras","Smartmatic VIU 생체인증+결과전송. 2025 시스템 다운 사고"),
    ("Jamaica","자메이카","JAM","Americas","Y","2025-03-10","2030","Mixed","Y","Y","Y","N","EVIS e-pollbook","High","EOJ Jamaica","EVIS 생체e-pollbook 7→63개 선거구 확대 조달"),
    ("Mexico","멕시코","MEX","Americas","Y","2024-06-02","2027","Paper","Y","N","N","N","INE+TGM(국영인쇄)","High","INE Mexico","TGM 국영 투표용지인쇄. 3.17억장 MXN 427.4M"),
    ("Nicaragua","니카라과","NIC","Americas","Limited","2021-11-07","2026","Paper","N","N","N","N","","High","IDEA","오르테가 독재. 형식적 선거"),
    ("Panama","파나마","PAN","Americas","Y","2024-05-05","2029","Mixed","Y","N","Y","N","TE Panama","High","TE Panama","종이+전자집계"),
    ("Paraguay","파라과이","PRY","Americas","Y","2023-04-30","2028","DRE","Y","N","Y","Y","TSJE+브라질기기","High","TSJE","전국 DRE(브라질기기+TSJE SW)+생체인증재추진"),
    ("Peru","페루","PER","Americas","Y","2021-06-06","2026","Paper","Y","N","Y","N","ONPE+RENIEC","High","ONPE","종이+전자집계. Corporación Gráfica Navarrete 용지인쇄"),
    ("Saint Kitts and Nevis","세인트키츠네비스","KNA","Americas","Y","2022-08-05","2027","Paper","N","N","N","N","","High","IDEA","소규모"),
    ("Saint Lucia","세인트루시아","LCA","Americas","Y","2021-07-26","2026","Paper","N","N","N","N","","High","IDEA","소규모"),
    ("Saint Vincent and the Grenadines","세인트빈센트그레나딘","VCT","Americas","Y","2020-11-05","2025","Paper","N","N","N","N","","High","IDEA","소규모"),
    ("Suriname","수리남","SUR","Americas","Y","2025-05-25","2030","Paper","N","N","Y","N","","High","IDEA","종이투표"),
    ("Trinidad and Tobago","트리니다드토바고","TTO","Americas","Y","2025-08-25","2030","Paper","N","N","N","N","","High","EBC TTobago","종이투표"),
    ("United States","미국","USA","Americas","Y","2024-11-05","2028","Mixed","N","N","Y","N","ES&S/Dominion/Hart(주별)","High","EAC USA","주별 상이(OMR/DRE/BMD/Paper). 연방 통일 없음"),
    ("Uruguay","우루과이","URY","Americas","Y","2024-11-24","2029","Paper","Y","N","Y","N","","High","Corte Electoral","종이+전자집계. 투명한 민주주의"),
    ("Venezuela","베네수엘라","VEN","Americas","Limited","2024-07-28","2030","DRE","Y","N","Y","Y","CNE(자체)","High","CNE Venezuela","전국 DRE. Smartmatic→CNE 자체운영. 2024 선거 조작 의혹"),
]

# 중복 제거 (Tunisia, Turkey, Kazakhstan, Kyrgyzstan, Tajikistan, Turkmenistan, Uzbekistan, Afghanistan, Pakistan은 두 지역에 걸침)
# 지역이 다른 중복 행 제거
seen = set()
deduped = []
for row in DATA:
    key = row[2]  # iso3
    if key not in seen:
        seen.add(key)
        deduped.append(row)
    # Tunisia는 Middle East에서만 유지 (Africa 중복 제거)
    # Turkey는 Middle East에서만 유지
    # 중앙아시아 국가들은 Central Asia에서만 유지

# 실제로는 지역별로 분리해서 저장하고 싶으므로 중복 허용
# (키르기스스탄 등은 "Central Asia"와 "Asia-Pacific" 두 개가 있을 수 있음)

def build_db(data):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS countries")
    conn.executescript(SCHEMA)

    conn.executemany("""
        INSERT INTO countries
        (country, country_ko, iso3, region, has_elections,
         last_election_date, next_election_date, voting_method,
         biometric_voter_reg, biometric_voter_verify, electronic_results_tx,
         evoting, vendor, confidence, source, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, data)

    conn.commit()

    # 통계
    total = conn.execute("SELECT COUNT(*) FROM countries").fetchone()[0]
    by_election = dict(conn.execute("SELECT has_elections, COUNT(*) FROM countries GROUP BY has_elections").fetchall())
    by_evoting = dict(conn.execute("SELECT evoting, COUNT(*) FROM countries GROUP BY evoting").fetchall())
    by_bvr = dict(conn.execute("SELECT biometric_voter_reg, COUNT(*) FROM countries GROUP BY biometric_voter_reg").fetchall())
    by_bvv = dict(conn.execute("SELECT biometric_voter_verify, COUNT(*) FROM countries GROUP BY biometric_voter_verify").fetchall())
    by_ert = dict(conn.execute("SELECT electronic_results_tx, COUNT(*) FROM countries GROUP BY electronic_results_tx").fetchall())
    by_method = dict(conn.execute("SELECT voting_method, COUNT(*) FROM countries GROUP BY voting_method ORDER BY 2 DESC").fetchall())
    miru_countries = conn.execute("SELECT country, region, notes FROM countries WHERE vendor LIKE '%Miru%'").fetchall()

    conn.close()
    return total, by_election, by_evoting, by_bvr, by_bvv, by_ert, by_method, miru_countries

def export_csv(data):
    fieldnames = ["country","country_ko","iso3","region","has_elections",
                  "last_election_date","next_election_date","voting_method",
                  "biometric_voter_reg","biometric_voter_verify","electronic_results_tx",
                  "evoting","vendor","confidence","source","notes"]
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(data)

if __name__ == "__main__":
    total, by_election, by_evoting, by_bvr, by_bvv, by_ert, by_method, miru_countries = build_db(DATA)
    export_csv(DATA)

    print(f"\n{'='*60}")
    print(f"전 세계 선거 기술 DB 구축 완료")
    print(f"{'='*60}")
    print(f"총 {total}개국 수록")
    print(f"\n[선거 실시 현황]")
    print(f"  민주적 정기선거 (Y):      {by_election.get('Y', 0)}개국")
    print(f"  제한적/형식적 (Limited):  {by_election.get('Limited', 0)}개국")
    print(f"  선거 없음 (N):           {by_election.get('N', 0)}개국")
    print(f"\n[투표 방식]")
    for method, cnt in sorted(by_method.items(), key=lambda x: -x[1]):
        print(f"  {method or '미분류'}: {cnt}개국")
    print(f"\n[기술 도입 현황]")
    print(f"  생체 유권자 등록 (Y):     {by_bvr.get('Y', 0)}개국")
    print(f"  투표소 생체 인증 (Y):     {by_bvv.get('Y', 0)}개국")
    print(f"  전자 결과 전송 (Y):       {by_ert.get('Y', 0)}개국")
    print(f"  전자투표기 사용 (Y):      {by_evoting.get('Y', 0)}개국")
    print(f"\n[Miru Systems 관련 국가]")
    for c, r, n in miru_countries:
        print(f"  {c} ({r}): {n[:60] if n else ''}...")
    print(f"\nDB: {DB_PATH}")
    print(f"CSV: {CSV_PATH}")
