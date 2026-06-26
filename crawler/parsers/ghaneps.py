"""Ghana — GHANEPS (Struts HTML table parser)"""
import requests
from bs4 import BeautifulSoup
from crawler.keywords import score

SEARCH_URL = 'https://www.ghaneps.gov.gh/epps/quickSearchAction.do'
DETAIL_BASE = 'https://www.ghaneps.gov.gh/epps/'
PORTAL = 'ghaneps.gov.gh'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Referer': 'https://www.ghaneps.gov.gh/epps/home.do',
}


def _fetch_page(session, page=1):
    try:
        r = session.get(SEARCH_URL, params={
            'searchSelect': '6',   # All open tenders
            'searchString': 'election',
            'pageNo': page,
        }, headers=HEADERS, timeout=30, verify=False)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f'  [ghaneps] fetch error (page {page}): {e}')
        return ''


def _parse_html(html):
    soup = BeautifulSoup(html, 'lxml')
    rows = []
    table = soup.find('table', {'class': lambda c: c and 'search' in c.lower()}) \
             or soup.find('table', id=lambda i: i and 'result' in (i or '').lower()) \
             or soup.find('table')
    if not table:
        return rows, 0

    for tr in table.find_all('tr')[1:]:
        tds = tr.find_all('td')
        if len(tds) < 3:
            continue
        link_tag = tr.find('a', href=True)
        title = link_tag.get_text(strip=True) if link_tag else tds[1].get_text(strip=True)
        href = link_tag['href'] if link_tag else ''
        url = (DETAIL_BASE + href.lstrip('/')) if href and not href.startswith('http') else href
        rows.append({'title': title, 'url': url, 'tds': [td.get_text(strip=True) for td in tds]})

    # total pages
    total_pages = 1
    nav = soup.find(string=lambda t: t and 'Page' in t and 'of' in t)
    if nav:
        try:
            total_pages = int(nav.split('of')[-1].strip().split()[0])
        except Exception:
            pass
    return rows, total_pages


def parse(country='Ghana', iso3='GHA'):
    import urllib3
    urllib3.disable_warnings()
    session = requests.Session()

    results = []
    seen = set()

    html = _fetch_page(session, 1)
    if not html:
        print('  [ghaneps] no response')
        return []

    rows, total_pages = _parse_html(html)
    all_rows = list(rows)

    for p in range(2, min(total_pages + 1, 11)):
        html = _fetch_page(session, p)
        r, _ = _parse_html(html)
        all_rows.extend(r)

    for row in all_rows:
        title = row['title']
        url = row['url']
        if not title or url in seen:
            continue
        seen.add(url)
        tds = row['tds']
        snippet = ' | '.join(tds[:4]) if tds else ''
        results.append({
            'country': country, 'iso3': iso3, 'portal_name': PORTAL,
            'title': title, 'url': url,
            'published_date': tds[2] if len(tds) > 2 else '',
            'deadline_date': tds[3] if len(tds) > 3 else '',
            'status': tds[-1] if tds else '',
            'buyer': tds[1] if len(tds) > 1 else '',
            'amount': None, 'currency': 'GHS',
            'snippet': snippet[:300],
            'score': score(title, snippet),
        })

    print(f'  [ghaneps] {len(results)} notices found')
    return results
