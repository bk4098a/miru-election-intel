"""
Generate data/election_tech_report.html
Multi-page tab-based dark-theme intelligence report for Miru Systems.
"""
import sqlite3, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

DB       = os.path.join(os.path.dirname(__file__), '..', 'data', 'election_technology_world.db')
OUT      = os.path.join(os.path.dirname(__file__), '..', 'data', 'election_tech_report.html')
CHARTJS  = os.path.join(os.path.dirname(__file__), '..', 'data', '_chartjs_cache.js')

# Inline Chart.js for fully self-contained HTML
_chartjs_src = ''
if os.path.exists(CHARTJS):
    with open(CHARTJS, encoding='utf-8') as _f:
        _chartjs_src = _f.read()
else:
    # Fallback to CDN if local cache missing
    _chartjs_src = None

# ── Procurement category overrides ─────────────────────────────────────────
PROCUREMENT_CATEGORY = {
    'BRA': 'both', 'PHL': 'both', 'ZAF': 'both', 'JAM': 'both', 'BTN': 'both',
    'IRQ': 'emb_only', 'KEN': 'emb_only',
    'KAZ': 'gov_only', 'USA': 'gov_only', 'ARG': 'gov_only', 'EST': 'gov_only',
    'COD': 'gov_only', 'BIH': 'gov_only', 'MNG': 'gov_only', 'OMN': 'gov_only',
    'ALB': 'gov_only', 'PRY': 'gov_only', 'KGZ': 'gov_only', 'BEL': 'gov_only',
    'CHE': 'gov_only', 'ARE': 'gov_only', 'IND': 'gov_only', 'BHR': 'gov_only',
    'UZB': 'gov_only', 'DOM': 'gov_only', 'SLV': 'gov_only', 'HND': 'gov_only',
    'BGR': 'gov_only', 'MKD': 'gov_only', 'PAN': 'gov_only',
    'GHA': 'login_req', 'IRN': 'login_req', 'KOR': 'login_req', 'GEO': 'login_req',
    'VEN': 'opaque',
}

CAT_META = {
    'both':      {'label': '국가조달 + 선관위 공동',  'label_en': 'National + EMB',    'color': '#22c55e', 'bg': '#052e16'},
    'emb_only':  {'label': '선관위 직접공고',          'label_en': 'EMB Direct Only',   'color': '#a78bfa', 'bg': '#2e1065'},
    'gov_only':  {'label': '국가조달 전용',            'label_en': 'National Only',     'color': '#38bdf8', 'bg': '#082f49'},
    'login_req': {'label': '로그인/등록 필요',         'label_en': 'Login Required',    'color': '#fb923c', 'bg': '#431407'},
    'opaque':    {'label': '수의계약/불투명',           'label_en': 'Opaque / Direct',   'color': '#94a3b8', 'bg': '#0f172a'},
}

REGIONS = {
    '아프리카':    ['COD', 'GHA', 'KEN', 'ZAF'],
    '아시아·중동': ['ARE', 'BHR', 'BTN', 'IND', 'IRN', 'IRQ', 'KAZ', 'KGZ', 'KOR', 'MNG', 'OMN', 'PHL', 'UZB'],
    '유럽·CIS':   ['ALB', 'BEL', 'BGR', 'BIH', 'CHE', 'EST', 'GEO', 'MKD'],
    '아메리카':   ['ARG', 'BRA', 'DOM', 'HND', 'JAM', 'PAN', 'PRY', 'SLV', 'USA', 'VEN'],
}

MIRU_ISO = {'PHL', 'KOR', 'KGZ', 'IRQ', 'COD'}

# ── Crawl / verification status ────────────────────────────────────────────────
# "포털이 존재한다" != "선거 관련 공고가 실제로 올라온다는 게 확인됐다"
CRAWL_STATUS = {
    # ✅ confirmed — 크롤러로 선거 관련 공고 실제 수집 완료
    'BHR': 'confirmed',   # bahrain.py ✅
    'KEN': 'confirmed',   # tenders_kenya.py ✅ 313건
    'IRQ': 'confirmed',   # ihec_iraq.py ✅
    'ZAF': 'confirmed',   # etenders_za.py ✅ IEC 공고 확인
    'PRY': 'confirmed',   # dncp_paraguay.py ✅
    'PHL': 'confirmed',   # philgeps.py ✅

    # 🔑 needs_key — 파서 완성, API 키만 있으면 즉시 수집 가능
    'KAZ': 'needs_key',   # goszakup.py → GOSZAKUP_TOKEN 필요
    'KOR': 'needs_key',   # g2b_korea.py → G2B_SERVICE_KEY 필요
    'USA': 'needs_key',   # samgov_usa.py → SAMGOV_API_KEY 필요

    # ⚠️ parser_unconfirmed — 파서 존재, 선거 공고 게재 여부 미확인
    'ARG': 'parser_unconfirmed',  # compr_ar.py — 테스트 필요
    'EST': 'parser_unconfirmed',  # riigihanked_est.py — API 401 폴백
    'GEO': 'parser_unconfirmed',  # spa_georgia.py — 등록 필요
    'OMN': 'parser_unconfirmed',  # tenderboard_omn.py — DNS 미확인
    'IND': 'parser_unconfirmed',  # cppp_india.py — 403/지역차단
    'COD': 'parser_unconfirmed',  # armp_drc.py — JSF 세션 필요
    'BIH': 'parser_unconfirmed',  # ejn_bosnia.py — Angular
    'MNG': 'parser_unconfirmed',  # gpa_mongolia.py — DNS 미확인
    'JAM': 'parser_unconfirmed',  # gojep.py — Playwright 필요
    'BRA': 'parser_unconfirmed',  # pncp.py — WAF/TLS 차단
    'KGZ': 'parser_unconfirmed',  # zakupki_kg.py — 미테스트
    'BTN': 'parser_unconfirmed',  # wp_portals.py — 타임아웃

    # 🔒 login_req — 로그인 없이 접근 불가 (procurement category와 동일)
    'GHA': 'login_req',   # GHANEPS 로그인 필요
    'IRN': 'login_req',   # 차단/로그인
    # KOR, GEO는 needs_key / parser_unconfirmed로 분류 (기술적 문제)

    # ❓ not_investigated — 파서 없음, 포털 상태 불명 (기본값)
}

