"""Mongolia — GPA e-Tender (tender.gov.mn)
Portal: https://tender.gov.mn
REST API or HTML scraping. Mongolian (mn) → English translation.
"""
import re
import requests
import urllib3
urllib3.disable_warnings()
from bs4 import BeautifulSoup
from crawler.keywords import score
from crawler.translate import translate_to_en


def _extract_date(text):
    """Extract first YYYY-MM-DD date from raw text."""
    m = re.search(r'\d{4}-\d{2}-\d{2}', text or '')
    return m.group(0) if m else ''

BASE = 'https://tender.gov.mn'
PORTAL = 'tender.gov.mn'

KEYWORDS_EN = ['election', 'ballot', 'voting', 'biometric', 'voter']
KEYWORDS_MN = ['сонгуул', 'санал хураалт', 'биометр', 'сонгогч']  # election, voting, biometric, voter

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/html, */*;q=0.8',
    'Accept-Language': 'mn,en;q=0.9',
}


def _try_api(session, keyword):
    """Try REST API endpoints."""
    api_urls = [
        (f'{BASE}/api/v1/tender/search', {'q': keyword, 'page': 1, 'limit': 50}),
        (f'{BASE}/api/tender', {'keyword': keyword, 'status': 'open', 'page': 1, 'pageSize': 50}),
        (f'{BASE}/api/v2/tenders', {'search': keyword, 'page': 0, 'size': 50}),
    ]
    for url, params in api_urls:
        try:
            r = session.get(url, params=params,
                            headers={**HEADERS, 'Accept': 'application/json'},
                            timeout=15, verify=False)
            if r.status_code == 200 and 'application/json' in r.headers.get('content-type', ''):
                data = r.json()
                items = (data.get('data') or data.get('items') or data.get('tenders')
                         or data.get('content') or (data if isinstance(data, list) else None))
                if items:
                    return items
        except Exception:
            continue
    return None


def _scrape_html(session, keyword=''):
    """Scrape search HTML page."""
    rows = []
    search_urls = [
        f'{BASE}/en/tender/list',
        f'{BASE}/tender/list',
        f'{BASE}/search?q={keyword}' if keyword else f'{BASE}/',
        BASE,
    ]
    for url in search_urls:
        try:
            r = session.get(url, headers={**HEADERS, 'Accept': 'text/html'},
                            timeout=20, verify=False)
            if r.status_code != 200 or len(r.text) < 500:
                continue
            soup = BeautifulSoup(r.text, 'lxml')

            # Tables
            for table in soup.find_all('table'):
                for tr in table.find_all('tr')[1:]:
                    tds = tr.find_all('td')
                    if not tds:
                        continue
                    a = tr.find('a', href=True)
                    title = a.get_text(strip=True) if a else tds[0].get_text(strip=True)
                    href = a['href'] if a else ''
                    link = (href if href.startswith('http') else f'{BASE}{href}') if href else url
                    td_texts = [td.get_text(strip=True) for td in tds]
                    # td[1] contains deadline datetime; td[2] contains "Зарласан огноо<date>" (published)
                    raw1 = td_texts[1] if len(td_texts) > 1 else ''
                    raw2 = td_texts[2] if len(td_texts) > 2 else ''
                    pub = _extract_date(raw2) or _extract_date(raw1)
                    deadline = _extract_date(raw1) if _extract_date(raw1) != pub else ''
                    rows.append({'title': title, 'url': link,
                                 'snippet': (title + ' | ' + ' '.join(td_texts[1:3]))[:300],
                                 'pub': pub, 'deadline': deadline})

            # Cards
            if not rows:
                for card in soup.find_all(['div', 'article'], class_=lambda c: c and any(
                        x in (c if isinstance(c, str) else ' '.join(c))
                        for x in ['tender', 'item', 'list-item', 'card'])):
                    a = card.find('a', href=True)
                    if not a:
                        continue
                    title = a.get_text(strip=True)
                    href = a['href']
                    link = href if href.startswith('http') else f'{BASE}{href}'
                    rows.append({'title': title, 'url': link,
                                 'snippet': card.get_text(' ', strip=True)[:200],
                                 'pub': '', 'deadline': ''})

            if rows:
                break
        except Exception as e:
            print(f'  [gpa_mongolia] error ({url}): {e}')

    return rows


def _parse_api_item(item):
    title_mn = (item.get('name') or item.get('title') or item.get('subject') or '').strip()
    title_en = (item.get('nameEn') or item.get('titleEn') or '').strip()
    proc_id = item.get('id') or item.get('tenderId') or ''
    url = item.get('url') or item.get('link') or (f'{BASE}/en/tender/{proc_id}' if proc_id else BASE)
    buyer = item.get('organization') or item.get('buyer') or item.get('authority') or ''
    if isinstance(buyer, dict):
        buyer = buyer.get('name') or buyer.get('nameEn') or ''
    pub = (item.get('publishedDate') or item.get('startDate') or item.get('createdAt') or '')[:10]
    deadline = (item.get('deadline') or item.get('endDate') or item.get('closingDate') or '')[:10]
    status = item.get('status') or 'Open'
    return title_mn, title_en, url, str(buyer), pub, deadline, str(status)


def parse(country='Mongolia', iso3='MNG'):
    session = requests.Session()
    seen = set()
    results = []

    all_keywords = KEYWORDS_EN + KEYWORDS_MN
    for kw in all_keywords:
        items = _try_api(session, kw)
        if items:
            for item in items:
                if not isinstance(item, dict):
                    continue
                title_mn, title_en_api, url, buyer, pub, deadline, status = _parse_api_item(item)
                if not title_mn or url in seen:
                    continue
                seen.add(url)
                snippet = f"{title_mn} | {buyer}"
                s = score(title_mn, snippet)
                if not s and title_en_api:
                    s = score(title_en_api, snippet)
                title_en = title_en_api or translate_to_en(title_mn, sl='mn')
                results.append({
                    'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                    'title': title_mn, 'title_en': title_en, 'url': url,
                    'published_date': pub, 'deadline_date': deadline,
                    'status': status, 'buyer': buyer or 'GEC Mongolia',
                    'amount': None, 'currency': 'MNT',
                    'snippet': snippet[:300], 'score': s,
                })
        else:
            # HTML fallback (once, with empty keyword for full list)
            break

    if not results:
        rows = _scrape_html(session)
        for row in rows:
            title = row['title']
            url = row['url']
            if not title or url in seen:
                continue
            seen.add(url)
            snippet = row['snippet']
            s = score(title, snippet)
            title_en = translate_to_en(title, sl='mn')
            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'title_en': title_en, 'url': url,
                'published_date': row['pub'], 'deadline_date': row['deadline'],
                'status': 'Open', 'buyer': 'GEC Mongolia',
                'amount': None, 'currency': 'MNT',
                'snippet': snippet[:300], 'score': s,
            })

    print(f'  [gpa_mongolia] {len(results)} notices found')
    return results
