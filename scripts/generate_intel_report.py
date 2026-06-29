"""Generate election_tech_report.html from election_technology_world.db"""
import sqlite3, sys, os
sys.stdout.reconfigure(encoding='utf-8')

DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'election_technology_world.db')
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'election_tech_report.html')

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("""
SELECT iso3,country,country_ko,region,voting_method,machine_type,machine_model,
       vendor_name,biometric_voter_reg,biometric_voter_verify,evoting,
       contract_year,deployment_scale,notes,machine_voting,
       last_election_date,next_election_date
FROM countries
WHERE iso3 IN (SELECT DISTINCT iso3 FROM machine_voting_portals)
ORDER BY region,country
""")
cols=['iso3','country','country_ko','region','voting_method','machine_type','machine_model',
      'vendor','bio_reg','bio_verify','evoting','contract_year','deploy_scale','notes',
      'machine_voting','last_election','next_election']
countries=[dict(zip(cols,r)) for r in c.fetchall()]

c.execute("""
SELECT iso3,portal_type,portal_name,url,access,priority,notes,http_status
FROM machine_voting_portals ORDER BY iso3,portal_type
""")
portals_by_iso={}
for r in c.fetchall():
    portals_by_iso.setdefault(r[0],[]).append(
        {'type':r[1],'name':r[2],'url':r[3],'access':r[4],'priority':r[5],'notes':r[6],'http':r[7]})
conn.close()

MIRU_ISO={'PHL','KOR','KGZ','IRQ','PRY','COD'}
FLAG={'COD':'🇨🇩','GHA':'🇬🇭','KEN':'🇰🇪','ZAF':'🇿🇦','ARG':'🇦🇷','BRA':'🇧🇷','DOM':'🇩🇴',
      'HND':'🇭🇳','JAM':'🇯🇲','PAN':'🇵🇦','PRY':'🇵🇾','SLV':'🇸🇻','USA':'🇺🇸','VEN':'🇻🇪',
      'BTN':'🇧🇹','IND':'🇮🇳','MNG':'🇲🇳','PHL':'🇵🇭','KOR':'🇰🇷','KAZ':'🇰🇿','KGZ':'🇰🇬',
      'UZB':'🇺🇿','ALB':'🇦🇱','BEL':'🇧🇪','BGR':'🇧🇬','BIH':'🇧🇦','CHE':'🇨🇭','EST':'🇪🇪',
      'GEO':'🇬🇪','MKD':'🇲🇰','ARE':'🇦🇪','BHR':'🇧🇭','IRN':'🇮🇷','IRQ':'🇮🇶','OMN':'🇴🇲'}

def portal_route(iso):
    types=[p['type'] for p in portals_by_iso.get(iso,[])]
    has_gov=any('국가조달' in t for t in types)
    has_emb=any(t=='EMB조달' for t in types)
    has_site=any(t in('선거위','선거주관','선거위(e-voting)') for t in types)
    if has_emb and has_gov: return 'both'
    if has_emb: return 'emb_only'
    if has_gov and has_site: return 'gov_plus_site'
    if has_gov: return 'gov_only'
    return 'unknown'

ROUTE={'both':('국가조달 + EMB 직접공고','#1B5E20','#E8F5E9'),
       'gov_plus_site':('국가조달 → 선거위 연동','#0D47A1','#E3F2FD'),
       'gov_only':('국가조달 전용','#E65100','#FFF3E0'),
       'emb_only':('선거위 직접공고','#4A148C','#F3E5F5'),
       'unknown':('미분류','#525252','#F5F5F5')}

def ml(mv):
    return {'Yes':('전체 도입','#1B5E20','#E8F5E9'),
            'Pilot':('파일럿/부분','#E65100','#FFF3E0')}.get(mv,('생체인식만','#0D47A1','#E3F2FD'))

