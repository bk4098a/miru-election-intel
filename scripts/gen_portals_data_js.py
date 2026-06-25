"""Generate data/portals_data.js from the SQLite reference DB."""
import sys, io, sqlite3, json, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── ISO3 → ISO numeric map ────────────────────────────────────────────────────
ISO_NUM = {
    'ALB':'008','ARE':'784','ARG':'032','BEL':'056','BGR':'100','BHR':'048',
    'BIH':'070','BRA':'076','BTN':'064','CHE':'756','COD':'180','DOM':'214',
    'EST':'233','GEO':'268','GHA':'288','HND':'340','IND':'356','IRN':'364',
    'IRQ':'368','JAM':'388','KAZ':'398','KEN':'404','KGZ':'417','KOR':'410',
    'MKD':'807','MNG':'496','OMN':'512','PAN':'591','PHL':'608','PRY':'600',
    'SLV':'222','USA':'840','UZB':'860','VEN':'862','ZAF':'710',
}

# ── Vendor name → canonical short label ──────────────────────────────────────
VENDOR_PAT = [
    (r'Miru',       'Miru'),
    (r'Smartmatic', 'Smartmatic'),
    (r'Dominion',   'Dominion'),
    (r'ES&S|Election Systems',  'ES&S'),
    (r'Hart',       'Hart'),
    (r'Thales',     'Thales'),
    (r'Ciela Norma','Ciela Norma'),
    (r'Ren-Form',   'Ren-Form'),
    (r'Scytl',      'Scytl'),
    (r'Indra',      'Indra'),
]

def extract_vendors(vendor_name):
    if not vendor_name:
        return []
    found = []
    for pat, label in VENDOR_PAT:
        if re.search(pat, vendor_name, re.IGNORECASE) and label not in found:
            found.append(label)
    return found if found else []

# ── machine_type → method ─────────────────────────────────────────────────────
def normalize_method(machine_type, portal_voting_method='Mixed'):
    if not machine_type:
        return portal_voting_method or 'Mixed'
    mt = machine_type.upper()
    if 'OMR' in mt and ('BMD' in mt or 'DRE' in mt):
        return 'Mixed'
    if 'OMR' in mt: return 'OMR'
    if 'DRE' in mt: return 'DRE'
    if 'EVM' in mt: return 'EVM'
    if 'BMD' in mt: return 'DRE'      # BMD ≈ DRE family
    if 'INTERNET' in mt: return 'EVM' # closest
    return portal_voting_method or 'Mixed'

# ── DB query ──────────────────────────────────────────────────────────────────
db = sqlite3.connect('C:/Users/KIM/Downloads/miru-election-intel/data/election_technology_world.db')
db.row_factory = sqlite3.Row
cur = db.cursor()

# All portals
cur.execute('''SELECT p.*, c.machine_type, c.vendor_name
               FROM machine_voting_portals p
               LEFT JOIN countries c ON p.iso3 = c.iso3
               ORDER BY p.id''')
portals_raw = [dict(r) for r in cur.fetchall()]

# Analysis keyed by (iso3, portal_name)
cur.execute('SELECT * FROM portal_analysis')
analysis_raw = [dict(r) for r in cur.fetchall()]
analysis_map = {}
for a in analysis_raw:
    analysis_map[(a['iso3'], a['portal_name'])] = a

# ── Build MIRU_PORTALS ────────────────────────────────────────────────────────
portals_out = []
for p in portals_raw:
    iso3 = p['iso3']
    # Try to find matching analysis
    akey = (iso3, p['portal_name'])
    a = analysis_map.get(akey)
    if not a:
        # fuzzy: first analysis for this iso3
        candidates = [v for k, v in analysis_map.items() if k[0] == iso3]
        a = candidates[0] if candidates else {}

    vendors = extract_vendors(p.get('vendor_name') or '')
    is_miru = 'Miru' in vendors

    portals_out.append({
        'id':           p['id'],
        'country':      p['country'],
        'country_ko':   p['country_ko'],
        'iso3':         iso3,
        'region':       p['region'],
        'name':         p['portal_name'],
        'url':          p['url'],
        'portal_type':  p['portal_type'] or '포털',
        'lang':         p['language'] or '',
        'crawl_id':     p['crawl_id'] or '',
        'priority':     p['priority'] or 'Low',
        'notes':        p['notes'] or '',
        'isMiru':       is_miru,
        'vendors':      vendors,
        'feasibility':  a.get('sql_feasibility') or '',
        'site_type':    a.get('site_type') or '',
        'crawl_method': a.get('crawl_method') or '',
        'api_endpoint': a.get('api_endpoint') or '',
    })

