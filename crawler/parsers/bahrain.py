"""Bahrain — Tender Board (HTML table parser)"""
import requests
from bs4 import BeautifulSoup
from crawler.keywords import score, is_election_related

BASE = 'https://etendering.tenderboard.gov.bh'
SEARCH_URLS = [
    f'{BASE}/',
    f'{BASE}/Home/PublishedOpenTenders',
    f'{BASE}/Tender/List',
]
PORTAL = 'tenderboard.gov.bh'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}


def _fetch(session, url):
    try:
        r = session.get(url, headers=HEADERS, timeout=30, verify=False)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f'  [bahrain] fetch error ({url}): {e}')
        return ''


def _parse_table(html, url_base):
    soup = BeautifulSoup(html, 'lxml')
    results = []
    for table in soup.find_all('table'):
        for tr in table.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if len(tds) < 2:
                continue
            link = tr.find('a', href=True)
            title = link.get_text(strip=True) if link else tds[0].get_text(strip=True)
            href = link['href'] if link else ''
            url = (url_base + href) if href and not href.startswith('http') else (href or url_base)
            td_texts = [td.get_text(strip=True) for td in tds]
            results.append({'title': title, 'url': url, 'tds': td_texts})
    return results


def parse(country='Bahrain', iso3='BHR'):
    import urllib3
    urllib3.disable_warnings()
    session = requests.Session()

    all_rows = []
    for search_url in SEARCH_URLS:
        html = _fetch(session, search_url)
        if html:
            rows = _parse_table(html, BASE)
            all_rows.extend(rows)
            if rows:
                break  # found working URL

    seen = set()
    results = []
    for row in all_rows:
        title = row['title']
        url = row['url']
        if not title or url in seen:
            continue
        seen.add(url)
        tds = row['tds']
        snippet = ' | '.join(tds[:4])
        if not is_election_related(title, snippet):
            continue

        results.append({
            'country': country, 'iso3': iso3, 'portal_name': PORTAL,
            'title': title, 'url': url,
            'published_date': tds[1] if len(tds) > 1 else '',
            'deadline_date': tds[3] if len(tds) > 3 else '',
            'status': 'Open',
            'buyer': 'Tender Board Bahrain',
            'amount': None, 'currency': 'BHD',
            'snippet': snippet[:300],
            'score': score(title, snippet),
        })

    print(f'  [bahrain] {len(results)} notices found')
    return results