CRAWL_STATUS_META = {
    'confirmed':          {'icon': '✅', 'label': '수집 확인',   'color': '#22c55e'},
    'needs_key':          {'icon': '🔑', 'label': 'API키 필요',  'color': '#38bdf8'},
    'parser_unconfirmed': {'icon': '⚠️', 'label': '파서 미확인', 'color': '#fb923c'},
    'login_req':          {'icon': '🔒', 'label': '로그인 필요', 'color': '#f87171'},
    'not_investigated':   {'icon': '❓', 'label': '미조사',       'color': '#6b7787'},
}

def get_crawl_status(iso):
    return CRAWL_STATUS.get(iso, 'not_investigated')

FLAG = {
    'COD':'🇨🇩','GHA':'🇬🇭','KEN':'🇰🇪','ZAF':'🇿🇦',
    'ARG':'🇦🇷','BRA':'🇧🇷','DOM':'🇩🇴','HND':'🇭🇳','JAM':'🇯🇲','PAN':'🇵🇦','PRY':'🇵🇾','SLV':'🇸🇻','USA':'🇺🇸','VEN':'🇻🇪',
    'BTN':'🇧🇹','IND':'🇮🇳','MNG':'🇲🇳','PHL':'🇵🇭','KOR':'🇰🇷','KAZ':'🇰🇿','KGZ':'🇰🇬','UZB':'🇺🇿',
    'ALB':'🇦🇱','BEL':'🇧🇪','BGR':'🇧🇬','BIH':'🇧🇦','CHE':'🇨🇭','EST':'🇪🇪','GEO':'🇬🇪','MKD':'🇲🇰',
    'ARE':'🇦🇪','BHR':'🇧🇭','IRN':'🇮🇷','IRQ':'🇮🇶','OMN':'🇴🇲',
}

# ── DB queries ──────────────────────────────────────────────────────────────
conn = sqlite3.connect(DB)
cur  = conn.cursor()

cur.execute("""
    SELECT iso3,country,country_ko,region,voting_method,machine_type,machine_model,
           vendor_name,biometric_voter_reg,biometric_voter_verify,evoting,
           contract_year,deployment_scale,notes,machine_voting
    FROM countries
    WHERE iso3 IN (SELECT DISTINCT iso3 FROM machine_voting_portals WHERE iso3!='ESP')
    ORDER BY region,country
""")
cols = ['iso3','country','country_ko','region','voting_method','machine_type','machine_model',
        'vendor','bio_reg','bio_verify','evoting','contract_year','deploy_scale','notes','machine_voting']
countries = [dict(zip(cols, r)) for r in cur.fetchall()]

cur.execute("""
    SELECT iso3,portal_type,portal_name,url,access,priority,notes,http_status
    FROM machine_voting_portals WHERE iso3!='ESP' ORDER BY iso3,portal_type
""")
portals_raw = cur.fetchall()
conn.close()

portals_by_iso = {}
for r in portals_raw:
    portals_by_iso.setdefault(r[0], []).append(
        {'type': r[1], 'name': r[2], 'url': r[3], 'access': r[4],
         'priority': r[5], 'notes': r[6], 'http': r[7]})

# ── Helpers ─────────────────────────────────────────────────────────────────
def get_cat(iso):
    return PROCUREMENT_CATEGORY.get(iso, 'gov_only')

def portal_status_html(p, iso):
    """Return colored status badge + optional note for a portal row."""
    http = (p.get('http') or '').strip()
    access = (p.get('access') or '').strip()
    # Special overrides
    if iso == 'KEN':
        return '<span class="ps-na">— Inaccessible</span>', '선관위 직접공고 확인됨'
    note = (p.get('notes') or '').replace('<','&lt;').replace('>','&gt;')
    # GHA EC Ghana note
    if iso == 'GHA' and 'EC Ghana' in (p.get('name') or ''):
        note = '공고 없음 (직접공고 미확인)' + ((' / ' + note) if note else '')
    if http in ('200', '200 OK', 'Working') or http.startswith('2'):
        badge = '<span class="ps-ok">✓ Working</span>'
    elif http in ('Dead', '404', '403', '410') or http.startswith(('4','5')):
        badge = '<span class="ps-dead">✗ Dead</span>'
    elif http == 'Login' or access == 'Login':
        badge = '<span class="ps-login">⚠ Login</span>'
    elif http == 'Info_only':
        badge = '<span class="ps-info">ℹ Info only</span>'
    elif http == 'JS_rendered':
        badge = '<span class="ps-js">⚠ JS render</span>'
    elif http == 'Blocked':
        badge = '<span class="ps-dead">✗ Blocked</span>'
    else:
        badge = '<span class="ps-na">— Unverified</span>'
    return badge, note

def portal_table(iso):
    portals = portals_by_iso.get(iso, [])
    if not portals:
        return '<p class="no-portals">포털 데이터 없음</p>'
    rows = ''
    for p in portals:
        url  = p['url'] or '#'
        name = (p['name'] or url).replace('<','&lt;')
        ptype = (p['type'] or '').replace('<','&lt;')
        badge, note = portal_status_html(p, iso)
        # Portal type badge colour
        if '국가조달' in ptype:
            type_span = f'<span class="pt-gov">{ptype}</span>'
        elif 'EMB' in ptype or '선거위' in ptype or '선거주관' in ptype or '선관위' in ptype:
            type_span = f'<span class="pt-emb">{ptype}</span>'
        else:
            type_span = f'<span class="pt-other">{ptype}</span>'
        note_cell = f'<span class="portal-note">{note}</span>' if note else ''
        rows += (f'<tr>'
                 f'<td>{type_span}</td>'
                 f'<td><a href="{url}" target="_blank" rel="noopener">{name}</a></td>'
                 f'<td>{badge} {note_cell}</td>'
                 f'</tr>')
    return (f'<table class="ptbl">'
            f'<thead><tr><th>유형</th><th>포털명</th><th>상태</th></tr></thead>'
            f'<tbody>{rows}</tbody>'
            f'</table>')