# ── Build MIRU_COUNTRIES ──────────────────────────────────────────────────────
# Group portals by iso3
from collections import defaultdict
by_iso = defaultdict(list)
for p in portals_out:
    by_iso[p['iso3']].append(p)

countries_out = []
for iso3, ps in sorted(by_iso.items()):
    first = ps[0]
    # Get country info
    cur.execute('SELECT * FROM countries WHERE iso3=?', (iso3,))
    c_row = cur.fetchone()
    c = dict(c_row) if c_row else {}

    # Determine method from DB or portals
    mt = c.get('machine_type')
    pm = ps[0].get('portal_type', '')   # not the method
    pm_voting = first.get('portal_type') # actually need from portals.voting_method
    # Get voting_method from portals table directly
    cur.execute('SELECT DISTINCT voting_method FROM machine_voting_portals WHERE iso3=?', (iso3,))
    vmethods = [r[0] for r in cur.fetchall() if r[0]]
    portal_vm = vmethods[0] if len(vmethods)==1 else ('Mixed' if len(vmethods)>1 else 'Mixed')

    method = normalize_method(mt, portal_vm)
    vendors = extract_vendors(c.get('vendor_name') or '')
    is_miru = 'Miru' in vendors

    countries_out.append({
        'country':    first['country'],
        'country_ko': first['country_ko'],
        'iso3':       iso3,
        'iso_num':    ISO_NUM.get(iso3, ''),
        'region':     first['region'],
        'method':     method,
        'vendors':    vendors,
        'isMiru':     is_miru,
        'count':      len(ps),
        'portals':    [p['id'] for p in ps],
    })

# ── Build MIRU_ANALYSIS_STATS ─────────────────────────────────────────────────
total = len(portals_out)
miru_countries = sum(1 for c in countries_out if c['isMiru'])
high_prio = sum(1 for p in portals_out if p['priority']=='High')
high_feas = sum(1 for p in portals_out if p['feasibility']=='High')
by_region = defaultdict(int)
for p in portals_out:
    by_region[p['region']] += 1

cur.execute('SELECT priority, COUNT(*) FROM portal_analysis GROUP BY priority')
prio_raw = dict(cur.fetchall())

stats_out = {
    'total_portals': total,
    'total_countries': len(countries_out),
    'miru_countries': miru_countries,
    'high_priority': high_prio,
    'crawlable_high': high_feas,
    'priority': {k: int(v) for k, v in prio_raw.items()},
    'by_region': dict(by_region),
}

# ── Vendor Intel data (from generate_intel_report.py) ────────────────────────
B_red    = '#EB0513'
B_steel  = '#8A94A6'
B_accent2= '#C0C6D0'

