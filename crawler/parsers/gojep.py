"""Jamaica — GOJEP (Playwright, JSF app requires JS rendering)
Portal: https://www.gojep.gov.jm — ePPS by European Dynamics
Org page: /epps/prepareViewCAOrganisation.do?id=1936 (Electoral Office of Jamaica)
"""
import time
from crawler.keywords import score

import urllib3
urllib3.disable_warnings()

ORG_URL = 'https://www.gojep.gov.jm/epps/prepareViewCAOrganisation.do?id=1936'
SEARCH_URL = 'https://www.gojep.gov.jm/epps/prepareSearchContractNotice.do'
PORTAL = 'gojep.gov.jm'
KEYWORDS = ['election', 'electoral', 'voting', 'ballot', 'biometric', 'tabulation']


def _is_relevant(text):
    t = text.lower()
    return any(k in t for k in KEYWORDS)


def _pw_fetch(url, wait_selector=None, timeout=30000):
    """Fetch a page with Playwright and return (html, page_title)."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
        ctx = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            ignore_https_errors=True,
        )
        page = ctx.new_page()
        try:
            page.goto(url, timeout=timeout, wait_until='domcontentloaded')
            if wait_selector:
                try:
                    page.wait_for_selector(wait_selector, timeout=10000)
                except Exception:
                    pass
            else:
                page.wait_for_load_state('networkidle', timeout=10000)
            html = page.content()
        except Exception as e:
            print(f'  [gojep] Playwright error ({url}): {e}')
            html = ''
        finally:
            browser.close()
    return html


def _parse_notices(html, base_url='https://www.gojep.gov.jm/epps/'):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    rows = []
    seen = set()

    # ePPS notice table — class varies but rows contain td links
    for table in soup.find_all('table'):
        for tr in table.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if len(tds) < 2:
                continue
            link = tr.find('a', href=True)
            title = link.get_text(strip=True) if link else tds[0].get_text(strip=True)
            href = link['href'] if link else ''
            if not href or not title:
                continue
            url = (base_url + href.lstrip('/')) if not href.startswith('http') else href
            if url in seen:
                continue
            seen.add(url)
            td_texts = [td.get_text(strip=True) for td in tds]
            rows.append({
                'title': title, 'url': url,
                'published_date': td_texts[1] if len(td_texts) > 1 else '',
                'deadline_date': td_texts[2] if len(td_texts) > 2 else '',
                'status': td_texts[-1] if td_texts else '',
                'snippet': ' | '.join(td_texts[:4]),
            })

    # Also check card-style layouts (some ePPS versions use div grids)
    if not rows:
        for card in soup.select('.notice-item, .contract-card, [class*="notice"], [class*="contract"]'):
            link = card.find('a', href=True)
            if not link:
                continue
            title = link.get_text(strip=True)
            href = link['href']
            url = (base_url + href.lstrip('/')) if not href.startswith('http') else href
            if not title or url in seen:
                continue
            seen.add(url)
            rows.append({
                'title': title, 'url': url,
                'published_date': '', 'deadline_date': '',
                'status': '', 'snippet': card.get_text(' ', strip=True)[:200],
            })

    return rows


def parse(country='Jamaica', iso3='JAM'):
    # Try org page first (Electoral Office, id=1936)
    html = _pw_fetch(ORG_URL, wait_selector='table')
    rows = _parse_notices(html) if html else []

    # If org page empty, try full search
    if not rows:
        html2 = _pw_fetch(SEARCH_URL, wait_selector='table')
        rows = _parse_notices(html2) if html2 else []

    results = []
    seen_titles = set()
    for row in rows:
        title = row['title']
        if not title or title in seen_titles:
            continue
        if not _is_relevant(title):
            continue
        seen_titles.add(title)
        snippet = row.get('snippet', title)
        results.append({
            'country': country, 'iso3': iso3, 'portal_name': PORTAL,
            'title': title, 'url': row['url'],
            'published_date': row.get('published_date', ''),
            'deadline_date': row.get('deadline_date', ''),
            'status': row.get('status', 'Open'),
            'buyer': 'Electoral Office of Jamaica',
            'amount': None, 'currency': 'JMD',
            'snippet': snippet[:300],
            'score': score(title, snippet),
        })

    print(f'  [gojep] {len(results)} notices found')
    return results