def country_card(ctr):
    iso   = ctr['iso3']
    flag  = FLAG.get(iso, '🏳')
    cat   = get_cat(iso)
    cm    = CAT_META[cat]
    cs    = get_crawl_status(iso)
    csm   = CRAWL_STATUS_META[cs]
    miru  = iso in MIRU_ISO
    bio_r = '✅' if ctr['bio_reg']  == 'Y' else '—'
    bio_v = '✅' if ctr['bio_verify']== 'Y' else '—'
    mtype = ctr['machine_type'] or ctr['voting_method'] or '—'
    miru_badge   = '<span class="miru-badge">★ MIRU</span>' if miru else ''
    cat_badge    = f'<span class="cat-badge" style="color:{cm["color"]};background:{cm["bg"]}">{cm["label"]}</span>'
    mtype_badge  = f'<span class="mtype-badge">{mtype}</span>'
    crawl_badge  = (f'<span class="crawl-badge" style="color:{csm["color"]}">'
                    f'{csm["icon"]} {csm["label"]}</span>')
    bio_html = f'<span class="bio-item">등록 {bio_r}</span><span class="bio-item">현장확인 {bio_v}</span>'
    ptbl = portal_table(iso)
    return (
        f'<div class="ccard" id="c-{iso}">'
        f'  <div class="ccard-head">'
        f'    <span class="cflag">{flag}</span>'
        f'    <div class="cname">'
        f'      <div class="cname-ko">{ctr["country_ko"]}</div>'
        f'      <div class="cname-en">{ctr["country"]} · {iso}</div>'
        f'    </div>'
        f'    <div class="cbadges">{miru_badge}{cat_badge}{mtype_badge}{crawl_badge}</div>'
        f'  </div>'
        f'  <div class="ccard-body">'
        f'    <div class="cbio">'
        f'      <span class="bio-label">생체인식</span>'
        f'      {bio_html}'
        f'    </div>'
        f'    {ptbl}'
        f'  </div>'
        f'</div>'
    )

def region_tab_content(region_name):
    isos = REGIONS[region_name]
    cards = ''
    for iso in isos:
        ctr = next((c for c in countries if c['iso3'] == iso), None)
        if ctr:
            cards += country_card(ctr)
    return f'<div class="region-grid">{cards}</div>'

# ── Stats for overview ───────────────────────────────────────────────────────
total_countries = len([c for c in countries if c['iso3'] != 'ESP'])
cat_counts = {}
for ctr in countries:
    cat = get_cat(ctr['iso3'])
    cat_counts[cat] = cat_counts.get(cat, 0) + 1

cat_country_lists = {}
for ctr in countries:
    cat = get_cat(ctr['iso3'])
    cat_country_lists.setdefault(cat, []).append(ctr['country_ko'])

emb_direct_count = cat_counts.get('both', 0) + cat_counts.get('emb_only', 0)
inaccessible_count = cat_counts.get('login_req', 0) + cat_counts.get('opaque', 0)

# Stat cards HTML
def stat_cards_html():
    html = ''
    for cat, cm in CAT_META.items():
        cnt   = cat_counts.get(cat, 0)
        names = ', '.join(cat_country_lists.get(cat, []))
        html += (
            f'<div class="stat-card">'
            f'  <div class="sc-count" style="color:{cm["color"]}">{cnt}</div>'
            f'  <div class="sc-label">{cm["label"]}</div>'
            f'  <div class="sc-label-en">{cm["label_en"]}</div>'
            f'  <div class="sc-countries">{names}</div>'
            f'</div>'
        )
    return html

# ── JSON embed for charts and CSV ────────────────────────────────────────────
chart_data = {
    'donut': {
        'labels': [CAT_META[k]['label_en'] for k in CAT_META],
        'values': [cat_counts.get(k, 0) for k in CAT_META],
        'colors': [CAT_META[k]['color'] for k in CAT_META],
    },
    'bar': {
        'regions': list(REGIONS.keys()),
        'cats': list(CAT_META.keys()),
        'colors': [CAT_META[k]['color'] for k in CAT_META],
        'data': {}
    }
}
for reg, isos in REGIONS.items():
    reg_cats = {}
    for iso in isos:
        cat = get_cat(iso)
        reg_cats[cat] = reg_cats.get(cat, 0) + 1
    chart_data['bar']['data'][reg] = [reg_cats.get(k, 0) for k in CAT_META]

# CSV rows
csv_rows = []
for ctr in countries:
    iso   = ctr['iso3']
    cat   = get_cat(iso)
    cm    = CAT_META[cat]
    region_ko = next((rk for rk, isos in REGIONS.items() if iso in isos), ctr['region'])
    portals = portals_by_iso.get(iso, [])
    portal_names = ' | '.join(p['name'] or p['url'] for p in portals if p['name'] or p['url'])
    portal_statuses = ' | '.join(p.get('http') or '—' for p in portals)
    cs  = get_crawl_status(iso)
    csv_rows.append({
        'iso3': iso,
        'country': ctr['country'],
        'country_ko': ctr['country_ko'],
        'region': region_ko,
        'machine_type': ctr['machine_type'] or ctr['voting_method'] or '—',
        'bio_reg': ctr['bio_reg'] or '—',
        'bio_verify': ctr['bio_verify'] or '—',
        'cat': cm['label_en'],
        'crawl_status': CRAWL_STATUS_META[cs]['label'],
        'portal_names': portal_names,
        'portal_statuses': portal_statuses,
        'miru': '★' if iso in MIRU_ISO else '',
    })