VENDOR_DATA = [
    {'slug':'smartmatic','name':'Smartmatic','flag':'🇬🇧','hq':'London, UK','homepage':'https://www.smartmatic.com','type':'Private','founded':'2000','employees':'~600','revenue':'~$175M','countries_count':24,'key_products':['bSmart BMD 100/155','SAES-1800plus VCM','EMS/EMP Platform','TIVI Internet Voting','VIU-500 Biometric Kit'],'categories':['BMD','DRE','OMR','Biometric','Internet','EMS'],'overlap':'Indirect','overlap_markets':['PHL'],'strengths':['35+개국 65억 표 처리 — 세계 최대 선거기술 풋프린트','BMD·OMR·생체인식·인터넷투표 엔드투엔드 포트폴리오','VVSG 2.0 최초 제출 — EAC 인증 공신력'],'weaknesses':['SGO Corporation 형사기소(FCPA, 2025.10) — 필리핀 뇌물 혐의, 기각신청 계류중','필리핀 시장 영구 상실 — COMELEC 2023 자격박탈 (Miru 2025 수주)','미국 시장 Dominion 비경쟁 조항으로 사실상 LA카운티 단독만 가능'],'news':'FCPA 기소(2025.10) 기각신청 계류 / Newsmax $40M 합의(2024) / Fox News 재판 2026년 예정','confidence':'High'},
    {'slug':'liberty_vote','name':'Liberty Vote (구 Dominion)','flag':'🇺🇸','hq':'Denver, CO, USA','homepage':'https://libertyvote.com','type':'Private','founded':'2003','employees':'~250','revenue':'~$100M','countries_count':2,'key_products':['ImageCast X BMD','ImageCast Precinct 2 OMR','Democracy Suite EMS','Frontier 1.0 (VVSG 2.0 제출중)'],'categories':['OMR','BMD','DRE','EMS'],'overlap':'None','overlap_markets':[],'strengths':['미국 등록유권자 25% 커버 — 27개 주 최대 설치기반','KNOWiNK 인수로 e-pollbook 포함 40개 주 통합 플랫폼','Frontier 1.0 VVSG 2.0 EAC 제출(2025.11)'],'weaknesses':['2020 음모론 $787.5M 합의 이후 브랜드 독성 여전','국제시장 사실상 전무 — 필리핀 2025 응찰조차 못 함','리브랜딩 후 신규계약 아직 없음'],'news':'2025.10 Dominion → Liberty Vote 리브랜딩 / 2025.11 Frontier 1.0 EAC VVSG 2.0 제출','confidence':'High'},
    {'slug':'ess','name':'ES&S (Election Systems & Software)','flag':'🇺🇸','hq':'Omaha, NE, USA','homepage':'https://www.essvote.com','type':'Private','founded':'1979','employees':'~700','revenue':'~$120M','countries_count':6,'key_products':['DS300/450/950 OMR 스캐너','ExpressVote BMD','ExpressVote XL','EVS 7.0 (VVSG 2.0 인증 2026.3)'],'categories':['OMR','BMD','DRE','e-Pollbook','EMS'],'overlap':'Indirect','overlap_markets':['PHL'],'strengths':['미국 시장 점유율 50~60% — 42개 주 4,500개 지자체','투표등록·e-pollbook·OMR·BMD·개표 풀스택 번들','EVS 7.0 VVSG 2.0 EAC 인증(2026.3) — 최신 표준 최초 인증'],'weaknesses':['보안 취약점 지속 — 원격접속 프리인스톨(2018), 중국산 부품 우려','텍사스 e-pollbook 인증 취소(2024.12) — 댈러스 오인쇄 사고','보안 연구자 소송 — 독립감사 저해'],'news':'2024.12 텍사스 e-pollbook 인증취소 / 2026.3 VVSG 2.0 인증 승인','confidence':'High'},
    {'slug':'hart','name':'Hart InterCivic','flag':'🇺🇸','hq':'Austin, TX, USA','homepage':'https://www.hartintercivic.com','type':'Private','founded':'1912','employees':'~100~150','revenue':'~$30~43M','countries_count':1,'key_products':['Verity Vanguard 1.0 (VVSG 2.0 최초 인증)','Vanguard Flex BMD','Vanguard Vault OMR'],'categories':['OMR','BMD','DRE','EMS'],'overlap':'None','overlap_markets':[],'strengths':['세계 최초 VVSG 2.0 EAC 인증(2025.7) — 규제 선점','바코드 없는 완전 사람이 읽을 수 있는 용지 — EO 14248 완전 준수','20개 주 100년+ 관계'],'weaknesses':['미국 단일 시장 — 국제 진출 없음','매출 $30~43M 소형사 — R&D 투자 한계','미국 시장 점유율 15%'],'news':'2025.7 Vanguard VVSG 2.0 최초 인증 / 2026.4 텍사스 6번째 주 인증','confidence':'High'},
    {'slug':'msa','name':'Grupo MSA / Comitia-MSA','flag':'🇦🇷','hq':'Buenos Aires, Argentina','homepage':'https://www.msa.com.ar','type':'Private','founded':'1995','employees':'~100+','revenue':'~$5.8M','countries_count':3,'key_products':['Vot.ar / BUE 전자투표용지','Scytl InVote Gov 인터넷투표','sVote (스위스 e-voting)'],'categories':['BMD','Internet','Software'],'overlap':'Indirect','overlap_markets':['ARG','PRY'],'strengths':['아르헨티나 BUE 시장 25년 지배 — CABA 등 11개 이상 주','2024.6 Scytl 인수로 1,000+ 미국 고객, 4개 대륙 IP 확보','RFID 칩+종이 혼합 BUE — ISO 9001 인증'],'weaknesses':['기술 장애 반복 — 2023 CABA PASO 판사 판정','단독입찰 반복 패턴 — 파라과이 2025 불법시비 논란','파라과이 $35M 단독낙찰 논란'],'news':'2024.6 Scytl 인수 / 2025.5 CABA $22M 단독입찰 / 2025.12 파라과이 $35M 단독낙찰 논란','confidence':'High'},
    {'slug':'scytl','name':'Scytl / Civica Election Services','flag':'🇪🇸','hq':'Barcelona / London','homepage':'https://www.scytl.com','type':'Subsidiary','founded':'2001','employees':'~125+200','revenue':'~$44M+$35M','countries_count':30,'key_products':['Invote Gov 인터넷투표','SOE Software ENR','CESvotes 온라인투표(Civica)'],'categories':['Internet','Software'],'overlap':'Indirect','overlap_markets':['ARE','PRY'],'strengths':['암호화 인터넷투표 50+ 특허, 25년 R&D 선점','SOE Software — 미국 24개 주 1,300개 선거구 ENR','UAE FNC 4연속(2006~) — 세계 최초 100% 디지털 국가선거'],'weaknesses':['노르웨이·호주 인터넷투표 취약점으로 계약 상실','2020년 파산(채무 €75M) — 2번의 소유권 변경','유럽·미국 인터넷투표 감사가능성 반대 여론'],'news':'2024.6 COMITIA MSA에 인수 / 2025.12 파라과이 $35M 계약','confidence':'Med'},
    {'slug':'positivo','name':'Positivo Tecnologia','flag':'🇧🇷','hq':'Curitiba, Brazil','homepage':'https://www.positivotecnologia.com.br/en/','type':'Public','founded':'1989','employees':'~8,400','revenue':'~$700M','countries_count':1,'key_products':['UE2022 DRE 투표기','UE2020 DRE','생체인식 리더 HID DP5360'],'categories':['DRE','EVM','Biometric'],'overlap':'None','overlap_markets':[],'strengths':['브라질 TSE 유일 DRE 제조사 — 2020 이후 독점','국내 공장 수직통합 — 가격경쟁력 + 국가안보 조달 우선','TSE 공동개발 파트너십'],'weaknesses':['브라질 단일 시장 — 국제 수출 없음','순이익 R$85M(2024)→R$12M(2025) 급감','DRE 외 제품(OMR·BMD·인터넷투표) 없음'],'news':'FY2025 매출 R$4.0B / 순이익 R$12M(86% 감소) / UE2026 신규입찰 미발표','confidence':'High'},
    {'slug':'bel_india','name':'BEL (Bharat Electronics Limited)','flag':'🇮🇳','hq':'Bengaluru, India','homepage':'https://bel-india.in','type':'State-owned','founded':'1954','employees':'~9,000~11,200','revenue':'~$3.3B','countries_count':7,'key_products':['EVM M3 Control Unit','EVM M3 Ballot Unit','VVPAT M3'],'categories':['EVM','DRE','VVPAT'],'overlap':'None','overlap_markets':[],'strengths':['인도 9억 유권자 선거 EVM 독점 공급','국방부 산하 Navratna PSU — 진입장벽 극히 높음','나미비아·부탄·피지 등 외교 채널 수출'],'weaknesses':['EVM 보안 투명성 비판 — 소프트웨어 감사보고서 공개 거부','선거기술은 전체 매출 소수 — R&D·수출 인프라 취약','국제 수출 전체 매출의 0.5% 미만'],'news':'FY2026 매출 ~$3.3B 신기록 / 수출 33.65% 증가 $141.9M — 방산 위주','confidence':'Med'},
    {'slug':'ecil','name':'ECIL (Electronics Corporation of India)','flag':'🇮🇳','hq':'Hyderabad, India','homepage':'https://www.ecil.co.in','type':'State-owned','founded':'1967','employees':'~3,000~5,000','revenue':'~$290M','countries_count':4,'key_products':['M3-EVM','VVPAT','S3-EVM (2025년 공개)'],'categories':['EVM','DRE','Software'],'overlap':'None','overlap_markets':[],'strengths':['BEL과 50:50 인도 ECI 공급 독점','EMS 2.0 클라우드 네이티브 + SMF 2.0 보안제조 소프트웨어','Miniratna Category-I 지위 부여(2025.5)'],'weaknesses':['해외수출 인도-G2G 외교 채널 의존','EVM 기술 특수 목적 설계 — OMR/BMD 국제 입찰 미적용','S3-EVM 공개(2025.3) 외 국제 시장 진출 계획 없음'],'news':'2025.3 S3-EVM 공개 / 2025.5 Miniratna Category-I 승격','confidence':'Med'},
    {'slug':'swiss_post','name':'Swiss Post e-voting','flag':'🇨🇭','hq':'Bern, Switzerland','homepage':'https://swisspost-digital.ch/en/solutions/e-voting','type':'State-owned','founded':'2014','employees':'~45(e-voting팀)','revenue':'그룹 ~$8.5B','countries_count':1,'key_products':['sVote 인터넷투표 시스템','Universal Verifiability 검증SW'],'categories':['Internet'],'overlap':'None','overlap_markets':[],'strengths':['완전 오픈소스 공개 — 수학적 검증 가능 유일 국가급 시스템','범용 검증가능성 최초 운용','스위스 연방 소유 — 상업 압력 없음'],'weaknesses':['스위스 단일 시장 — 4/26개 캔톤만 활성화','2019~2023 중단 이력(암호화 결함)','인터넷투표 전용 — OMR·EVM·BMD·생체인식 없음'],'news':'2025.6 연방 기본라이선스 4개 캔톤 2027까지 갱신','confidence':'High'},
    {'slug':'cybernetica','name':'Cybernetica AS','flag':'🇪🇪','hq':'Tallinn, Estonia','homepage':'https://cyber.ee','type':'Private','founded':'1997','employees':'~230','revenue':'~$16M','countries_count':1,'key_products':['IVXV 인터넷투표 시스템','m-Voting 모바일(2025 파일럿)'],'categories':['Internet','Software'],'overlap':'None','overlap_markets':[],'strengths':['20년 유일한 법적 구속력 국가 인터넷투표 운영(2023년 51%)','IVXV 오픈소스 투명성','40개국 UXP/X-Road 생태계'],'weaknesses':['에스토니아 단일 국제 운용','~230명 소형사','2024 EP선거 첫 오류 발생'],'news':'2025.5 m-Voting iOS/Android 파일럿 / 2025.11 양자내성암호 전환 3개 계약','confidence':'High'},
    {'slug':'idemia','name':'IDEMIA (→ IN Groupe / Amadeus)','flag':'🇫🇷','hq':'Courbevoie, France','homepage':'https://www.idemia.com','type':'Private','founded':'2017','employees':'~15,000','revenue':'~$3.1B','countries_count':9,'key_products':['MorphoTablet 2S 생체인식 태블릿','KIEMS(케냐 통합선거관리)','RAVEC(말리 시민ID)'],'categories':['Biometric','Software','BVR'],'overlap':'Indirect','overlap_markets':['KEN','GHA','COD'],'strengths':['아프리카 35개국+ 생체선거기술 — 최대 아프리카 풋프린트','NIST 지문 전 벤치마크 1위(2025.3)','ID스크린 태블릿 17만대+ 배포'],'weaknesses':['케냐 IEBC 지식이전 거부 비판 / 2017 KIEMS 실패','프랑스 검찰 뇌물수사 진행중(2022~)','분사 진행 — 사업 불확실성'],'news':'2025.7 Smart Identity 부문 IN Groupe에 ~€1B 매각 / 2026.4 IPS 부문 Amadeus €1.2B 발표','confidence':'High'},
    {'slug':'thales','name':'Thales Group (DIS / 구 Gemalto)','flag':'🇫🇷','hq':'La Défense, Paris, France','homepage':'https://www.thalesgroup.com','type':'Public','founded':'1893','employees':'~85,000','revenue':'~$24B','countries_count':15,'key_products':['Thales Election Suite','Coesys Mobile Enrollment Station','DactyScan84c 생체인식 스캐너'],'categories':['Biometric','Software'],'overlap':'Indirect','overlap_markets':['COD','GHA','PHL'],'strengths':['15개국+ 생체선거 배포 — 세계 최대 생체선거 벤더','20년+ Gemalto 유산으로 프랑코폰 아프리카 깊은 관계','€22B 그룹 규모 — 여권·국민ID→유권자등록 크로스셀'],'weaknesses':['Gemalto 자회사 프랑스 사법조사(2022~) — 카메룬·DRC 뇌물 혐의','투표기계(OMR·EVM·BMD) 없음','방산·항공·사이버 등 전방위 대기업 — 선거기술 집중도 낮음'],'news':'FY2025 €22.1B 매출 신기록 / Gemalto 프랑스 사법조사 지속','confidence':'High'},
    {'slug':'laxton','name':'Laxton Group (→ DNP 자회사)','flag':'🇳🇱','hq':'The Hague, Netherlands','homepage':'https://www.laxton.com','type':'Subsidiary','founded':'2004','employees':'~201','revenue':'~$35M','countries_count':14,'key_products':['Chameleon D 다중생체인식 태블릿','BRK 생체인식 등록 키트','Athena 신원관리 플랫폼'],'categories':['Biometric','Software'],'overlap':'Indirect','overlap_markets':['GHA','TZA'],'strengths':['20년+ 50개국 3억명+ 생체등록','하드웨어+소프트웨어 자체 설계/제조','DNP 인수($9.5B 부모사) + MOSIP SI 인증(2026.3)'],'weaknesses':['투표집계 기계(OMR·EVM·BMD) 없음','라이베리아 계약 논란(2022~2023 2회 거부 후 낙찰)','DNP 인수 전 $35M 소형사'],'news':'2025.6 DNP 75% 지분 인수 / 2026.3 MOSIP SI 파트너 인증','confidence':'High'},
    {'slug':'innovatrics','name':'Innovatrics','flag':'🇸🇰','hq':'Bratislava, Slovakia','homepage':'https://www.innovatrics.com','type':'Private','founded':'2004','employees':'~210','revenue':'~$18M','countries_count':7,'key_products':['Innovatrics ABIS 자동생체식별','Voter Management Platform','SmartFace 안면인식'],'categories':['Biometric','ABIS','Software'],'overlap':'Indirect','overlap_markets':['ALB'],'strengths':['NIST ELFT 잠재지문 정확도 1위(2025.1)','하드웨어 무관 클라우드 ABIS — 1억 인구 단일 AWS','MOSIP 컴플라이언트 ABIS(2026.6) — 29개국 GovStack'],'weaknesses':['소프트웨어/생체인식 전용 — Smartmatic 등에 납품 구조','~210명 소형사','투표기계 없음 — 고부가 하드웨어 계약 참여 불가'],'news':'2025.1 NIST 지문 1위 탈환 / 2026.5 UIDAI 안면인식 챌린지 1위','confidence':'Med'},
    {'slug':'tech5','name':'uqudo / TECH5','flag':'🇨🇭','hq':'Geneva / Manchester','homepage':'https://tech5.ai','type':'Private','founded':'2018','employees':'~120','revenue':'비공개','countries_count':1,'key_products':['Antakhib/Intakhib 모바일 생체인증 선거앱','T5-OmniMatch ABIS'],'categories':['Biometric','Internet','Software'],'overlap':'Indirect','overlap_markets':['OMN'],'strengths':['NIST 최상위 생체인식 알고리즘','오만 2022/2023 국가선거 NFC+생체 원격투표 실증 — 유일 벤더','창업자 Aadhaar(13억)/인도네시아 국민ID(1.93억) 경력'],'weaknesses':['선거 레퍼런스 오만 단일','~120명 소형사','법집행·DPI가 주 사업 — 선거기술 2차적'],'news':'2026.1 Salica Investments 성장대출 확보 / 이라크 거주자 ID 지원(2025.8)','confidence':'Med'},
    {'slug':'champtek','name':'Champtek Inc.','flag':'🇹🇼','hq':'New Taipei City, Taiwan','homepage':'https://www.champtek.com','type':'Private','founded':'1985','employees':'11~50','revenue':'비공개','countries_count':1,'key_products':['X-100 10.1인치 VMD(유권자관리단말)','Z Series 생체키트'],'categories':['Biometric','OMR','Software'],'overlap':'Indirect','overlap_markets':['ZAF'],'strengths':['하드웨어 전용 제조 — 모듈식 생체인식 통합','CHAMPTEK·SCANTECH ID 이중 브랜드 30개국+ 유통망','FBI 인증 지문, AFIS/ABIS 지원'],'weaknesses':['남아공 IEC X-100 VMD 2021·2024 선거 모두 현장 중단','11~50명 극소형사','Ren-Form 유통사 의존'],'news':'2026.6 Computex 타이페이 / 남아공 IEC 재입찰 결정 미발표','confidence':'Med'},
    {'slug':'samsung_sds','name':'Samsung SDS','flag':'🇰🇷','hq':'Seoul, South Korea','homepage':'https://www.samsungsds.com/en/index.html','type':'Public','founded':'1985','employees':'~26,000','revenue':'~$10.1B','countries_count':0,'key_products':['Nexsign 생체인증','Nexledger 블록체인','FabriX 생성AI'],'categories':['Software','Biometric'],'overlap':'None','overlap_markets':[],'strengths':['삼성그룹 브랜드 + 계열사 안정 수요','AI·클라우드 풀스택(SCP·FabriX·Brity Works)','방글라데시 NID 기반 선거인 확인 레퍼런스'],'weaknesses':['삼성 계열사 매출 의존도','선거기술 전용 포트폴리오 없음','아태 외 국제 브랜드 인지도 낮음'],'news':'2026.4 KKR KRW 1.22조(~$820M) 전환사채 투자 / FY2025 매출 KRW 13.93조','confidence':'High'},
    {'slug':'sopra_steria','name':'Sopra Steria','flag':'🇫🇷','hq':'Paris, France','homepage':'https://www.soprasteria.com','type':'Public','founded':'2014','employees':'~51,000','revenue':'~$6.0B','countries_count':1,'key_products':['EU Shared Biometric Matching System(sBMS)','FAED V3 프랑스 형사지문DB'],'categories':['Software','Biometric'],'overlap':'None','overlap_markets':[],'strengths':['유럽 공공기관 IT 톱5 — 프랑스·영국·EU 기관 깊은 관계','EU 국경 생체인식(SIS II·sBMS) 계약','유럽 디지털 주권 포지셔닝 — ESTIA 클라우드 연합'],'weaknesses':['선거기술 전용 제품 없음','EDPS 감사(2025): SIS II 수천개 고심각도 취약점','프랑스 43%·영국 16% 매출 집중'],'news':'Q1 2026 매출 +3.4% 반등 / sBMS 2025.8 eu-LISA와 가동','confidence':'High'},
]

