"""Philippines — PhilGEPS (HTML table, no login required)"""
import re
import requests
from bs4 import BeautifulSoup
from crawler.keywords import score, is_election_related

import urllib3
urllib3.disable_warnings()

BASE = 'https://philgeps.gov.ph'
ENDPOINTS = [
    f'{BASE}/Indexes/index',
    f'{BASE}/Indexes/getFormerOpportunities',
    f'{BASE}/Indexes/getAwardNotices',
]
PORTAL = 'philgeps.gov.ph'
KEYWORDS = ['election', 'comelec', 'voting', 'ballot', 'precinct', 'biometric',
            'automated count', 'electoral', 'canvassing', 'vcm', 'acm', 'vvpat']

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}


def _fetch(session, url, params=None):
    try:
        r = session.get(url, headers=HEADERS, params=params, timeout=30, verify=False)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f'  [philgeps] fetch error ({url}): {e}')
        return ''


def _is_election_row(title):
    t = title.lower()
    return any(k in t for k in KEYWORDS)


def _parse_table(html, base_url):
    soup = BeautifulSoup(html, 'lxml')
    rows = []
    for table in soup.find_all('table'):
        headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
        if not headers:
            continue
        for tr in table.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if len(tds) < 3:
                continue
            link = tr.find('a', href=True)
            title = link.get_text(strip=True) if link else tds[1].get_text(strip=True) if len(tds) > 1 else ''
            href = link['href'] if link else ''
            url = (base_url + href) if href and href.startswith('/') else (href or base_url)
            td_texts = [td.get_text(strip=True) for td in tds]
            rows.append({'title': title, 'url': url, 'tds': td_texts, 'cols': headers})
    return rows


def _extract_date(text):
    # Handles MM/DD/YYYY or YYYY-MM-DD
    m = re.search(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', text)
    return m.group(0) if m else ''


def parse(country='Philippines', iso3='PHL'):
    session = requests.Session()
    all_rows = []

    for endpoint in ENDPOINTS:
        page = 1
        while page <= 5:
            params = {'page': page} if page > 1 else None
            html = _fetch(session, endpoint, params)
            if not html:
                break
            rows = _parse_table(html, BASE)
            if not rows:
                break
            election_rows = [r for r in rows if _is_election_row(r['title'])]
            all_rows.extend(election_rows)
            # Stop paginating if we got few rows (likely last page)
            if len(rows) < 10:
                break
            page += 1

    seen = set()
    results = []
    for row in all_rows:
        title = row['title']
        url = row['url']
        if not title or url in seen:
            continue
        seen.add(url)
        tds = row['tds']
        snippet = ' | '.join(tds[:5])
        # Try to extract dates — typical order: title, mode, classification, agency, publish_date, close_date
        pub_date = _extract_date(tds[4]) if len(tds) > 4 else ''
        deadline = _extract_date(tds[5]) if len(tds) > 5 else ''
        agency = tds[3] if len(tds) > 3 else ''

        results.append({
            'country': country, 'iso3': iso3, 'portal_name': PORTAL,
            'title': title, 'url': url,
            'published_date': pub_date,
            'deadline_date': deadline,
            'status': tds[-1] if tds else 'Active',
            'buyer': agency,
            'amount': None, 'currency': 'PHP',
            'snippet': snippet[:300],
            'score': score(title, snippet),
        })

    print(f'  [philgeps] {len(results)} notices found')
    return results