# Full table rows HTML
def full_table_rows():
    html = ''
    for row in csv_rows:
        iso = row['iso3']
        cat = get_cat(iso)
        cm  = CAT_META[cat]
        cs  = get_crawl_status(iso)
        csm = CRAWL_STATUS_META[cs]
        miru_cell   = '<span style="color:#ef4444;font-weight:700;">★ MIRU</span>' if row['miru'] else ''
        cat_cell    = f'<span class="cat-badge" style="color:{cm["color"]};background:{cm["bg"]}">{cm["label_en"]}</span>'
        crawl_cell  = f'<span style="font-size:11px;color:{csm["color"]};font-weight:700">{csm["icon"]} {csm["label"]}</span>'
        html += (
            f'<tr data-cat="{cat}" data-cs="{cs}">'
            f'<td>{FLAG.get(iso,"🏳")} {row["country_ko"]}</td>'
            f'<td style="color:#9aa6b5">{row["region"]}</td>'
            f'<td style="color:#9aa6b5">{row["machine_type"]}</td>'
            f'<td style="text-align:center">{row["bio_reg"]}&nbsp;/&nbsp;{row["bio_verify"]}</td>'
            f'<td>{cat_cell}</td>'
            f'<td>{crawl_cell}</td>'
            f'<td style="font-size:11px;color:#9aa6b5;max-width:200px;word-break:break-all">{row["portal_names"]}</td>'
            f'<td style="text-align:center">{miru_cell}</td>'
            f'</tr>'
        )
    return html

# ── Assemble final HTML ──────────────────────────────────────────────────────
CHART_DATA_JSON = json.dumps(chart_data, ensure_ascii=False)
CSV_DATA_JSON   = json.dumps(csv_rows, ensure_ascii=False)

HTML = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>조달 경로 분석 — Miru Systems Intelligence</title>
<style>
@font-face{{font-family:'Gmarket Sans';src:url('../fonts/GmarketSansTTFMedium.ttf') format('truetype');font-weight:300 800;font-display:swap;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
:root{{
  --bg:#070e1a;--card:#11161f;--surface:#0c1119;
  --text:#e7edf4;--text2:#9aa6b5;--muted:#6b7787;
  --border:#222c3a;--hover:#161d28;--shadow:rgba(0,0,0,.4);
  --red:#EB0513;--blue:#3B86D6;--navy:#04185F;
  --green:#22c55e;--purple:#a78bfa;--sky:#38bdf8;--orange:#fb923c;--slate:#94a3b8;
}}
html.light{{
  --bg:#f0f3f7;--card:#ffffff;--surface:#f5f7fa;
  --text:#0d1421;--text2:#4a5568;--muted:#8090a4;
  --border:#d1d9e4;--hover:#e8edf4;--shadow:rgba(0,0,0,.12);
}}
*{{transition:background-color .15s,color .15s,border-color .15s;}}
html,body{{min-height:100%;background:var(--bg);color:var(--text);font-family:'Gmarket Sans',sans-serif;font-size:14px;line-height:1.5;}}
::-webkit-scrollbar{{width:8px;height:8px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:var(--border);border-radius:5px;}}
a{{color:var(--blue);text-decoration:none;}}
a:hover{{text-decoration:underline;}}
input,select,button{{font-family:'Gmarket Sans',sans-serif;}}

/* TOP BAR */
#top-bar{{
  display:flex;align-items:center;gap:12px;
  height:56px;padding:0 20px;
  background:var(--navy);
  position:sticky;top:0;z-index:200;
  flex-wrap:nowrap;
}}
.tb-logo{{display:flex;align-items:center;gap:10px;flex:0 0 auto;}}
.tb-logo img{{height:20px;width:auto;display:block;}}
.tb-logo-divider{{width:1px;height:24px;background:rgba(255,255,255,.22);}}
.tb-logo-text .t1{{font-size:15px;font-weight:700;letter-spacing:.2px;color:#fff;}}
.tb-logo-text .t2{{font-size:8.5px;font-weight:500;letter-spacing:2px;color:rgba(255,255,255,.5);}}
.tb-nav{{display:flex;gap:4px;margin-left:6px;overflow-x:auto;}}
.tb-nav::-webkit-scrollbar{{height:0;}}
.nav-tab{{
  font-family:'Gmarket Sans',sans-serif;font-size:12px;padding:6px 12px;
  border-radius:7px;cursor:pointer;border:none;white-space:nowrap;
  background:rgba(255,255,255,.1);color:rgba(255,255,255,.72);
  transition:all .15s;
}}
.nav-tab:hover{{background:rgba(255,255,255,.18);color:#fff;}}
.nav-tab.active{{background:#fff;color:var(--navy);font-weight:700;}}
.tb-spacer{{flex:1;min-width:8px;}}
.tb-actions{{display:flex;gap:8px;flex:0 0 auto;}}
#csv-btn{{
  display:flex;align-items:center;gap:6px;padding:6px 13px;border-radius:7px;
  background:rgba(56,189,248,.12);border:1px solid rgba(56,189,248,.35);
  color:var(--sky);font-size:12px;cursor:pointer;white-space:nowrap;
}}
#csv-btn:hover{{background:rgba(56,189,248,.22);}}
#theme-btn{{
  width:32px;height:32px;border-radius:7px;border:none;cursor:pointer;
  background:rgba(255,255,255,.1);color:#fff;font-size:14px;
  display:flex;align-items:center;justify-content:center;
}}
#theme-btn:hover{{background:rgba(255,255,255,.18);}}

/* TAB PAGES */
.tab-page{{display:none;}}
.tab-page.active{{display:block;}}

/* HERO */
.hero{{padding:36px 24px 24px;text-align:center;}}
.hero h1{{font-size:26px;font-weight:800;color:var(--text);margin-bottom:6px;}}
.hero .sub{{font-size:13px;color:var(--text2);margin-bottom:20px;}}
.hero-stats{{display:flex;justify-content:center;gap:14px;flex-wrap:wrap;}}
.hstat{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:12px 18px;text-align:center;min-width:90px;
}}
.hstat-n{{font-size:22px;font-weight:800;line-height:1;}}
.hstat-l{{font-size:11px;color:var(--text2);margin-top:4px;}}

/* STAT CARDS */
.stat-cards{{
  display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
  gap:14px;max-width:1100px;margin:0 auto 32px;padding:0 20px;
}}
.stat-card{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:18px 16px;
}}
.sc-count{{font-size:36px;font-weight:800;line-height:1;margin-bottom:4px;}}
.sc-label{{font-size:13px;font-weight:700;color:var(--text);margin-bottom:2px;}}
.sc-label-en{{font-size:11px;color:var(--text2);margin-bottom:8px;}}
.sc-countries{{font-size:11px;color:var(--muted);line-height:1.6;}}

