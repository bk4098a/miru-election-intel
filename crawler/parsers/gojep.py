"""Jamaica — GOJEP (Electoral Office of Jamaica, org id=1936)"""
import requests
from bs4 import BeautifulSoup
from crawler.keywords import score, is_election_related

ORG_URL = 'https://www.gojep.gov.jm/epps/prepareViewCAOrganisation.do?id=1936'
DETAIL_BASE = 'https://www.gojep.gov.jm/epps/'
PORTAL = 'gojep.gov.jm'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}


def parse(country='Jamaica', iso3='JAM'):
    try:
        r = requests.get(ORG_URL, headers=HEADERS, timeout=30, verify=False)
        r.raise_for_status()
    except Exception as e:
        print(f'  [gojep] fetch error: {e}')
        return []

    import urllib3
    urllib3.disable_warnings()

    soup = BeautifulSoup(r.text, 'lxml')
    results = []
    seen = set()

    for table in soup.find_all('table'):
        for tr in table.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if len(tds) < 2:
                continue
            link = tr.find('a', href=True)
            title = link.get_text(strip=True) if link else tds[0].get_text(strip=True)
            href = link['href'] if link else ''
            if not href:
                continue
            url = (DETAIL_BASE + href.lstrip('/')) if not href.startswith('http') else href
            if url in seen:
                continue
            seen.add(url)

            td_texts = [td.get_text(strip=True) for td in tds]
            snippet = ' | '.join(td_texts[:4])

            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'url': url,
                'published_date': td_texts[1] if len(td_texts) > 1 else '',
                'deadline_date': td_texts[2] if len(td_texts) > 2 else '',
                'status': td_texts[-1] if td_texts else '',
                'buyer': 'Electoral Office of Jamaica',
                'amount': None, 'currency': 'JMD',
                'snippet': snippet[:300],
                'score': score(title, snippet),
            })

    print(f'  [gojep] {len(results)} notices found')
    return results
