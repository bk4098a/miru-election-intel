"""DRC (Congo) — ARMP marchepublic.cd
Portal: https://www.marchepublic.cd
Static HTML, French → English translation.
"""
import requests
import urllib3
urllib3.disable_warnings()
from bs4 import BeautifulSoup
from crawler.keywords import score
from crawler.translate import translate_to_en

BASE = 'https://www.marchepublic.cd'
PORTAL = 'marchepublic.cd'

SEARCH_PATHS = [
    '/avis-dappels-doffres/',
    '/appels-doffres/',
    '/marches-publics/',
    '/actualites/avis-dappel-doffres/',
    '/avis/',
    '/',
]

ELECTION_KW_FR = [
    'élection', 'electoral', 'vote', 'scrutin', 'bulletin', 'biométrique',
    'enrôlement', 'machine à voter', 'CENI', 'commission électorale',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
    'Accept-Language': 'fr,en;q=0.8',
}


def _is_election_related(text):
    t = text.lower()
    return any(k.lower() in t for k in ELECTION_KW_FR + [
        'election', 'ballot', 'vote', 'voter', 'biometric', 'ceni', 'scrutin',
    ])


def _scrape_path(session, path):
    rows = []
    try:
        r = session.get(f'{BASE}{path}', headers=HEADERS, timeout=20, verify=False)
        if r.status_code != 200 or len(r.text) < 500:
            return rows
        soup = BeautifulSoup(r.text, 'lxml')

        # Table rows
        for table in soup.find_all('table'):
            for tr in table.find_all('tr')[1:]:
                tds = tr.find_all('td')
                if not tds:
                    continue
                a = tr.find('a', href=True)
                title = a.get_text(strip=True) if a else tds[0].get_text(strip=True)
                href = a['href'] if a else ''
                url = (href if href.startswith('http')
                       else f'{BASE}{href}' if href.startswith('/')
                       else f'{BASE}/{href}') if href else f'{BASE}{path}'
                td_texts = [td.get_text(strip=True) for td in tds]
                rows.append({'title': title, 'url': url,
                             'snippet': ' | '.join(td_texts[:4]),
                             'pub': td_texts[1] if len(td_texts) > 1 else '',
                             'deadline': td_texts[2] if len(td_texts) > 2 else ''})

        # Article/div-based listings
        if not rows:
            for article in soup.find_all(['article', 'div'], class_=lambda c: c and any(
                    x in c for x in ['post', 'entry', 'notice', 'tender', 'avis', 'marche'])):
                a = article.find('a', href=True)
                if not a:
                    continue
                title = a.get_text(strip=True)
                href = a['href']
                url = href if href.startswith('http') else f'{BASE}{href}'
                parent_text = article.get_text(' ', strip=True)[:300]
                rows.append({'title': title, 'url': url, 'snippet': parent_text,
                             'pub': '', 'deadline': ''})

    except Exception as e:
        print(f'  [armp_drc] error ({path}): {e}')
    return rows


def parse(country='Democratic Republic of Congo', iso3='COD'):
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
            combined = f"{title} {snippet}"
            s = score(title, snippet)
            if s <= 0 and not _is_election_related(combined):
                continue  # skip non-election tenders
            if s <= 0:
                s = 15

            title_en = translate_to_en(title, sl='fr')
            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'title_en': title_en, 'url': url,
                'published_date': row['pub'], 'deadline_date': row['deadline'],
                'status': 'Open',
                'buyer': 'CENI / ARMP Congo',
                'amount': None, 'currency': 'CDF',
                'snippet': snippet[:300], 'score': s,
            })

        if results:
            break  # found working path

    print(f'  [armp_drc] {len(results)} notices found')
    return results
