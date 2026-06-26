"""Argentina — COMPR.AR (comprar.gob.ar) + CNE (Cámara Nacional Electoral)
Portal: https://comprar.gob.ar  (ASP.NET WebForms — HTML scraping)
CNE: https://www.cnecarga.cne.gov.ar (Electoral procurement notices)
No REST API available; uses HTML table scraping + ES→EN translation.
"""
import requests
import urllib3
urllib3.disable_warnings()
from bs4 import BeautifulSoup
from crawler.keywords import score
from crawler.translate import translate_to_en

BASE = 'https://comprar.gob.ar'
PORTAL = 'comprar.gob.ar'

# ASP.NET "show all processes" URL (encoded qs = all)
COMPRAS_URL = f'{BASE}/Compras.aspx?qs=W1HXHGHtH10='

# CNE is the Argentine electoral court — direct static page
CNE_URLS = [
    'https://www.cne.gov.ar/licitaciones/',
    'https://www.cne.gov.ar/licitaciones-y-contrataciones/',
    'https://www.electoral.gov.ar/licitaciones/',
]

ELECTION_KW_ES = [
    'elección', 'electoral', 'voto', 'urna', 'padrón', 'sufragio',
    'cámara electoral', 'CNE', 'DINE', 'biometrico',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
}


def _is_election_related(text):
    t = text.lower()
    return any(k.lower() in t for k in ELECTION_KW_ES + [
        'election', 'ballot', 'biometric', 'vote', 'voter',
    ])


def _scrape_compras(session):
    """Scrape comprar.gob.ar all-processes table, filter by election keywords."""
    rows = []
    try:
        r = session.get(COMPRAS_URL, headers=HEADERS, timeout=25, verify=False)
        if r.status_code != 200:
            return rows
        soup = BeautifulSoup(r.text, 'lxml')
        for table in soup.find_all('table'):
            for tr in table.find_all('tr')[1:]:
                tds = tr.find_all('td')
                if not tds:
                    continue
                a = tr.find('a', href=True)
                title = a.get_text(strip=True) if a else tds[0].get_text(strip=True)
                href = a['href'] if a else ''
                url = (href if href.startswith('http') else f'{BASE}{href}') if href else BASE
                td_texts = [td.get_text(strip=True) for td in tds]
                combined = f"{title} {' '.join(td_texts)}"
                if not _is_election_related(combined):
                    continue
                rows.append({
                    'title': title, 'url': url,
                    'snippet': ' | '.join(td_texts[:4]),
                    'pub': td_texts[1] if len(td_texts) > 1 else '',
                    'deadline': td_texts[3] if len(td_texts) > 3 else '',
                    'buyer': td_texts[0] if td_texts else 'ONC Argentina',
                })
    except Exception as e:
        print(f'  [compr_ar] scrape error: {e}')
    return rows


def _scrape_cne(session):
    """Scrape CNE (electoral court) tender pages."""
    rows = []
    for url in CNE_URLS:
        try:
            r = session.get(url, headers=HEADERS, timeout=20, verify=False)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, 'lxml')
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                href = a['href']
                if not title or len(title) < 8:
                    continue
                full_url = href if href.startswith('http') else f'https://www.cne.gov.ar{href}'
                parent = (a.parent or a).get_text(' ', strip=True)[:300]
                s = score(title, parent)
                if s <= 0:
                    s = 40  # CNE = election authority, everything is relevant
                rows.append({'title': title, 'url': full_url, 'snippet': parent,
                             'pub': '', 'deadline': '', 'buyer': 'Cámara Nacional Electoral'})
            if rows:
                break
        except Exception as e:
            print(f'  [compr_ar] CNE error ({url}): {e}')
    return rows


def parse(country='Argentina', iso3='ARG'):
    session = requests.Session()
    seen = set()
    results = []

    for row in _scrape_compras(session) + _scrape_cne(session):
        title = row['title']
        url = row['url']
        if not title or url in seen:
            continue
        seen.add(url)
        snippet = row['snippet']
        s = score(title, snippet) or 15
        title_en = translate_to_en(title, sl='es')
        results.append({
            'country': country, 'iso3': iso3, 'portal_name': PORTAL,
            'title': title, 'title_en': title_en, 'url': url,
            'published_date': row['pub'], 'deadline_date': row['deadline'],
            'status': 'Open',
            'buyer': row.get('buyer', 'ONC Argentina'),
            'amount': None, 'currency': 'ARS',
            'snippet': snippet[:300], 'score': s,
        })

    print(f'  [compr_ar] {len(results)} notices found')
    return results
