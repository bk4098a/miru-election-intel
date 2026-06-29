"""Spain/Barcelona — Portal de Contractació Electrònica de Barcelona

Site: https://licitacions.bcn.cat/
Language: Catalan (ca)
Architecture:
  - List page: GET /licitacion/licitaciones?page=N&term=&filtropred=en-plazo
  - Panel: div.panel.panel-default
    - Reference: p.media-heading.h4
    - Title:     p.ajBcn-item  (inside panel-heading)
    - Detail link: div.media-right a.btn.layout-link  (href = /licitacion/licitaciones/detalle?id=XXXXX)
    - Budget:    div.ajBcn-item-separate[strong='Pressupost sense IVA'] span+span
    - Date range: div.ajBcn-item-separate[strong~='Vigència'] span (e.g. '26/de juny/2026 - 17/de jul./2026 13:00')
    - Buyer:     div.ajBcn-item-separate a.ajBcn-link span
    - Status:    div.ajBcn-item-separate[strong='Estat'] span
  - Pagination max: auto-detected from .pagination links
  - No API — pure HTML scraping
"""

import re
import requests
import urllib3
from bs4 import BeautifulSoup

from crawler.keywords import score
from crawler.translate import translate_to_en

urllib3.disable_warnings()

BASE   = 'https://licitacions.bcn.cat'
PORTAL = 'licitacions.bcn.cat'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Catalan month → zero-padded number
_CA_MONTHS = {
    'gen': '01', 'febr': '02', 'mar': '03', 'abr': '04',
    'maig': '05', 'juny': '06', 'jun': '06',
    'jul': '07', 'ago': '08', 'set': '09',
    'oct': '10', 'nov': '11', 'des': '12',
}

_DATE_RE = re.compile(r'(\d{1,2})/de\s+(\w+)\.?/(\d{4})', re.I)


def _parse_date(text: str) -> str:
    """Parse 'D/de Month/YYYY' → 'YYYY-MM-DD', return '' on failure."""
    m = _DATE_RE.search(text)
    if not m:
        return ''
    day, mon_raw, year = m.group(1), m.group(2).lower()[:4], m.group(3)
    mon = _CA_MONTHS.get(mon_raw, '')
    if not mon:
        return ''
    return f'{year}-{mon}-{day.zfill(2)}'


def _parse_amount(panel) -> tuple[float | None, str]:
    """Return (amount_float, currency) from panel body."""
    for div in panel.select('div.ajBcn-item-separate'):
        strong = div.select_one('strong')
        if not strong:
            continue
        if 'Pressupost' in strong.text or 'Import' in strong.text:
            spans = div.select('span')
            if len(spans) >= 2:
                raw = spans[0].text.strip().replace('.', '').replace(',', '.')
                try:
                    return float(raw), spans[1].text.strip()
                except ValueError:
                    pass
    return None, 'EUR'


def _parse_dates(panel) -> tuple[str, str]:
    """Return (published_date, deadline_date) from 'Vigència del tràmit' span."""
    for div in panel.select('div.ajBcn-item-separate'):
        strong = div.select_one('strong')
        if strong and 'Vig' in strong.text:
            span = div.select_one('span')
            if span:
                parts = span.text.strip().split(' - ')
                pub      = _parse_date(parts[0]) if parts else ''
                deadline = _parse_date(parts[1]) if len(parts) > 1 else ''
                return pub, deadline
    return '', ''


def _parse_buyer(panel) -> str:
    for div in panel.select('div.ajBcn-item-separate'):
        link = div.select_one('a.ajBcn-link span')
        if link:
            return link.text.strip()
    return ''


def _parse_status(panel) -> str:
    for div in panel.select('div.ajBcn-item-separate'):
        strong = div.select_one('strong')
        if strong and 'Estat' in strong.text:
            spans = [s.text.strip() for s in div.select('span') if s.text.strip()]
            return spans[0] if spans else 'Published'
    return 'Published'


def _fetch_page(session: requests.Session, page: int) -> BeautifulSoup | None:
    url = f'{BASE}/licitacion/licitaciones?page={page}&term=&filtropred=en-plazo'
    try:
        r = session.get(url, headers=HEADERS, timeout=30, verify=False)
        r.raise_for_status()
        return BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f'  [bcn_barcelona] page {page} error: {e}')
        return None


def _max_page(soup: BeautifulSoup) -> int:
    nums = []
    for a in soup.select('.pagination a'):
        try:
            nums.append(int(a.text.strip()))
        except ValueError:
            pass
    return max(nums) if nums else 1


def parse(country: str = 'Spain', iso3: str = 'ESP') -> list[dict]:
    session = requests.Session()
    soup1 = _fetch_page(session, 1)
    if not soup1:
        return []

    max_pg = _max_page(soup1)
    soups = [soup1]
    for pg in range(2, max_pg + 1):
        s = _fetch_page(session, pg)
        if s:
            soups.append(s)

    results: list[dict] = []

    for soup in soups:
        for panel in soup.select('div.panel.panel-default'):
            heading = panel.select_one('div.panel-heading.media')
            if not heading:
                continue

            ref_el   = heading.select_one('p.media-heading')
            title_el = heading.select_one('p.ajBcn-item')
            link_el  = heading.select_one('div.media-right a.btn')

            if not title_el:
                continue

            ref   = (ref_el.text.strip()   if ref_el   else '')
            title = title_el.text.strip()
            href  = link_el.get('href', '') if link_el  else ''
            url   = (BASE + href) if href.startswith('/') else href

            amount, currency = _parse_amount(panel)
            pub, deadline    = _parse_dates(panel)
            buyer            = _parse_buyer(panel)
            status           = _parse_status(panel)

            snippet = f'{ref} | {buyer}' if buyer else ref

            title_en = translate_to_en(title, sl='ca') if title else ''

            s = score(title_en or title, snippet)

            results.append({
                'country':        country,
                'iso3':           iso3,
                'portal_name':    PORTAL,
                'title':          title,
                'title_en':       title_en,
                'url':            url,
                'published_date': pub,
                'deadline_date':  deadline,
                'status':         status,
                'buyer':          buyer,
                'amount':         amount,
                'currency':       currency,
                'snippet':        snippet[:300],
                'score':          s,
            })

    print(f'  [bcn_barcelona] {len(results)} notices found ({max_pg} pages)')
    return results