def pb(pt):
    if '국가조달' in pt: return f'<span class="ptg">{pt}</span>'
    if pt=='EMB조달':    return f'<span class="pte">{pt}</span>'
    return f'<span class="pts">{pt}</span>'

def country_panel(ctr):
    iso=ctr['iso3']; flag=FLAG.get(iso,'🏳')
    miru=iso in MIRU_ISO
    rl,rc,rbg=ROUTE[portal_route(iso)]
    mll,mlc,mlbg=ml(ctr['machine_voting'])
    bio='유권자 등록 '+('✅' if ctr['bio_reg']=='Y' else '—')+'  투표소 확인 '+('✅' if ctr['bio_verify']=='Y' else '—')
    ps=portals_by_iso.get(iso,[])
    mb='<span class="mb">★ MIRU 납품국</span>' if miru else ''

    ptbl=''
    for p in ps:
        url=p['url'] or '#'; nh=(p['notes'] or '')
        hc='hok' if (p['http'] or '').startswith('2') else ('her' if (p['http'] or '').startswith(('4','5')) else 'hna')
        hb=f'<span class="{hc}">{p["http"]}</span>' if p['http'] else ''
        ptbl+=f'<tr><td>{pb(p["type"])}</td><td><a href="{url}" target="_blank">{p["name"] or url}</a></td><td class="pn">{nh} {hb}</td></tr>'

    minfo=''
    for lbl,key in [('유형','machine_type'),('모델','machine_model'),('공급사','vendor'),('계약','contract_year'),('규모','deploy_scale')]:
        if ctr[key]: minfo+=f'<div class="ir"><span class="il">{lbl}</span><span class="iv">{ctr[key]}</span></div>'
    notes_h=f'<div class="cn">{ctr["notes"]}</div>' if ctr['notes'] else ''

    return f'''<div class="cc" id="{iso}">
  <div class="ch">
    <span class="cf">{flag}</span>
    <div class="cn2"><div class="cn3">{ctr["country_ko"]}</div><div class="cn4">{ctr["country"]} · {iso}</div></div>
    <div class="cbdg">{mb}<span class="bm" style="background:{mlbg};color:{mlc};">{mll}</span><span class="br2" style="background:{rbg};color:{rc};">{rl}</span></div>
  </div>
  <div class="cb2">
    <div class="col">
      <div class="ct">🗳 투표 장비</div>
      <div class="ir"><span class="il">방식</span><span class="iv">{ctr["voting_method"] or "—"}</span></div>
      {minfo}{notes_h}
    </div>
    <div class="col">
      <div class="ct">🔍 생체인식</div>
      <div class="ir"><span class="il">등록</span><span class="iv">{"✅ 적용" if ctr["bio_reg"]=="Y" else "미사용"}</span></div>
      <div class="ir"><span class="il">투표소</span><span class="iv">{"✅ 적용" if ctr["bio_verify"]=="Y" else "미사용"}</span></div>
      <div class="ir"><span class="il">e-voting</span><span class="iv">{"✅" if ctr["evoting"]=="Y" else "—"}</span></div>
    </div>
    <div class="col colw">
      <div class="ct">📋 조달 경로</div>
      <table class="pt"><thead><tr><th>유형</th><th>포털명</th><th>비고</th></tr></thead><tbody>{ptbl}</tbody></table>
    </div>
  </div>
</div>'''

total=len(countries)
machine_yes=sum(1 for x in countries if x['machine_voting']=='Yes')
machine_pilot=sum(1 for x in countries if x['machine_voting']=='Pilot')
bio_use=sum(1 for x in countries if x['bio_reg']=='Y' or x['bio_verify']=='Y')
route_counts={}
for ctr in countries:
    r=portal_route(ctr['iso3']); route_counts[r]=route_counts.get(r,0)+1

REGION_ORDER=['Africa','Americas','Asia-Pacific','Central Asia','Europe','Middle East']
REGION_KO={'Africa':'아프리카','Americas':'아메리카','Asia-Pacific':'아시아·태평양',
           'Central Asia':'중앙아시아','Europe':'유럽','Middle East':'중동'}