/* CHARTS */
.charts-row{{
  display:grid;grid-template-columns:1fr 1.6fr;
  gap:20px;max-width:1100px;margin:0 auto 28px;padding:0 20px;
}}
@media(max-width:700px){{.charts-row{{grid-template-columns:1fr;}}}}
.chart-card{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:20px;
}}
.chart-title{{font-size:13px;font-weight:700;color:var(--text2);margin-bottom:14px;letter-spacing:.04em;}}
.chart-wrap{{position:relative;}}
#donutChart{{max-height:240px;}}
#barChart{{max-height:280px;}}

/* INSIGHT BOXES */
.insights{{max-width:1100px;margin:0 auto 32px;padding:0 20px;display:flex;flex-direction:column;gap:10px;}}
.insight-box{{
  background:var(--card);border:1px solid var(--border);border-radius:10px;
  border-left:4px solid var(--blue);padding:14px 18px;
  font-size:13px;color:var(--text2);line-height:1.7;
}}
.insight-box strong{{color:var(--text);}}
.insight-box.green{{border-left-color:var(--green);}}
.insight-box.orange{{border-left-color:var(--orange);}}

/* REGION PAGE */
.region-page-wrap{{max-width:1100px;margin:0 auto;padding:20px;}}
.region-header{{margin-bottom:20px;padding-bottom:12px;border-bottom:1px solid var(--border);}}
.region-header h2{{font-size:18px;font-weight:800;color:var(--text);}}
.region-header .rcount{{font-size:12px;color:var(--muted);margin-top:3px;}}
.region-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(480px,1fr));gap:16px;}}
@media(max-width:600px){{.region-grid{{grid-template-columns:1fr;}}}}

/* COUNTRY CARD */
.ccard{{
  background:var(--card);border:1px solid var(--border);border-radius:12px;
  overflow:hidden;
}}
.ccard-head{{
  display:flex;align-items:center;gap:10px;
  padding:12px 16px;background:var(--surface);
  border-bottom:1px solid var(--border);flex-wrap:wrap;
}}
.cflag{{font-size:22px;line-height:1;}}
.cname{{flex:1;min-width:100px;}}
.cname-ko{{font-size:14px;font-weight:700;color:var(--text);}}
.cname-en{{font-size:11px;color:var(--muted);}}
.cbadges{{display:flex;flex-wrap:wrap;gap:5px;align-items:center;}}
.miru-badge{{
  font-size:11px;font-weight:700;padding:3px 8px;
  background:rgba(235,5,19,.1);color:#ef4444;
  border:1px solid rgba(235,5,19,.25);border-radius:20px;
}}
.cat-badge{{font-size:11px;font-weight:700;padding:3px 8px;border-radius:20px;white-space:nowrap;}}
.mtype-badge{{
  font-size:11px;padding:3px 8px;border-radius:20px;
  background:rgba(255,255,255,.07);color:var(--text2);
}}
.ccard-body{{padding:12px 16px;}}
.cbio{{
  display:flex;gap:8px;align-items:center;flex-wrap:wrap;
  margin-bottom:10px;font-size:12px;
}}
.bio-label{{color:var(--muted);font-size:11px;font-weight:700;letter-spacing:.04em;}}
.bio-item{{
  background:var(--surface);border:1px solid var(--border);
  border-radius:6px;padding:2px 8px;font-size:11px;color:var(--text2);
}}