CONTRACT_DATA = {
    'PRY':{'tier':'CRITICAL','next_tender':'2027','contract_end':'2026','contract_type':'lease','notes':'Comitia-MSA 임대 계약 10월 종료 → 2028 총선 입찰 예정. MSA 단독낙찰 논란으로 재입찰 가능성.'},
    'ARG':{'tier':'CRITICAL','next_tender':'2027','contract_end':'2025','contract_type':'service','notes':'CABA 선거별 서비스 계약(MSA 단독입찰 ~$22M) → 2027 재입찰.'},
    'ARE':{'tier':'CRITICAL','next_tender':'2026-2027','contract_end':'2023','contract_type':'service','notes':'FNC 선거별 계약 (Scytl 4연속) → 2027 FNC 선거 입찰 2026년 개시.'},
    'OMN':{'tier':'CRITICAL','next_tender':'2026-2027','contract_end':'unknown','contract_type':'service','notes':'Shura 4년 주기 → 2027 선거 입찰 예상. Iraq 생체카메라 레퍼런스 활용 가능.'},
    'PHL':{'tier':'WATCH','next_tender':'2027','contract_end':'2025','contract_type':'lease','notes':'Miru P17.99B 임대 완료 → COMELEC 2028 ACM 입찰 2027년 예정 (4월 기술전시회 완료).'},
    'BEL':{'tier':'WATCH','next_tender':'2026-2027','contract_end':'2027','contract_type':'service','notes':'Smartmatic 15년 계약(2012) 만료 예정 → 2029 선거용 재입찰. EU 조달법 적용.'},
    'BGR':{'tier':'WATCH','next_tender':'2026-2027','contract_end':'2024','contract_type':'purchase','notes':'소프트웨어 보증 만료 → Ciela Norma 단독계약 대체 입법 논의중.'},
    'CHE':{'tier':'WATCH','next_tender':'2027-2028','contract_end':'2027','contract_type':'pilot','notes':'Swiss Post 연방 라이선스 2027년 6월 만료 → 재심사. 경쟁입찰 없음.'},
    'BRA':{'tier':'WATCH','next_tender':'2027','contract_end':'owned/ongoing','contract_type':'purchase','notes':'UE2028 공청회 진행중(2026.6) → 2027 공식 입찰. 22만대 규모. 국내 JV 필요.'},
    'GEO':{'tier':'MONITOR','next_tender':'2027-2028','contract_end':'owned/ongoing','contract_type':'purchase','notes':'선거별 Smartmatic 조달(2025 $2.3M 추가) → 2028 의회선거 입찰.'},
    'ALB':{'tier':'MONITOR','next_tender':'2027-2029','contract_end':'owned/ongoing','contract_type':'purchase','notes':'EU 자금 $20M EVM 파일럿 → 전국 확대 미결정. 2027 지방/2029 의회.'},
    'MNG':{'tier':'MONITOR','next_tender':'2026-2028','contract_end':'owned/ongoing','contract_type':'purchase','notes':'2012년 Dominion 장비 14년 경과 → Liberty Vote 브랜드 변경이 진입 기회.'},
    'KOR':{'tier':'MONITOR','next_tender':'2027-2030','contract_end':'owned/ongoing','contract_type':'purchase','notes':'10년 주기 교체 (2013→2022) → 다음 교체 2027-2030. KRW 32.5B 규모.'},
    'COD':{'tier':'MONITOR','next_tender':'2027-2028','contract_end':'owned/ongoing','contract_type':'purchase','notes':'Miru $250M+ 장비 보유 → 2028 총선 교체/추가 조달. AS 계약 진행중.'},
    'IRQ':{'tier':'MONITOR','next_tender':'2028-2029','contract_end':'owned/ongoing','contract_type':'purchase','notes':'Miru ~$135M 장비 보유 → 2025년 생체카메라 추가. 10년 주기 2028-2029.'},
    'ZAF':{'tier':'MONITOR','next_tender':'2027-2030','contract_end':'owned/ongoing','contract_type':'purchase','notes':'VMD 2024 선거 오작동 → 교체 압박. DRE 도입 Green Paper 2026 결정 예정.'},
    'KGZ':{'tier':'MONITOR','next_tender':'2028-2030','contract_end':'owned/ongoing','contract_type':'purchase','notes':'Miru KOICA 자금 PCOS 5-in-1 → 2025 선거 재사용. 10년 수명 2028-2030.'},
    'BIH':{'tier':'LONG','next_tender':'2029-2030','contract_end':'2030','contract_type':'purchase','notes':'2026년 체결 4년 계약 74.5M BAM(38M EUR) → 2030 만료.'},
    'IND':{'tier':'LONG','next_tender':'2027-2030','contract_end':'owned/ongoing','contract_type':'purchase','notes':'국영제조사(BEL/ECIL) 직발주 → 민간입찰 없음. M3A 도입중.'},
    'BTN':{'tier':'LONG','next_tender':'2027-2028','contract_end':'owned/ongoing','contract_type':'purchase','notes':'2008/2013 BEL/ECIL 장비 18년 경과 → 2028 선거 전 교체. 인도 재조달 예상.'},
    'EST':{'tier':'LONG','next_tender':'unknown','contract_end':'owned/ongoing','contract_type':'service','notes':'국가직영 오픈소스 i-Voting → Miru 진입 불가.'},
    'USA':{'tier':'LONG','next_tender':'2027-2030','contract_end':'owned/ongoing','contract_type':'purchase','notes':'카운티별 10년 교체 물결 2027-2030. GA Dominion(Liberty Vote) 2029 만료.'},
    'VEN':{'tier':'LONG','next_tender':'2030-2031','contract_end':'owned/ongoing','contract_type':'purchase','notes':'OFAC 제재 ExClé 운영 → 불투명 조달. 다음 대선 2031.'},
    'IRN':{'tier':'UNKNOWN','next_tender':'unknown','contract_end':'unknown','contract_type':'pilot','notes':'소규모 파일럿 (4-8개 선거구) → 제재 환경. 진입 불가.'},
    'UZB':{'tier':'UNKNOWN','next_tender':'2027-2028','contract_end':'unknown','contract_type':'pilot','notes':'37대 파일럿(2024) → 2029 의회선거 전 본격 입찰 예상 2027-2028.'},
}

