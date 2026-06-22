"""WordPress REST API portals — Bhutan ECB, Albania KQZ"""
import requests
from crawler.keywords import score, is_election_related

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; MiruIntelBot/1.0)'}

PORTALS = {
    'ecb_bhutan': {
        'base': 'https://www.ecb.bt',
        'api':  'https://www.ecb.bt/wp-json/wp/v2/posts',
        'params': {'per_page': 50, 'search': 'tender'},
        'portal_name': 'ecb.bt',
        'country': 'Bhutan', 'iso3': 'BTN', 'currency': 'BTN',
    },
    'kqz_albania': {
        'base': 'https://kqz.gov.al',
        'api':  'https://kqz.gov.al/wp-json/wp/v2/posts',
        'params': {'per_page': 50, 'search': 'prokurimi'},
        'portal_name': 'kqz.gov.al',
        'country': 'Albania', 'iso3': 'ALB', 'currency': 'ALL',
    },
}


def _fetch_wp(cfg):
    results = []
    try:
        r = requests.get(cfg['api'], params=cfg['params'], headers=HEADERS, timeout=30, verify=False)
        r.raise_for_status()
        posts = r.json()
    except Exception as e:
        print(f"  [wp:{cfg['portal_name']}] error: {e}")
        return []

    for post in posts:
        title = post.get('title', {}).get('rendered', '').strip()
        url = post.get('link', '')
        snippet = post.get('excerpt', {}).get('rendered', '')
        snippet = BeautifulSoup_strip(snippet)

        if not title or not is_election_related(title, snippet):
            continue

        date = post.get('date', '')[:10]
        results.append({
            'country': cfg['country'], 'iso3': cfg['iso3'],
            'portal_name': cfg['portal_name'],
            'title': title, 'url': url,
            'published_date': date, 'deadline_date': '',
            'status': post.get('status', ''),
            'buyer': cfg['country'] + ' Electoral Commission',
            'amount': None, 'currency': cfg['currency'],
            'snippet': snippet[:300],
            'score': score(title, snippet),
        })
    return results


def BeautifulSoup_strip(html: str) -> str:
    """Strip HTML tags from a string."""
    try:
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, 'lxml').get_text(strip=True)
    except Exception:
        import re
        return re.sub(r'<[^>]+>', '', html).strip()


def parse_ecb_bhutan(country='Bhutan', iso3='BTN'):
    import urllib3
    urllib3.disable_warnings()
    results = _fetch_wp(PORTALS['ecb_bhutan'])
    print(f'  [ecb_bhutan] {len(results)} notices found')
    return results


def parse_kqz_albania(country='Albania', iso3='ALB'):
    import urllib3
    urllib3.disable_warnings()
    results = _fetch_wp(PORTALS['kqz_albania'])
    print(f'  [kqz_albania] {len(results)} notices found')
    return results
