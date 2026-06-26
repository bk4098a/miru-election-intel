"""Kyrgyzstan — zakupki.gov.kg (JSF portal + OCDS fallback)"""
import requests
from bs4 import BeautifulSoup
from crawler.keywords import score

BASE = 'https://zakupki.gov.kg'
SEARCH_PATH = '/epps/quickSearchAction.do'
OCDS_API = 'https://ocds.zakupki.gov.kg/api/tendering-processes'
PORTAL = 'zakupki.gov.kg'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
}

KEYWORDS_KG = ['выборы', 'избирательн', 'биометр', 'election', 'шайлоо']


def _try_ocds(session):
    """Try OCDS API first — cleaner JSON response."""
    results = []
    for kw in KEYWORDS_KG:
        try:
            r = session.get(OCDS_API, params={'q': kw, 'limit': 50}, timeout=20)
            if r.status_code != 200:
                continue
            data = r.json()
            items = data if isinstance(data, list) else data.get('data', [])
            for item in items:
                tender = item.get('tender', item)
                title = tender.get('title', '') or item.get('title', '')
                url = item.get('url') or f"{BASE}/epps/contract.do?id={item.get('id','')}"
                if not title:
                    continue
                results.append({
                    'title': title, 'url': url,
                    'published_date': tender.get('tenderPeriod', {}).get('startDate', '')[:10],
                    'deadline_date': tender.get('tenderPeriod', {}).get('endDate', '')[:10],
                    'status': tender.get('status', ''),
                    'buyer': item.get('buyer', {}).get('name', '') if isinstance(item.get('buyer'), dict) else '',
                    'amount': None, 'currency': 'KGS',
                    'snippet': title,
                    'score': score(title),
                })
        except Exception as e:
            print(f'  [zakupki_kg] OCDS error ({kw}): {e}')
    return results


def _try_html(session):
    """Fallback: JSF search page with ViewState extraction."""
    results = []
    try:
        # Step 1: GET to obtain ViewState
        r = session.get(f'{BASE}{SEARCH_PATH}', headers=HEADERS, timeout=30, verify=False)
        soup = BeautifulSoup(r.text, 'lxml')
        vs_input = soup.find('input', {'name': 'javax.faces.ViewState'})
        viewstate = vs_input['value'] if vs_input else ''

        for kw in KEYWORDS_KG[:2]:
            # Step 2: POST search
            data = {
                'javax.faces.ViewState': viewstate,
                'searchString': kw,
                'searchSelect': '6',
                'quickSearchForm:searchButton': 'Search',
            }
            pr = session.post(f'{BASE}{SEARCH_PATH}', data=data,
                              headers={**HEADERS, 'Content-Type': 'application/x-www-form-urlencoded'},
                              timeout=30, verify=False)
            psoup = BeautifulSoup(pr.text, 'lxml')

            for table in psoup.find_all('table'):
                for tr in table.find_all('tr')[1:]:
                    tds = tr.find_all('td')
                    if len(tds) < 2:
                        continue
                    link = tr.find('a', href=True)
                    title = link.get_text(strip=True) if link else tds[0].get_text(strip=True)
                    href = (link['href'] if link else '')
                    url = (BASE + '/' + href.lstrip('/')) if href and not href.startswith('http') else href
                    if not title:
                        continue
                    td_texts = [td.get_text(strip=True) for td in tds]
                    results.append({
                        'title': title, 'url': url or f'{BASE}/epps/',
                        'published_date': td_texts[1] if len(td_texts) > 1 else '',
                        'deadline_date': td_texts[2] if len(td_texts) > 2 else '',
                        'status': td_texts[-1] if td_texts else '',
                        'buyer': 'Central Commission for Elections (CEC KG)',
                        'amount': None, 'currency': 'KGS',
                        'snippet': ' | '.join(td_texts[:4]),
                        'score': score(title),
                    })
    except Exception as e:
        print(f'  [zakupki_kg] HTML fallback error: {e}')
    return results


def parse(country='Kyrgyzstan', iso3='KGZ'):
    import urllib3
    urllib3.disable_warnings()
    session = requests.Session()

    results = _try_ocds(session)
    if not results:
        results = _try_html(session)

    seen = set()
    deduped = []
    for r in results:
        if r['url'] not in seen:
            seen.add(r['url'])
            r.update({'country': country, 'iso3': iso3, 'portal_name': PORTAL})
            deduped.append(r)

    print(f'  [zakupki_kg] {len(deduped)} notices found')
    return deduped
