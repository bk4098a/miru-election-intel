"""India — ECI tenders + CPPP (Central Public Procurement Portal)
Primary: https://eci.gov.in/tenders.html  (Election Commission of India — English)
Secondary: https://eprocure.gov.in  (CPPP, search by ECI keyword)
No translation needed (English portal).
"""
import requests
import urllib3
urllib3.disable_warnings()
from bs4 import BeautifulSoup
from crawler.keywords import score

ECI_URLS = [
    'https://eci.gov.in/tenders.html',
    'https://eci.gov.in/tenders-and-procurements/',
    'https://eci.gov.in/procurement/',
]

CPPP_SEARCH = 'https://eprocure.gov.in/eprocure/app'
PORTAL_ECI = 'eci.gov.in'
PORTAL_CPPP = 'eprocure.gov.in'

ELECTION_KEYWORDS = [
    'EVM', 'VVPAT', 'voting machine', 'ballot', 'biometric', 'voter',
    'election', 'electoral', 'COMELEC',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}


def _fetch_eci(session):
    """Scrape ECI tender page (English, static HTML)."""
    results = []
    for url in ECI_URLS:
        try:
            r = session.get(url, headers=HEADERS, timeout=20, verify=False)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, 'lxml')

            # Look for tender list items — ECI usually uses ul/li or table
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                href = a['href']
                if not title or len(title) < 8:
                    continue
                # ECI page may list PDFs and notices
                full_url = (href if href.startswith('http')
                            else f'https://eci.gov.in{href}' if href.startswith('/')
                            else f'https://eci.gov.in/{href}')
                parent = (a.parent or a).get_text(' ', strip=True)[:300]
                s = score(title, parent)
                if s <= 0:
                    s = 15  # ECI context: always election-related
                results.append({
                    'title': title, 'url': full_url,
                    'snippet': parent, 'buyer': 'Election Commission of India',
                    'pub': '', 'deadline': '', 'status': 'Open', 'score': s,
                })

            if results:
                break
        except Exception as e:
            print(f'  [cppp_india] ECI error ({url}): {e}')

    return results


def _fetch_cppp(session):
    """CPPP: search for election-related notices (keyword-filtered)."""
    results = []
    cppp_search_urls = [
        'https://eprocure.gov.in/eprocure/app?component=%24DirectLink&page=FrontEndSearchTenders&service=direct',
        'https://eprocure.gov.in/eprocure/app?component=%24DirectLink&page=FrontEndAdvSearch&service=direct',
    ]
    # CPPP is a JSF application — static GET likely to fail, but try keyword search
    for kw in ['election commission', 'EVM', 'VVPAT', 'ballot paper', 'voter registration']:
        try:
            r = session.get(
                'https://eprocure.gov.in/eprocure/app',
                params={
                    'component': '%24DirectLink',
                    'page': 'FrontEndSearchTenders',
                    'service': 'direct',
                    'searchStr': kw,
                },
                headers=HEADERS, timeout=20, verify=False,
            )
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, 'lxml')
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                href = a['href']
                if not title or len(title) < 10:
                    continue
                if 'Tender' not in title and not any(k.lower() in title.lower() for k in ELECTION_KEYWORDS):
                    continue
                full_url = href if href.startswith('http') else f'https://eprocure.gov.in{href}'
                s = score(title)
                results.append({
                    'title': title, 'url': full_url,
                    'snippet': title, 'buyer': 'Ministry/Dept (India)',
                    'pub': '', 'deadline': '', 'status': 'Open', 'score': s,
                })
        except Exception:
            continue
    return results


def parse(country='India', iso3='IND'):
    import urllib3
    urllib3.disable_warnings()
    session = requests.Session()

    seen = set()
    results = []

    for row in _fetch_eci(session) + _fetch_cppp(session):
        title = row['title']
        url = row['url']
        if not title or url in seen:
            continue
        seen.add(url)
        # India portals are in English — no translation needed
        results.append({
            'country': country, 'iso3': iso3, 'portal_name': PORTAL_ECI,
            'title': title, 'title_en': title, 'url': url,
            'published_date': row['pub'], 'deadline_date': row['deadline'],
            'status': row['status'], 'buyer': row['buyer'],
            'amount': None, 'currency': 'INR',
            'snippet': row['snippet'][:300], 'score': row['score'],
        })

    print(f'  [cppp_india] {len(results)} notices found')
    return results
