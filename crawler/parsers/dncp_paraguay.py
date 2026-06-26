"""Paraguay — DNCP (Dirección Nacional de Contrataciones Públicas) OCDS API
API: https://www.contrataciones.gov.py/datos/api/v3/doc/search/processes
No auth required. Search by tender.title.
"""
import requests
from crawler.keywords import score
from crawler.translate import translate_to_en

import urllib3
urllib3.disable_warnings()

BASE_API = 'https://www.contrataciones.gov.py/datos/api/v3/doc'
BASE_WEB = 'https://www.contrataciones.gov.py'
PORTAL = 'contrataciones.gov.py'
BUYER_TSJE = ('justicia electoral', 'tsje', 'tribunal electoral', 'electoral')

SEARCH_TERMS = [
    'electoral',
    'elecciones',
    'voto',
    'urna electoral',
    'padron electoral',
    'tribunal electoral',
    'sistema electoral',
    'biometrico',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}


def _build_url(ocid):
    parts = ocid.split('-')
    ocid_num = parts[2] if len(parts) >= 3 else ''
    if ocid_num:
        return f'{BASE_WEB}/licitaciones/convocatoria/{ocid_num}.html'
    return BASE_WEB


def _fetch(session, term):
    try:
        r = session.get(
            f'{BASE_API}/search/processes',
            params={'tender.title': term, 'items_per_page': 50},
            headers=HEADERS, timeout=20, verify=False,
        )
        r.raise_for_status()
        return r.json().get('records', [])
    except Exception as e:
        print(f'  [dncp_paraguay] API error ({term}): {e}')
        return []


def parse(country='Paraguay', iso3='PRY'):
    session = requests.Session()
    seen_ocids = set()
    results = []

    for term in SEARCH_TERMS:
        for rec in _fetch(session, term):
            ocid = rec.get('ocid', '')
            if ocid in seen_ocids:
                continue
            seen_ocids.add(ocid)

            cr = rec.get('compiledRelease', {})
            tender = cr.get('tender', {})
            title = (tender.get('title') or '').strip()
            if not title:
                continue

            # Check buyer is election-related even if title isn't
            buyer_name = ((cr.get('buyer') or {}).get('name') or '').strip()
            is_election_buyer = any(k in buyer_name.lower() for k in BUYER_TSJE)

            tp = tender.get('tenderPeriod') or {}
            deadline = (tp.get('endDate') or '')[:10]
            pub_date = (tp.get('startDate') or '')[:10]
            url = _build_url(ocid)
            status = (tender.get('status') or '').lower()
            snippet = f"{title} | {buyer_name} | {status}"

            s = score(title, snippet)
            if s <= 0 and is_election_buyer:
                s = 40  # boost score for TSJE/electoral buyer

            title_en = translate_to_en(title, sl='es')

            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'title_en': title_en, 'url': url,
                'published_date': pub_date,
                'deadline_date': deadline,
                'status': status or 'active',
                'buyer': buyer_name or 'DNCP Paraguay',
                'amount': None, 'currency': 'PYG',
                'snippet': snippet[:300],
                'score': s,
            })

    print(f'  [dncp_paraguay] {len(results)} notices found')
    return results
