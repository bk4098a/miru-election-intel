"""Kazakhstan — goszakup.gov.kz REST API v3"""
import os
import requests
from crawler.keywords import score

BASE = 'https://ows.goszakup.gov.kz/v3/trd-buy'
KEYWORDS = ['election', 'выборы', 'избирательн', 'голосован', 'биометр']
PORTAL = 'goszakup.gov.kz'

def _session():
    s = requests.Session()
    s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
    token = os.getenv('GOSZAKUP_TOKEN')
    if token:
        s.headers['Authorization'] = f'Bearer {token}'
    return s


def _fetch_keyword(session, keyword, limit=50):
    try:
        r = session.get(BASE, params={'filter[name]': keyword, 'limit': limit}, timeout=30)
        if r.status_code == 401:
            print(f'  [goszakup] 401 — set GOSZAKUP_TOKEN env var for authenticated access')
            return []
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else data.get('items', data.get('data', []))
    except Exception as e:
        print(f'  [goszakup] error ({keyword}): {e}')
        return []


def parse(country='Kazakhstan', iso3='KAZ'):
    session = _session()
    seen = set()
    results = []

    for kw in KEYWORDS:
        for item in _fetch_keyword(session, kw):
            url = item.get('trd_url') or item.get('link') or \
                  f"https://www.goszakup.gov.kz/ru/announce/index/{item.get('id','')}"
            title = item.get('name_ru') or item.get('name_kz') or item.get('name', '')
            if not title or url in seen:
                continue
            seen.add(url)
            snippet = item.get('subject_type', {}).get('name_ru', '') if isinstance(item.get('subject_type'), dict) else ''

            amount = None
            try:
                amount = float(item.get('ref_trade_methods', {}).get('price') or item.get('price') or 0) or None
            except Exception:
                pass

            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'url': url,
                'published_date': item.get('publish_date', ''),
                'deadline_date': item.get('end_date', ''),
                'status': item.get('status', {}).get('name_ru', '') if isinstance(item.get('status'), dict) else str(item.get('status', '')),
                'buyer': item.get('org_name_ru', '') or item.get('customer_bin', ''),
                'amount': amount, 'currency': 'KZT',
                'snippet': snippet,
                'score': score(title, snippet),
            })

    print(f'  [goszakup] {len(results)} notices found')
    return results
