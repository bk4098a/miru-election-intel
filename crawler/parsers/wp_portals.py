"""WordPress REST API / Playwright portals — Bhutan ECB, Albania KQZ

ECB Bhutan: WordPress REST API (requests, may timeout)
KQZ Albania: Moved to Next.js in 2026 — wp-json gone → Playwright scrape
"""
import re
import requests
from bs4 import BeautifulSoup
from crawler.keywords import score, is_election_related

import urllib3
urllib3.disable_warnings()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/json,*/*;q=0.8',
}

# ── Bhutan ECB ────────────────────────────────────────────────────────────────

ECB_PORTALS = [
    {'api': 'https://www.ecb.bt/wp-json/wp/v2/posts', 'params': {'per_page': 50, 'search': 'tender'}},
    {'api': 'https://www.ecb.bt/wp-json/wp/v2/posts', 'params': {'per_page': 50, 'search': 'procurement'}},
    {'api': 'https://www.ecb.bt/wp-json/wp/v2/posts', 'params': {'per_page': 50, 'search': 'election'}},
]


def _strip_html(html):
    try:
        return BeautifulSoup(html, 'lxml').get_text(strip=True)
    except Exception:
        return re.sub(r'<[^>]+>', '', html).strip()


def parse_ecb_bhutan(country='Bhutan', iso3='BTN'):
    results = []
    seen = set()
    for cfg in ECB_PORTALS:
        try:
            r = requests.get(cfg['api'], params=cfg['params'], headers=HEADERS, timeout=45, verify=False)
            r.raise_for_status()
            posts = r.json()
        except Exception as e:
            print(f'  [ecb_bhutan] error: {e}')
            continue

        for post in posts:
            title = (post.get('title') or {}).get('rendered', '').strip()
            url = post.get('link', '')
            if not title or url in seen:
                continue
            snippet = _strip_html((post.get('excerpt') or {}).get('rendered', ''))
            if not is_election_related(title, snippet):
                continue
            seen.add(url)
            date = (post.get('date') or '')[:10]
            results.append({
                'country': country, 'iso3': iso3, 'portal_name': 'ecb.bt',
                'title': title, 'url': url,
                'published_date': date, 'deadline_date': '',
                'status': post.get('status', ''),
                'buyer': 'Election Commission of Bhutan',
                'amount': None, 'currency': 'BTN',
                'snippet': snippet[:300],
                'score': score(title, snippet),
            })

    print(f'  [ecb_bhutan] {len(results)} notices found')
    return results


# ── Albania KQZ — Playwright (Next.js, no wp-json) ───────────────────────────

KQZ_BASE = 'https://kqz.gov.al'
# Candidate paths for procurement notices on the rebuilt Next.js site
KQZ_PATHS = [
    '/prokurimi',       # Albanian: procurement
    '/tenderime',       # tenders
    '/blerje-publike',  # public procurement
    '/konkurse',        # contests/tenders
    '/njoftime',        # announcements
    '/',                # homepage (may list recent tenders)
]
KQZ_KEYWORDS = ['election', 'zgjedhje', 'votim', 'ballot', 'biometric', 'tender',
                 'procurement', 'software', 'sistem', 'teknologji']


def _kqz_is_relevant(text):
    t = text.lower()
    return any(k in t for k in KQZ_KEYWORDS)


def parse_kqz_albania(country='Albania', iso3='ALB'):
    from playwright.sync_api import sync_playwright

    results = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
        ctx = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            ignore_https_errors=True,
        )
        page = ctx.new_page()

        for path in KQZ_PATHS:
            url = KQZ_BASE + path
            try:
                page.goto(url, timeout=20000, wait_until='domcontentloaded')
                page.wait_for_load_state('networkidle', timeout=8000)
            except Exception as e:
                print(f'  [kqz_albania] goto error ({path}): {e}')
                continue

            html = page.content()
            soup = BeautifulSoup(html, 'lxml')

            # Collect all links with potentially relevant anchor text
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                href = a['href']
                if not title or len(title) < 8:
                    continue
                if not _kqz_is_relevant(title):
                    continue
                full_url = (KQZ_BASE + href) if href.startswith('/') else href
                if not full_url.startswith('http') or full_url in seen:
                    continue
                seen.add(full_url)
                parent_text = (a.parent or a).get_text(' ', strip=True)[:300]
                s = score(title, parent_text)
                if s <= 0:
                    s = 15  # minimum for Albanian electoral context
                results.append({
                    'country': country, 'iso3': iso3, 'portal_name': 'kqz.gov.al',
                    'title': title, 'url': full_url,
                    'published_date': '', 'deadline_date': '',
                    'status': 'Open',
                    'buyer': 'Komisioni Qendror i Zgjedhjeve (KQZ)',
                    'amount': None, 'currency': 'ALL',
                    'snippet': parent_text[:300],
                    'score': s,
                })

            # If we found notices on this path, don't keep trying every path
            if results:
                break

        browser.close()

    print(f'  [kqz_albania] {len(results)} notices found')
    return results