TIER_META_DATA = {
    'CRITICAL': {'color':'#EB0513','label':'즉시 대응','icon':'🔴'},
    'WATCH':    {'color':'#D4870A','label':'제안 준비','icon':'🟠'},
    'MONITOR':  {'color':'#4d9fff','label':'모니터링','icon':'🔵'},
    'LONG':     {'color':'#8A94A6','label':'장기 관찰','icon':'⚫'},
    'UNKNOWN':  {'color':'#C0C6D0','label':'정보 부족','icon':'⬜'},
}

# ── Write portals_data.js ─────────────────────────────────────────────────────
out = io.open('C:/Users/KIM/Downloads/miru-election-intel/data/portals_data.js', 'w', encoding='utf-8')
out.write('// Auto-generated from election_technology_world.db — do not edit manually.\n')
out.write('// Run: python scripts/gen_portals_data_js.py\n\n')
out.write('window.MIRU_PORTALS = ')
out.write(json.dumps(portals_out, ensure_ascii=False, indent=2))
out.write(';\n\n')
out.write('window.MIRU_COUNTRIES = ')
out.write(json.dumps(countries_out, ensure_ascii=False, indent=2))
out.write(';\n\n')
out.write('window.MIRU_ANALYSIS_STATS = ')
out.write(json.dumps(stats_out, ensure_ascii=False, indent=2))
out.write(';\n\n')
out.write('window.MIRU_VENDOR_DATA = ')
out.write(json.dumps(VENDOR_DATA, ensure_ascii=False, indent=2))
out.write(';\n\n')
out.write('window.MIRU_CONTRACT_DATA = ')
out.write(json.dumps(CONTRACT_DATA, ensure_ascii=False, indent=2))
out.write(';\n\n')
out.write('window.MIRU_TIER_META = ')
out.write(json.dumps(TIER_META_DATA, ensure_ascii=False, indent=2))
out.write(';\n')
out.close()

print(f'✅ portals_data.js generated: {total} portals, {len(countries_out)} countries, {miru_countries} Miru')
print(f'   + {len(VENDOR_DATA)} vendors, {len(CONTRACT_DATA)} contract records')
print('Countries:', sorted(by_iso.keys()))
