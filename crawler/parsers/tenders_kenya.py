"""Kenya — tenders.go.ke (Vue SPA with JSON API fallback)"""
import re
import requests
from bs4 import BeautifulSoup
from crawler.keywords import score, is_election_related

import urllib3
urllib3.disable_warnings()

BASE = 'https://tenders.go.ke'
PORTAL = 'tenders.go.ke'
# Try API endpoints (Vue SPA often exposes /api routes)
API_ENDPOINTS = [
    f'{BASE}/api/v1/tenders',
    f'{BASE}/api/tenders',
    f'{BASE}/api/v1/procurements',
]
HTML_ENDPOINTS = [
    f'{BASE}/website/tenders/index',
    f'{BASE}',
]
KEYWORDS = ['election', 'iebc', 'biometric', 'voter', 'ballot', 'electoral',
            'voting machine', 'registration kit', 'bvr', 'kie']

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/html,*/*;q=0.9',
    'Referer': BASE,
}


def _is_election_row(title):
    t = title.lower()
    return any(k in t for k in KEYWORDS)


def _fetch(session, url, as_json=False):
    try:
        h = dict(HEADERS)
        if as_json:
            h['Accept'] = 'application/json'
        r = session.get(url, headers=h, timeout=30, verify=False)
        r.raise_for_status()
        if as_json:
            return r.json()
        return r.text
    except Exception as e:
        print(f'  [tenders_kenya] fetch error ({url}): {e}')
        return None


def _try_api(session):
    results = []
    for endpoint in API_ENDPOINTS:
        # Try with election keywords
        for kw in ['election', 'IEBC', 'biometric voter', 'ballot']:
            data = _fetch(session, endpoint, as_json=True)
            if not data:
                data = _fetch(session, f'{endpoint}?search={kw}', as_json=True)
            if not data:
                continue
            # Handle various API response shapes
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                for key in ('data', 'tenders', 'results', 'items'):
                    if key in data:
                        items = data[key]
                        if isinstance(items, list):
                            break
            for item in items:
                if not isinstance(item, dict):
                    continue
                title = (item.get('title') or item.get('name') or item.get('tender_name') or '').strip()
                if not title or not _is_election_row(title):
                    continue
                url = item.get('url') or item.get('link') or item.get('detail_url') or BASE
                pub = item.get('published_date') or item.get('created_at') or item.get('date') or ''
                deadline = item.get('closing_date') or item.get('deadline') or item.get('end_date') or ''
                buyer = item.get('entity') or item.get('procuring_entity') or item.get('buyer') or 'Government of Kenya'
                snippet = f"{buyer} | {pub} | {deadline}"
                results.append({
                    'title': title, 'url': url,
                    'published_date': pub[:10] if pub else '',
                    'deadline_date': deadline[:10] if deadline else '',
                    'buyer': buyer, 'snippet': snippet,
                })
            if results:
                return results
    return results


def _try_html(session):
    results = []
    for endpoint in HTML_ENDPOINTS:
        html = _fetch(session, endpoint)
        if not html:
            continue
        soup = BeautifulSoup(html, 'lxml')
        for table in soup.find_all('table'):
            for tr in table.find_all('tr')[1:]:
                tds = tr.find_all('td')
                if len(tds) < 2:
                    continue
                link = tr.find('a', href=True)
                title = link.get_text(strip=True) if link else tds[0].get_text(strip=True)
                if not title or not _is_election_row(title):
                    continue
                href = link['href'] if link else ''
                url = (BASE + href) if href and href.startswith('/') else (href or BASE)
                td_texts = [td.get_text(strip=True) for td in tds]
                results.append({
                    'title': title, 'url': url,
                    'published_date': td_texts[2] if len(td_texts) > 2 else '',
                    'deadline_date': td_texts[3] if len(td_texts) > 3 else '',
                    'buyer': td_texts[1] if len(td_texts) > 1 else 'Government of Kenya',
                    'snippet': ' | '.join(td_texts[:5]),
                })
        if results:
            break
    return results


def parse(country='Kenya', iso3='KEN'):
    session = requests.Session()

    rows = _try_api(session)
    if not rows:
        rows = _try_html(session)

    seen = set()
    results = []
    for row in rows:
        title = row['title']
        url = row['url']
        if not title or url in seen:
            continue
        seen.add(url)
        snippet = row.get('snippet', title)
        results.append({
            'country': country, 'iso3': iso3, 'portal_name': PORTAL,
            'title': title, 'url': url,
            'published_date': row.get('published_date', ''),
            'deadline_date': row.get('deadline_date', ''),
            'status': 'Open',
            'buyer': row.get('buyer', 'Government of Kenya'),
            'amount': None, 'currency': 'KES',
            'snippet': snippet[:300],
            'score': score(title, snippet),
        })

    print(f'  [tenders_kenya] {len(results)} notices found')
    return results
