"""Bosnia and Herzegovina — eJN (e-Javne Nabavke)
Portal: https://www.ejn.gov.ba
HTML table scraping + Bosnian→English translation.
"""
import requests
import urllib3
urllib3.disable_warnings()
from bs4 import BeautifulSoup
from crawler.keywords import score
from crawler.translate import translate_to_en

BASE = 'https://www.ejn.gov.ba'
PORTAL = 'ejn.gov.ba'

SEARCH_PATHS = [
    '/tender/search.aspx?Status=2&SubStatus=0',    # active tenders
    '/tender/search.aspx',
    '/ponude',
    '/en/tender/search',
    '/',
]

ELECTION_KW_BS = [
    'izbor', 'glasanje', 'bilja', 'birač', 'izborne', 'komisija',
    'CIK', 'Centralna izborna komisija', 'election', 'ballot',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
    'Accept-Language': 'bs,hr,sr,en;q=0.8',
}


def _is_election_related(text):
    t = text.lower()
    return any(k.lower() in t for k in ELECTION_KW_BS + [
        'election', 'ballot', 'vote', 'biometric', 'cik',
    ])


def _scrape_path(session, path):
    rows = []
    try:
        r = session.get(f'{BASE}{path}', headers=HEADERS, timeout=20, verify=False)
        if r.status_code != 200 or len(r.text) < 500:
            return rows
        soup = BeautifulSoup(r.text, 'lxml')

        for table in soup.find_all('table'):
            for tr in table.find_all('tr')[1:]:
                tds = tr.find_all('td')
                if len(tds) < 2:
                    continue
                a = tr.find('a', href=True)
                title = a.get_text(strip=True) if a else tds[0].get_text(strip=True)
                href = a['href'] if a else ''
                url = (href if href.startswith('http')
                       else f'{BASE}{href}') if href else f'{BASE}{path}'
                td_texts = [td.get_text(strip=True) for td in tds]
                rows.append({
                    'title': title, 'url': url,
                    'snippet': ' | '.join(td_texts[:4]),
                    'pub': td_texts[1] if len(td_texts) > 1 else '',
                    'deadline': td_texts[3] if len(td_texts) > 3 else '',
                    'buyer': td_texts[0] if td_texts else '',
                })

        # div/article listings
        if not rows:
            for card in soup.find_all(['div', 'article', 'li'], class_=lambda c: c and any(
                    x in (c if isinstance(c, str) else ' '.join(c))
                    for x in ['tender', 'nabavk', 'ponud', 'notice'])):
                a = card.find('a', href=True)
                if not a:
                    continue
                title = a.get_text(strip=True)
                href = a['href']
                url = href if href.startswith('http') else f'{BASE}{href}'
                rows.append({
                    'title': title, 'url': url,
                    'snippet': card.get_text(' ', strip=True)[:300],
                    'pub': '', 'deadline': '', 'buyer': '',
                })
    except Exception as e:
        print(f'  [ejn_bosnia] error ({path}): {e}')
    return rows


def parse(country='Bosnia and Herzegovina', iso3='BIH'):
    session = requests.Session()
    seen = set()
    results = []

    for path in SEARCH_PATHS:
        rows = _scrape_path(session, path)
        for row in rows:
            title = row['title']
            url = row['url']
            if not title or len(title) < 6 or url in seen:
                continue
            seen.add(url)

            snippet = row['snippet']
            s = score(title, snippet)
            if s <= 0 and not _is_election_related(f"{title} {snippet}"):
                continue
            if s <= 0:
                s = 15

            title_en = translate_to_en(title, sl='bs')
            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'title_en': title_en, 'url': url,
                'published_date': row['pub'], 'deadline_date': row['deadline'],
                'status': 'Open',
                'buyer': row['buyer'] or 'CIK Bosnia',
                'amount': None, 'currency': 'BAM',
                'snippet': snippet[:300], 'score': s,
            })

        if results:
            break

    print(f'  [ejn_bosnia] {len(results)} notices found')
    return results