regions={}
for ctr in countries: regions.setdefault(ctr['region'],[]).append(ctr)

panels=''
for reg in REGION_ORDER:
    ctrs=regions.get(reg,[])
    if not ctrs: continue
    panels+=f'<section class="rs" id="r-{reg.lower().replace(" ","-")}"><div class="rh"><span class="rn">{REGION_KO[reg]}</span><span class="rs2">{reg} · {len(ctrs)}개국</span></div>'
    for ctr in ctrs: panels+=country_panel(ctr)
    panels+='</section>'

nav_rows=''
for ctr in countries:
    iso=ctr['iso3']; rl,rc,rbg=ROUTE[portal_route(iso)]
    nav_rows+=f'<tr><td>{REGION_KO.get(ctr["region"],ctr["region"])}</td><td><a href="#{iso}">{FLAG.get(iso,"🏳")} {ctr["country_ko"]}</a></td><td style="color:#8C8C8C">{iso}</td><td>{ctr["voting_method"] or "—"}</td><td><span style="font-size:.68rem;font-weight:700;padding:.15rem .5rem;border-radius:4px;background:{rbg};color:{rc};">{rl}</span></td><td style="color:#EB0414;font-weight:700;">{"★" if iso in MIRU_ISO else ""}</td></tr>'

sum_route=''
for r,lbl in ROUTE.items():
    cnt=route_counts.get(r,0)
    if cnt: sum_route+=f'<div class="si2"><span class="sn" style="color:{lbl[1]};">{cnt}</span><span class="sl">{lbl[0]}</span></div>'