/* PORTAL TABLE */
.ptbl{{width:100%;border-collapse:collapse;font-size:12px;}}
.ptbl th{{
  font-size:10px;font-weight:700;letter-spacing:.05em;
  color:var(--muted);padding:5px 8px;
  border-bottom:1px solid var(--border);text-align:left;
}}
.ptbl td{{padding:6px 8px;border-bottom:1px solid var(--border);vertical-align:top;}}
.ptbl tr:last-child td{{border-bottom:none;}}
.ptbl a{{color:var(--blue);font-size:12px;word-break:break-all;}}
.pt-gov{{
  font-size:10px;font-weight:700;padding:2px 6px;
  background:rgba(56,189,248,.12);color:var(--sky);border-radius:4px;white-space:nowrap;
}}
.pt-emb{{
  font-size:10px;font-weight:700;padding:2px 6px;
  background:rgba(167,139,250,.12);color:var(--purple);border-radius:4px;white-space:nowrap;
}}
.pt-other{{
  font-size:10px;font-weight:700;padding:2px 6px;
  background:rgba(255,255,255,.06);color:var(--text2);border-radius:4px;white-space:nowrap;
}}
.ps-ok{{font-size:11px;font-weight:700;color:#22c55e;}}
.ps-dead{{font-size:11px;font-weight:700;color:#ef4444;}}
.ps-login{{font-size:11px;font-weight:700;color:#fb923c;}}
.ps-info{{font-size:11px;color:var(--muted);}}
.ps-js{{font-size:11px;font-weight:700;color:#fb923c;}}
.ps-na{{font-size:11px;color:var(--muted);}}
.portal-note{{font-size:10px;color:var(--muted);margin-left:4px;}}
.no-portals{{font-size:12px;color:var(--muted);padding:8px 0;}}
.crawl-badge{{font-size:10.5px;font-weight:700;padding:3px 8px;border-radius:20px;background:rgba(255,255,255,.06);white-space:nowrap;}}

/* FULL LIST PAGE */
.list-wrap{{max-width:1100px;margin:0 auto;padding:20px;}}
.list-header{{
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:10px;margin-bottom:16px;
}}
.list-header h2{{font-size:18px;font-weight:800;}}
.filter-chips{{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:14px;}}
.chip{{
  font-size:11px;font-weight:700;padding:4px 12px;border-radius:20px;
  cursor:pointer;border:1px solid transparent;transition:all .15s;
  background:var(--card);color:var(--text2);border-color:var(--border);
}}
.chip.active{{color:#fff;}}
.chip[data-cat="all"].active{{background:var(--blue);border-color:var(--blue);}}
.chip[data-cat="both"].active{{background:#052e16;border-color:#22c55e;color:#22c55e;}}
.chip[data-cat="emb_only"].active{{background:#2e1065;border-color:#a78bfa;color:#a78bfa;}}
.chip[data-cat="gov_only"].active{{background:#082f49;border-color:#38bdf8;color:#38bdf8;}}
.chip[data-cat="login_req"].active{{background:#431407;border-color:#fb923c;color:#fb923c;}}
.chip[data-cat="opaque"].active{{background:#0f172a;border-color:#94a3b8;color:#94a3b8;}}
.full-tbl{{width:100%;border-collapse:collapse;font-size:12.5px;}}
.full-tbl th{{
  background:var(--surface);border-bottom:2px solid var(--border);
  padding:10px 12px;text-align:left;font-size:11px;font-weight:700;
  color:var(--text2);letter-spacing:.05em;cursor:pointer;user-select:none;
  white-space:nowrap;
}}
.full-tbl th:hover{{color:var(--text);}}
.full-tbl td{{padding:9px 12px;border-bottom:1px solid var(--border);vertical-align:top;}}
.full-tbl tr:hover td{{background:var(--hover);}}
.full-tbl tr.hidden{{display:none;}}

footer{{
  text-align:center;padding:24px;font-size:11px;color:var(--muted);
  border-top:1px solid var(--border);margin-top:20px;
}}
</style>
</head>
<body>

<!-- TOP BAR -->
<div id="top-bar">
  <div class="tb-logo">
    <img src="../miru_white_logo_enhanced_transparent.png" alt="Miru" onerror="this.style.display='none'">
    <div class="tb-logo-divider"></div>
    <div class="tb-logo-text">
      <div class="t1">Market Intelligence</div>
      <div class="t2">MIRU SYSTEMS · CONFIDENTIAL</div>
    </div>
  </div>
  <div class="tb-nav">
    <button class="nav-tab" onclick="location.href='https://bk4098a.github.io/miru-election-intel/'">← 홈</button>
    <button class="nav-tab active" data-tab="overview" onclick="showTab('overview')">개요</button>
    <button class="nav-tab" data-tab="africa" onclick="showTab('africa')">아프리카</button>
    <button class="nav-tab" data-tab="asia" onclick="showTab('asia')">아시아·중동</button>
    <button class="nav-tab" data-tab="europe" onclick="showTab('europe')">유럽·CIS</button>
    <button class="nav-tab" data-tab="americas" onclick="showTab('americas')">아메리카</button>
    <button class="nav-tab" data-tab="fulllist" onclick="showTab('fulllist')">전체 목록</button>
  </div>
  <div class="tb-spacer"></div>
  <div class="tb-actions">
    <button id="csv-btn" onclick="downloadCSV()">⬇ CSV 다운로드</button>
    <button id="theme-btn" onclick="toggleTheme()" title="테마 전환">☀</button>
  </div>
</div>

<!-- ══════════════════════════════════════════════════════════════
     TAB 1: 개요
══════════════════════════════════════════════════════════════ -->
<div id="tab-overview" class="tab-page active">

  <div class="hero">
    <h1>35개국 조달 경로 분석</h1>
    <div class="sub">기계투표·생체인식 도입국 전략 인텔리전스 · 2026.06.29</div>
    <div class="hero-stats">
      <div class="hstat"><div class="hstat-n" style="color:var(--sky)">{total_countries}</div><div class="hstat-l">모니터링 국가</div></div>
      <div class="hstat"><div class="hstat-n" style="color:var(--green)">{emb_direct_count}</div><div class="hstat-l">선관위 직접공고</div></div>
      <div class="hstat"><div class="hstat-n" style="color:var(--orange)">{inaccessible_count}</div><div class="hstat-l">접근 불가</div></div>
      <div class="hstat"><div class="hstat-n" style="color:#ef4444">{len(MIRU_ISO)}</div><div class="hstat-l">MIRU 납품국</div></div>
    </div>
  </div>

  <div class="stat-cards">
    {stat_cards_html()}
  </div>

  <div class="charts-row">
    <div class="chart-card">
      <div class="chart-title">조달 경로 분포</div>
      <div class="chart-wrap"><canvas id="donutChart"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">지역별 카테고리 분포</div>
      <div class="chart-wrap"><canvas id="barChart"></canvas></div>
    </div>
  </div>

  <div class="insights">
    <div class="insight-box green">
      <strong>선관위 직접공고 ({emb_direct_count}개국)</strong> &nbsp;
      Iraq (IHEC), Kenya (IEBC), Philippines (COMELEC), Brazil (TSE), South Africa (IEC), Jamaica (EOJ) — 이 6개국은 선관위가 자체 사이트에 조달 공고를 직접 게시합니다.
      국가조달 포털과 선관위 포털을 병행 모니터링해야 합니다.
    </div>
    <div class="insight-box orange">
      <strong>접근 불가 포털 ({inaccessible_count}개국)</strong> &nbsp;
      로그인 필요(Ghana, Iran, Korea, Georgia) 또는 완전 불투명(Venezuela) — 공개 크롤로는 공고 수집이 불가능합니다.
      파트너사 계정 또는 현지 네트워크를 통한 우회 모니터링이 필요합니다.
    </div>
    <div class="insight-box">
      <strong>국가조달 전용 ({cat_counts.get("gov_only", 0)}개국)</strong> &nbsp;
      대부분의 국가는 단일 국가 전자조달 포털에 모든 공고를 의무 게시합니다.
      정부 조달법상 의무 게시이므로 국가조달 포털 모니터링만으로 충분합니다.
    </div>
    <div class="insight-box" style="border-left-color:#38bdf8">
      <strong>수집 상태 현황</strong><br>
      ✅ 수집 확인 {sum(1 for c in countries if get_crawl_status(c["iso3"])=="confirmed")}개국 (BHR · KEN · IRQ · ZAF · PRY · PHL) &nbsp;|&nbsp;
      🔑 API키 필요 {sum(1 for c in countries if get_crawl_status(c["iso3"])=="needs_key")}개국 (KAZ · KOR · USA) &nbsp;|&nbsp;
      ⚠️ 파서 미확인 {sum(1 for c in countries if get_crawl_status(c["iso3"])=="parser_unconfirmed")}개국 &nbsp;|&nbsp;
      🔒 로그인 필요 {sum(1 for c in countries if get_crawl_status(c["iso3"])=="login_req")}개국 &nbsp;|&nbsp;
      ❓ 미조사 {sum(1 for c in countries if get_crawl_status(c["iso3"])=="not_investigated")}개국
    </div>
  </div>

</div>

<!-- ══════════════════════════════════════════════════════════════
     TAB 2-5: Regional pages
══════════════════════════════════════════════════════════════ -->
<div id="tab-africa" class="tab-page">
  <div class="region-page-wrap">
    <div class="region-header">
      <h2>🌍 아프리카</h2>
      <div class="rcount">{len(REGIONS["아프리카"])}개국</div>
    </div>
    {region_tab_content('아프리카')}
  </div>
</div>

<div id="tab-asia" class="tab-page">
  <div class="region-page-wrap">
    <div class="region-header">
      <h2>🌏 아시아·중동</h2>
      <div class="rcount">{len(REGIONS["아시아·중동"])}개국</div>
    </div>
    {region_tab_content('아시아·중동')}
  </div>
</div>

<div id="tab-europe" class="tab-page">
  <div class="region-page-wrap">
    <div class="region-header">
      <h2>🌍 유럽·CIS</h2>
      <div class="rcount">{len(REGIONS["유럽·CIS"])}개국</div>
    </div>
    {region_tab_content('유럽·CIS')}
  </div>
</div>

<div id="tab-americas" class="tab-page">
  <div class="region-page-wrap">
    <div class="region-header">
      <h2>🌎 아메리카</h2>
      <div class="rcount">{len(REGIONS["아메리카"])}개국</div>
    </div>
    {region_tab_content('아메리카')}
  </div>
</div>

<!-- ══════════════════════════════════════════════════════════════
     TAB 6: 전체 목록
══════════════════════════════════════════════════════════════ -->
<div id="tab-fulllist" class="tab-page">
  <div class="list-wrap">
    <div class="list-header">
      <h2>전체 목록 ({total_countries}개국)</h2>
      <button id="csv-btn2" onclick="downloadCSV()" style="
        display:flex;align-items:center;gap:6px;padding:7px 14px;border-radius:7px;
        background:rgba(56,189,248,.12);border:1px solid rgba(56,189,248,.35);
        color:var(--sky);font-size:12px;cursor:pointer;">⬇ CSV 다운로드</button>
    </div>
    <div class="filter-chips">
      <button class="chip active" data-cat="all" onclick="filterTable('all')">전체</button>
      <button class="chip" data-cat="both" onclick="filterTable('both')">국가조달 + 선관위 공동</button>
      <button class="chip" data-cat="emb_only" onclick="filterTable('emb_only')">선관위 직접공고</button>
      <button class="chip" data-cat="gov_only" onclick="filterTable('gov_only')">국가조달 전용</button>
      <button class="chip" data-cat="login_req" onclick="filterTable('login_req')">로그인 필요</button>
      <button class="chip" data-cat="opaque" onclick="filterTable('opaque')">수의계약/불투명</button>
    </div>
    <div style="overflow-x:auto;">
      <table class="full-tbl" id="fullTable">
        <thead>
          <tr>
            <th onclick="sortTable(0)">국가 ↕</th>
            <th onclick="sortTable(1)">지역 ↕</th>
            <th onclick="sortTable(2)">투표장비 ↕</th>
            <th style="text-align:center">생체인식<br><span style="font-weight:400;font-size:10px">등록/확인</span></th>
            <th onclick="sortTable(4)">조달 경로 ↕</th>
            <th onclick="sortTable(5)">수집 상태 ↕</th>
            <th>포털</th>
            <th style="text-align:center">MIRU</th>
          </tr>
        </thead>
        <tbody id="fullTableBody">
          {full_table_rows()}
        </tbody>
      </table>
    </div>
  </div>
</div>

<footer>
  Miru Systems · Election Technology Intelligence · 2026.06.29 · 총 {total_countries}개국 {len(portals_raw)}개 포털
</footer>

<!-- Chart.js (inlined for self-contained HTML) -->
{"<script>" + _chartjs_src + "</script>" if _chartjs_src else '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'}
<script>
/* ── Embedded data ────────────────────────────────────────── */
const CHART_DATA = {CHART_DATA_JSON};
const CSV_DATA   = {CSV_DATA_JSON};

/* ── Tab navigation ─────────────────────────────────────────── */
function showTab(name) {{
  document.querySelectorAll('.tab-page').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab[data-tab]').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  const btn = document.querySelector('.nav-tab[data-tab="' + name + '"]');
  if (btn) btn.classList.add('active');
  // Init charts on first open of overview
  if (name === 'overview') initCharts();
}}

/* ── Theme toggle ─────────────────────────────────────────── */
function toggleTheme() {{
  const isLight = document.documentElement.classList.toggle('light');
  document.getElementById('theme-btn').textContent = isLight ? '🌙' : '☀';
  localStorage.setItem('miru_theme', isLight ? 'light' : 'dark');
}}
(function() {{
  if (localStorage.getItem('miru_theme') === 'light') {{
    document.documentElement.classList.add('light');
    const btn = document.getElementById('theme-btn');
    if (btn) btn.textContent = '🌙';
  }}
}})();

/* ── Charts ───────────────────────────────────────────────── */
let chartsInited = false;
function initCharts() {{
  if (chartsInited || typeof Chart === 'undefined') return;
  chartsInited = true;

  const isDark = !document.documentElement.classList.contains('light');
  const gridColor = isDark ? 'rgba(255,255,255,.07)' : 'rgba(0,0,0,.07)';
  const labelColor = isDark ? '#9aa6b5' : '#4a5568';

  // Donut chart
  new Chart(document.getElementById('donutChart'), {{
    type: 'doughnut',
    data: {{
      labels: CHART_DATA.donut.labels,
      datasets: [{{
        data: CHART_DATA.donut.values,
        backgroundColor: CHART_DATA.donut.colors,
        borderColor: isDark ? '#11161f' : '#ffffff',
        borderWidth: 3,
        hoverOffset: 6,
      }}]
    }},
    options: {{
      responsive: true,
      cutout: '62%',
      plugins: {{
        legend: {{
          position: 'bottom',
          labels: {{ color: labelColor, boxWidth: 12, padding: 12, font: {{ size: 11 }} }}
        }},
        tooltip: {{
          callbacks: {{
            label: ctx => ` ${{ctx.label}}: ${{ctx.raw}}개국`
          }}
        }}
      }}
    }}
  }});

  // Horizontal bar chart
  const regions = CHART_DATA.bar.regions;
  const cats = CHART_DATA.bar.cats;
  const catLabels = {json.dumps([CAT_META[k]['label_en'] for k in CAT_META])};
  const datasets = cats.map((cat, i) => ({{
    label: catLabels[i],
    data: regions.map(r => CHART_DATA.bar.data[r][i]),
    backgroundColor: CHART_DATA.bar.colors[i],
    borderRadius: 3,
    borderSkipped: false,
  }}));

  new Chart(document.getElementById('barChart'), {{
    type: 'bar',
    data: {{ labels: regions, datasets }},
    options: {{
      indexAxis: 'y',
      responsive: true,
      scales: {{
        x: {{
          stacked: true,
          grid: {{ color: gridColor }},
          ticks: {{ color: labelColor, font: {{ size: 11 }}, stepSize: 1 }},
        }},
        y: {{
          stacked: true,
          grid: {{ color: gridColor }},
          ticks: {{ color: labelColor, font: {{ size: 12 }} }},
        }}
      }},
      plugins: {{
        legend: {{
          position: 'bottom',
          labels: {{ color: labelColor, boxWidth: 12, padding: 10, font: {{ size: 11 }} }}
        }},
        tooltip: {{
          mode: 'index',
          callbacks: {{
            label: ctx => ctx.raw > 0 ? ` ${{ctx.dataset.label}}: ${{ctx.raw}}개국` : null
          }}
        }}
      }}
    }}
  }});
}}

// Init charts immediately (overview is shown first)
if (document.readyState === 'loading') {{
  document.addEventListener('DOMContentLoaded', initCharts);
}} else {{
  initCharts();
}}

/* ── Full list: filter chips ─────────────────────────────── */
function filterTable(cat) {{
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  const activeChip = document.querySelector('.chip[data-cat="' + cat + '"]');
  if (activeChip) activeChip.classList.add('active');
  document.querySelectorAll('#fullTableBody tr').forEach(tr => {{
    if (cat === 'all' || tr.dataset.cat === cat) {{
      tr.classList.remove('hidden');
    }} else {{
      tr.classList.add('hidden');
    }}
  }});
}}

/* ── Full list: sort ─────────────────────────────────────── */
let sortState = {{ col: -1, asc: true }};
function sortTable(col) {{
  const tbody = document.getElementById('fullTableBody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const asc = sortState.col === col ? !sortState.asc : true;
  sortState = {{ col, asc }};
  rows.sort((a, b) => {{
    const ta = a.cells[col]?.textContent.trim() || '';
    const tb = b.cells[col]?.textContent.trim() || '';
    return asc ? ta.localeCompare(tb, 'ko') : tb.localeCompare(ta, 'ko');
  }});
  rows.forEach(r => tbody.appendChild(r));
}}

/* ── CSV download ────────────────────────────────────────── */
function downloadCSV() {{
  const headers = ['iso3','country','country_ko','region','machine_type','bio_reg','bio_verify','cat','crawl_status','portal_names','portal_statuses','miru'];
  const rows = CSV_DATA.map(r => headers.map(h => {{
    const v = String(r[h] || '').replace(/"/g, '""');
    return v.includes(',') || v.includes('"') || v.includes('\\n') ? '"' + v + '"' : v;
  }}).join(','));
  const csv = [headers.join(','), ...rows].join('\\n');
  const blob = new Blob(['\\uFEFF' + csv], {{ type: 'text/csv;charset=utf-8;' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'miru_election_intel_portals.csv';
  document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
}}
</script>
</body>
</html>'''

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(HTML)

line_count = HTML.count('\n') + 1
print(f'Done: {OUT}')
print(f'{total_countries} countries | {len(portals_raw)} portals (excl. ESP)')
print(f'Line count: {line_count}')
