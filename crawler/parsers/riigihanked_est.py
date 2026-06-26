"""Estonia — Riigihangete Register (State Procurement Register)
Portal: https://riigihanked.riik.ee
API: REST v3/v4 public procurement search
"""
import requests
import urllib3
urllib3.disable_warnings()
from crawler.keywords import score
from crawler.translate import translate_to_en

BASE = 'https://riigihanked.riik.ee'
PORTAL = 'riigihanked.riik.ee'

KEYWORDS_ET = [
    'valimine', 'valimiskomisjon', 'hääletus', 'valimissüsteem',
    'election', 'e-voting', 'biometric',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'et,en;q=0.9',
}


def _search_v4(session, keyword):
    """Try RHR API v4 search endpoint."""
    try:
        r = session.get(
            f'{BASE}/rhr/api/v4/procurements/public',
            params={'page': 0, 'pageSize': 50, 'keyword': keyword},
            headers=HEADERS, timeout=20, verify=False,
        )
        if r.status_code == 200:
            data = r.json()
            return data.get('content') or data.get('items') or (data if isinstance(data, list) else [])
    except Exception:
        pass
    return None


def _search_v3(session, keyword):
    """Fallback: RHR API v3."""
    try:
        r = session.get(
            f'{BASE}/rhr/api/v3/procurements/public',
            params={'page': 0, 'pageSize': 50, 'keyword': keyword, 'status': 'ACTIVE'},
            headers=HEADERS, timeout=20, verify=False,
        )
        if r.status_code == 200:
            data = r.json()
            return data.get('content') or data.get('items') or (data if isinstance(data, list) else [])
    except Exception:
        pass
    return None


def _search_html(session, keyword):
    """Last resort: scrape the search HTML pages (EN + ET paths)."""
    from bs4 import BeautifulSoup
    results = []
    paths = [
        f'{BASE}/rhr/en/public-procurement?keyword={keyword}',
        f'{BASE}/rhr/et/riigihanked?keyword={keyword}',
        f'{BASE}/rhr/en/public-procurement/notices?keyword={keyword}',
        BASE,
    ]
    for url in paths:
        try:
            r = session.get(url, headers={**HEADERS, 'Accept': 'text/html'},
                            timeout=20, verify=False)
            if r.status_code != 200 or len(r.text) < 500:
                continue
            soup = BeautifulSoup(r.text, 'lxml')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/procurement/' not in href and '/rhr/' not in href and '/hanked/' not in href:
                    continue
                title = a.get_text(strip=True)
                if not title or len(title) < 8:
                    continue
                full_url = href if href.startswith('http') else f'{BASE}{href}'
                parent = (a.parent or a).get_text(' ', strip=True)[:200]
                results.append({'title': title, 'url': full_url, 'buyer': '',
                                'pub': '', 'deadline': '', 'snippet': parent})
            if results:
                break
        except Exception as e:
            print(f'  [riigihanked] HTML error ({url}): {e}')
    return results


def _parse_item(item):
    """Extract fields from API response item (v3/v4 format)."""
    # v4 format
    title = (item.get('subject') or item.get('title') or item.get('name') or '').strip()
    proc_id = item.get('id') or item.get('procurementId') or ''
    url = item.get('url') or (f'{BASE}/rhr/en/public-procurement/{proc_id}' if proc_id else BASE)
    buyer = item.get('authority') or item.get('contractingAuthority') or ''
    if isinstance(buyer, dict):
        buyer = buyer.get('name') or buyer.get('registryCode') or ''
    pub = (item.get('publicationDate') or item.get('publishDate') or '')[:10]
    deadline = (item.get('submissionDeadline') or item.get('deadline') or '')[:10]
    status = item.get('status') or 'Open'
    return title, url, str(buyer), pub, deadline, str(status)


def parse(country='Estonia', iso3='EST'):
    session = requests.Session()
    seen = set()
    results = []

    for kw in KEYWORDS_ET:
        items = _search_v4(session, kw)
        if items is None:
            items = _search_v3(session, kw)
        if items is None:
            items = _search_html(session, kw)

        if not items:
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            # HTML scrape results have different keys than API results
            if 'snippet' in item:
                title = item.get('title', '')
                url = item.get('url', '')
                buyer = item.get('buyer', '')
                pub = item.get('pub', '')
                deadline = item.get('deadline', '')
                status = 'Open'
            else:
                title, url, buyer, pub, deadline, status = _parse_item(item)

            if not title or url in seen:
                continue
            seen.add(url)

            snippet = item.get('snippet') or f"{title} | {buyer}"
            s = score(title, snippet)
            title_en = translate_to_en(title, sl='et')

            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'title_en': title_en, 'url': url,
                'published_date': pub, 'deadline_date': deadline,
                'status': status,
                'buyer': buyer or 'Riigi Valimisteenistus',
                'amount': None, 'currency': 'EUR',
                'snippet': snippet[:300], 'score': s,
            })

    print(f'  [riigihanked] {len(results)} notices found')
    return results