HTML=f'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>선거 장비 도입국 조달 경로 분석 — MIRU</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--navy:#05195E;--red:#EB0414;--accent:#123A9E;--accent2:#AEB7D6;--ink:#161616;--slate:#525252;--steel:#8C8C8C;--fog:#F2F4FA;--line:#C7CEDC;--white:#fff}}
body{{font-family:'Noto Sans KR',-apple-system,sans-serif;font-size:14px;color:var(--ink);background:#f8f9fc;line-height:1.65}}
a{{color:var(--accent)}}a:hover{{text-decoration:underline}}
.hdr{{background:var(--navy);color:#fff;padding:2.5rem 2rem 2rem}}
.hdr-eye{{font-size:.68rem;letter-spacing:.18em;color:var(--accent2);text-transform:uppercase;margin-bottom:.5rem}}
.hdr-title{{font-size:1.55rem;font-weight:700;line-height:1.2;margin-bottom:.5rem}}
.hdr-sub{{font-size:.84rem;color:rgba(255,255,255,.62);max-width:640px;margin-bottom:1.2rem}}
.hdr-meta{{font-size:.7rem;color:rgba(255,255,255,.4)}}
.sbar{{background:var(--white);border-bottom:1px solid var(--line);padding:1.1rem 2rem;display:flex;flex-wrap:wrap;gap:1.4rem;align-items:center}}
.skpi{{text-align:center;min-width:64px}}.skn{{font-size:1.55rem;font-weight:700;color:var(--navy);line-height:1}}.skl{{font-size:.66rem;color:var(--steel);margin-top:.2rem}}
.sdiv{{width:1px;height:32px;background:var(--line)}}
.sroute{{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}}
.si2{{display:flex;align-items:center;gap:.4rem;font-size:.74rem}}.sn{{font-size:1.05rem;font-weight:700}}.sl{{color:var(--slate)}}
.fbox{{max-width:960px;margin:1.4rem auto;padding:0 1.4rem}}
.f{{background:var(--white);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:0 7px 7px 0;padding:.9rem 1.3rem;margin-bottom:.7rem;font-size:.83rem;color:var(--slate);line-height:1.7}}
.f strong{{color:var(--navy)}}
.nwrap{{max-width:960px;margin:1rem auto;padding:0 1.4rem}}
.ntbl{{width:100%;border-collapse:collapse;font-size:.77rem;background:var(--white);border:1px solid var(--line);border-radius:8px;overflow:hidden}}
.ntbl th{{background:var(--navy);color:#fff;padding:.52rem .9rem;text-align:left;font-size:.7rem;letter-spacing:.04em}}
.ntbl td{{padding:.48rem .9rem;border-bottom:1px solid var(--line)}}.ntbl tr:last-child td{{border-bottom:none}}.ntbl tr:hover td{{background:var(--fog)}}
.rs{{max-width:960px;margin:2rem auto;padding:0 1.4rem}}
.rh{{display:flex;align-items:baseline;gap:.7rem;margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:2px solid var(--navy)}}
.rn{{font-size:1.05rem;font-weight:700;color:var(--navy)}}.rs2{{font-size:.73rem;color:var(--steel)}}
.cc{{background:var(--white);border:1px solid var(--line);border-radius:8px;margin-bottom:.9rem;overflow:hidden}}
.ch{{display:flex;align-items:center;gap:.9rem;padding:.8rem 1.1rem;background:var(--fog);border-bottom:1px solid var(--line);flex-wrap:wrap}}
.cf{{font-size:1.7rem}}.cn2{{flex:1;min-width:130px}}.cn3{{font-size:.93rem;font-weight:700;color:var(--navy)}}.cn4{{font-size:.7rem;color:var(--steel)}}
.cbdg{{display:flex;flex-wrap:wrap;gap:.35rem}}
.mb{{display:inline-flex;font-size:.64rem;font-weight:700;padding:.18rem .6rem;background:rgba(235,4,20,.08);color:var(--red);border:1px solid rgba(235,4,20,.22);border-radius:20px}}
.bm,.br2{{font-size:.64rem;font-weight:700;padding:.18rem .6rem;border-radius:20px}}
.cb2{{display:grid;grid-template-columns:1fr 1fr 2fr}}
.col{{padding:.9rem 1.1rem;border-right:1px solid var(--line)}}.col:last-child{{border-right:none}}
.ct{{font-size:.7rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--steel);margin-bottom:.6rem}}
.ir{{display:flex;gap:.4rem;margin-bottom:.28rem;font-size:.79rem}}.il{{color:var(--steel);flex-shrink:0;width:54px}}.iv{{color:var(--ink);font-weight:500}}
.cn{{font-size:.73rem;color:var(--slate);margin-top:.5rem;line-height:1.5;background:var(--fog);padding:.45rem .6rem;border-radius:4px}}
.pt{{width:100%;border-collapse:collapse;font-size:.76rem}}
.pt th{{font-size:.66rem;font-weight:700;color:var(--steel);padding:.28rem .45rem;border-bottom:1px solid var(--line);text-align:left}}
.pt td{{padding:.36rem .45rem;border-bottom:1px solid var(--fog);vertical-align:top}}.pt tr:last-child td{{border-bottom:none}}
.pn{{font-size:.7rem;color:var(--slate)}}
.ptg{{font-size:.63rem;font-weight:700;padding:.12rem .45rem;background:#E3F2FD;color:#0D47A1;border-radius:3px;white-space:nowrap}}
.pte{{font-size:.63rem;font-weight:700;padding:.12rem .45rem;background:#FCE4EC;color:#B71C1C;border-radius:3px;white-space:nowrap}}
.pts{{font-size:.63rem;font-weight:700;padding:.12rem .45rem;background:#F3E5F5;color:#4A148C;border-radius:3px;white-space:nowrap}}
.hok{{font-size:.63rem;background:#E8F5E9;color:#1B5E20;padding:.1rem .35rem;border-radius:3px}}
.her{{font-size:.63rem;background:#FFEBEE;color:#B71C1C;padding:.1rem .35rem;border-radius:3px}}
.hna{{font-size:.63rem;background:#F5F5F5;color:#757575;padding:.1rem .35rem;border-radius:3px}}
@media(max-width:680px){{.cb2{{grid-template-columns:1fr}}.col{{border-right:none;border-bottom:1px solid var(--line)}}}}
footer{{text-align:center;padding:1.8rem;font-size:.7rem;color:var(--steel);border-top:1px solid var(--line);margin-top:2rem;background:var(--white)}}
</style></head><body>

<div class="hdr">
  <div class="hdr-eye">MIRU SYSTEMS · INTELLIGENCE REPORT · CONFIDENTIAL</div>
  <h1 class="hdr-title">선거 장비 도입국 35개국 조달 경로 분석</h1>
  <p class="hdr-sub">기계투표(DRE·EVM·OMR) 및 생체인식 장비 사용 국가들이<br>조달 공고를 <strong style="color:#fff">국가조달 포털</strong>에 올리는지 <strong style="color:#fff">자체 선관위 사이트</strong>에 올리는지 분석</p>
  <div class="hdr-meta">작성: bhkim@mirusystems.com · 2026.06.29</div>
</div>

<div class="sbar">
  <div class="skpi"><div class="skn">{total}</div><div class="skl">모니터링 국가</div></div>
  <div class="sdiv"></div>
  <div class="skpi"><div class="skn">{machine_yes}</div><div class="skl">기계투표 전체</div></div>
  <div class="skpi"><div class="skn">{machine_pilot}</div><div class="skl">파일럿·부분</div></div>
  <div class="skpi"><div class="skn">{bio_use}</div><div class="skl">생체인식 활용</div></div>
  <div class="skpi"><div class="skn" style="color:var(--red);">{len(MIRU_ISO)}</div><div class="skl">MIRU 납품국</div></div>
  <div class="sdiv"></div>
  <div class="sroute">{sum_route}</div>
</div>

<div class="fbox">
  <div class="f"><strong>핵심 결론 ①</strong> &nbsp;35개국 전부 <strong>국가조달 포털이 1차 공고 채널</strong>. 정부 조달법상 의무 게시이므로 전자조달 포털에 반드시 올라옵니다.</div>
  <div class="f"><strong>핵심 결론 ②</strong> &nbsp;브라질(TSE)·부탄(ECB)·인도(ECI/CPPP)·자메이카(EOJ)·필리핀(COMELEC) <strong>5개국은 선관위가 자체 사이트에도 직접 공고</strong>. 국가조달 포털과 병행 게시.</div>
  <div class="f"><strong>핵심 결론 ③</strong> &nbsp;나머지 국가의 선관위 사이트는 <strong>정보 제공 목적</strong>. 입찰 공고는 국가조달 포털에만 올라가며, 선관위 사이트에서 포털로 링크 안내하는 형태.</div>
  <div class="f"><strong>생체인식 현황</strong> &nbsp;<strong>{bio_use}개국</strong> 생체인식 활용 중. 유권자 등록(생체DB 구축)과 투표소 현장 본인확인(지문·얼굴인식)으로 구분. 이라크·오만·키르기스스탄은 두 가지 모두 적용.</div>
</div>

<div class="nwrap">
  <table class="ntbl">
    <thead><tr><th>지역</th><th>국가</th><th>ISO</th><th>투표방식</th><th>조달경로</th><th>MIRU</th></tr></thead>
    <tbody>{nav_rows}</tbody>
  </table>
</div>

{panels}

<footer>MIRU Systems · Election Technology Intelligence · 2026.06.29 · 총 {total}개국 {len([p for ps in portals_by_iso.values() for p in ps])}개 포털</footer>
</body></html>'''

with open(OUT,'w',encoding='utf-8') as f: f.write(HTML)
print(f'Done: {OUT}')
print(f'{total} countries | {len([p for ps in portals_by_iso.values() for p in ps])} portals')
