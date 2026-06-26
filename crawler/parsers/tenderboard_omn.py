"""Oman — Tender Board (tenderboard.gov.om)
Portal: https://www.tenderboard.gov.om
HTML table scraping + Arabic→English translation, similar to Bahrain.
"""
import requests
import urllib3
urllib3.disable_warnings()
from bs4 import BeautifulSoup
from crawler.keywords import score
from crawler.translate import translate_to_en

BASE = 'https://www.tenderboard.gov.om'
PORTAL = 'tenderboard.gov.om'

SEARCH_PATHS = [
    '/Tenders',
    '/OpenTenders',
    '/en/Tenders',
    '/Home/OpenTenders',
    '/tenders',
    '/',
]

ELECTION_KEYWORDS_AR = [
    'انتخاب', 'اقتراع', 'ناخب', 'بطاقة', 'تصويت', 'لجنة الانتخابات',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
}


def _try_api(session):
    """Try JSON API endpoints first."""
    api_urls = [
        f'{BASE}/api/v1/tenders',
        f'{BASE}/api/tenders/open',
        f'{BASE}/WebAPI/api/Tender/GetOpenTenders',
    ]
    for url in api_urls:
        try:
            r = session.get(url, headers={**HEADERS, 'Accept': 'application/json'},
                            timeout=15, verify=False)
            if r.status_code == 200 and r.headers.get('content-type', '').startswith('application/json'):
                return r.json()
        except Exception:
            continue
    return None


def _scrape_html(session):
    """Scrape HTML table pages."""
    rows = []
    for path in SEARCH_PATHS:
        try:
            r = session.get(f'{BASE}{path}', headers=HEADERS, timeout=20, verify=False)
            if r.status_code != 200 or len(r.text) < 500:
                continue
            soup = BeautifulSoup(r.text, 'lxml')
            tables = soup.find_all('table')
            if not tables:
                # Try div-based listings
                for card in soup.find_all(['div', 'li'], class_=lambda c: c and 'tender' in c.lower()):
                    a = card.find('a', href=True)
                    if not a:
                        continue
                    title = a.get_text(strip=True)
                    href = a['href']
                    url = href if href.startswith('http') else f'{BASE}{href}'
                    rows.append({'title': title, 'url': url,
                                 'tds': [card.get_text(' ', strip=True)[:200]]})
                if rows:
                    break
                continue

            for table in tables:
                for tr in table.find_all('tr')[1:]:
                    tds = tr.find_all('td')
                    if not tds:
                        continue
                    a = tr.find('a', href=True)
                    title = a.get_text(strip=True) if a else tds[0].get_text(strip=True)
                    href = a['href'] if a else ''
                    url = (f'{BASE}{href}' if href and not href.startswith('http') else href) or f'{BASE}{path}'
                    rows.append({'title': title, 'url': url,
                                 'tds': [td.get_text(strip=True) for td in tds]})

            if rows:
                break
        except Exception as e:
            print(f'  [tenderboard_omn] error ({path}): {e}')

    return rows


def parse(country='Oman', iso3='OMN'):
    session = requests.Session()
    seen = set()
    results = []

    # Try JSON API first
    json_data = _try_api(session)
    if json_data and isinstance(json_data, list):
        for item in json_data:
            title = (item.get('tenderTitle') or item.get('title') or item.get('name') or '').strip()
            if not title:
                continue
            url = item.get('url') or item.get('link') or BASE
            if url in seen:
                continue
            seen.add(url)
            snippet = str(item)[:300]
            s = score(title, snippet)
            title_en = translate_to_en(title, sl='ar') if not title.isascii() else title
            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'title_en': title_en, 'url': url,
                'published_date': (item.get('publishDate') or '')[:10],
                'deadline_date': (item.get('deadline') or item.get('closingDate') or '')[:10],
                'status': item.get('status') or 'Open',
                'buyer': item.get('ministry') or item.get('buyer') or 'Tender Board Oman',
                'amount': None, 'currency': 'OMR',
                'snippet': snippet, 'score': s,
            })
    else:
        rows = _scrape_html(session)
        for row in rows:
            title = row['title']
            url = row['url']
            if not title or url in seen or len(title) < 5:
                continue
            seen.add(url)
            tds = row['tds']
            snippet = ' | '.join(tds[:4])

            # For HTML scraping include ALL tenders (no keyword filter) — like Bahrain
            s = score(title, snippet)
            title_en = translate_to_en(title, sl='ar') if not title.isascii() else title
            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'title_en': title_en, 'url': url,
                'published_date': tds[1] if len(tds) > 1 else '',
                'deadline_date': tds[3] if len(tds) > 3 else '',
                'status': 'Open',
                'buyer': 'Tender Board Oman',
                'amount': None, 'currency': 'OMR',
                'snippet': snippet[:300], 'score': s,
            })

    print(f'  [tenderboard_omn] {len(results)} notices found')
    return results
