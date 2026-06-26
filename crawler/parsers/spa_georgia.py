"""Georgia — SPA (State Procurement Agency) tenders.procurement.gov.ge
Portal: https://tenders.procurement.gov.ge
Tries REST API, falls back to HTML scraping.
"""
import requests
import urllib3
urllib3.disable_warnings()
from bs4 import BeautifulSoup
from crawler.keywords import score
from crawler.translate import translate_to_en

BASE = 'https://tenders.procurement.gov.ge'
PORTAL = 'procurement.gov.ge'

KEYWORDS = [
    'election', 'voting', 'ballot', 'biometric', 'electoral',
    'არჩევნები', 'ხმის მიცემა',  # Georgian: elections, voting
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en,ka;q=0.8',
}


def _api_search(session, keyword):
    """Try the SPA REST API endpoints (various known patterns for Georgian e-procurement)."""
    # Try both GET and POST variants with different path conventions
    attempts = [
        (f'{BASE}/api/v1/tender/list',       {'keyword': keyword, 'page': 0, 'pageSize': 50}, 'GET'),
        (f'{BASE}/api/tenders',              {'keyword': keyword, 'lang': 'ka', 'page': 1, 'pageSize': 50}, 'GET'),
        (f'{BASE}/api/v1/public/tenders',    {'keyword': keyword, 'status': 'ACTIVE'}, 'GET'),
        (f'{BASE}/api/announcements',        {'keyword': keyword, 'page': 1, 'limit': 50}, 'GET'),
        (f'{BASE}/tenders/api/search',       {'q': keyword, 'page': 0, 'size': 50}, 'GET'),
    ]
    for url, params, method in attempts:
        try:
            r = session.get(url, params=params, headers=HEADERS, timeout=15, verify=False)
            if r.status_code == 200 and 'json' in r.headers.get('content-type', ''):
                data = r.json()
                items = (data.get('data') or data.get('items') or data.get('tenders')
                         or data.get('content') or data.get('list')
                         or (data if isinstance(data, list) else None))
                if items:
                    return items, url
        except Exception:
            continue
    return None, None


def _html_scrape(session):
    """Fallback: scrape the portal root (Georgian-language). Filter by election keywords."""
    results = []
    # Root URL and common Georgian government portal sub-paths
    urls_to_try = [
        BASE,
        f'{BASE}/ka/public/tenders',
        f'{BASE}/ka/tenders',
        f'{BASE}/public/tenders',
    ]
    ELECTION_KW = ['election', 'ballot', 'vote', 'biometric', 'voting', 'electoral',
                   'არჩევნები', 'ხმის', 'ბიომეტრ']
    for url in urls_to_try:
        try:
            r = session.get(url, headers={**HEADERS, 'Accept': 'text/html'},
                            timeout=20, verify=False)
            if r.status_code != 200 or len(r.text) < 500:
                continue
            soup = BeautifulSoup(r.text, 'lxml')
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                href = a['href']
                if not title or len(title) < 8:
                    continue
                full_url = href if href.startswith('http') else f'{BASE}{href}'
                parent = (a.parent or a).get_text(' ', strip=True)[:300]
                combined = f"{title} {parent}".lower()
                if not any(k.lower() in combined for k in ELECTION_KW):
                    continue
                results.append({'title': title, 'url': full_url, 'snippet': parent,
                                'buyer': '', 'pub': '', 'deadline': '', 'status': 'Open'})
            if results:
                break
        except Exception as e:
            print(f'  [spa_georgia] HTML error ({url}): {e}')
    return results


def _parse_api_item(item):
    title = (item.get('nameEn') or item.get('name') or item.get('title') or
             item.get('subject') or '').strip()
    title_ka = (item.get('nameKa') or item.get('nameGe') or '').strip()
    proc_id = item.get('id') or item.get('tenderId') or ''
    url = item.get('url') or (f'{BASE}/en/public/procurement/{proc_id}' if proc_id else BASE)
    buyer_d = item.get('organizationName') or item.get('buyer') or item.get('authority') or ''
    buyer = (buyer_d.get('nameEn') or buyer_d.get('name') or buyer_d) if isinstance(buyer_d, dict) else str(buyer_d)
    pub = (item.get('publishDate') or item.get('publicationDate') or item.get('startDate') or '')[:10]
    deadline = (item.get('deadline') or item.get('submissionDeadline') or item.get('endDate') or '')[:10]
    status = item.get('status') or item.get('statusName') or 'Open'
    return title, title_ka, url, str(buyer), pub, deadline, str(status)


def parse(country='Georgia', iso3='GEO'):
    session = requests.Session()
    seen = set()
    results = []

    api_found = False
    for kw in KEYWORDS:
        items, _source = _api_search(session, kw)
        if not items:
            continue
        api_found = True
        for item in items:
            if not isinstance(item, dict):
                continue
            title, title_ka, url, buyer, pub, deadline, status = _parse_api_item(item)
            if not title and title_ka:
                title = title_ka
            if not title or url in seen:
                continue
            seen.add(url)
            snippet = f"{title} | {buyer}"
            s = score(title, snippet)
            title_en = title if title.isascii() else translate_to_en(title_ka or title, sl='ka')
            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title_ka or title, 'title_en': title_en, 'url': url,
                'published_date': pub, 'deadline_date': deadline,
                'status': status, 'buyer': buyer or 'SPA Georgia',
                'amount': None, 'currency': 'GEL',
                'snippet': snippet[:300], 'score': s,
            })

    if not api_found:
        for row in _html_scrape(session):
            t = row['title']
            u = row['url']
            if not t or u in seen:
                continue
            seen.add(u)
            s = score(t, row['snippet'])
            title_en = translate_to_en(t, sl='ka') if not t.isascii() else t
            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': t, 'title_en': title_en, 'url': u,
                'published_date': row['pub'], 'deadline_date': row['deadline'],
                'status': row['status'], 'buyer': row['buyer'] or 'SPA Georgia',
                'amount': None, 'currency': 'GEL',
                'snippet': row['snippet'][:300], 'score': s,
            })

    print(f'  [spa_georgia] {len(results)} notices found')
    return results
