"""Kenya — IEBC (Independent Electoral and Boundaries Commission)

Source: https://www.iebc.or.ke/work/?tenders
Structure: static HTML, one page, each tender is a div.row with:
  col-lg-8  → h4 (title + tender no in <small>), deadline text, status span
  col-lg-4  → uploaded-on date text, <a href=PDF> Download button
"""
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString
from crawler.keywords import score

import urllib3
urllib3.disable_warnings()

URL    = 'https://www.iebc.or.ke/work/?tenders'
PORTAL = 'iebc.or.ke'
BUYER  = 'Independent Electoral and Boundaries Commission (IEBC)'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,*/*;q=0.8',
}

_ORD_RE  = re.compile(r'(\d+)(?:st|nd|rd|th)', re.I)
_PHP_RE  = re.compile(r'echo\s+\$\w+;\s*\?>\s*', re.I)
_DATE_FMTS = ('%b %d, %Y', '%d %b, %Y', '%d %b %Y', '%B %d, %Y', '%d %B %Y')


def _to_iso(raw: str) -> str:
    """Parse 'Jun 19th, 2026' or 'Fri 12th Jun, 2026' → 'YYYY-MM-DD'."""
    if not raw:
        return ''
    s = _ORD_RE.sub(r'\1', raw.strip())
    s = re.sub(r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+', '', s, flags=re.I).strip()
    for fmt in _DATE_FMTS:
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return ''


def _parse_row(row) -> dict | None:
    """Extract tender data from one div.row block. Returns None if invalid."""
    left  = row.find('div', class_='col-lg-8')
    right = row.find('div', class_=re.compile(r'col-lg-4'))
    if not left or not right:
        return None

    # ── Title + Tender No ────────────────────────────────────────────────────
    h4 = left.find('h4')
    if not h4:
        return None

    small = h4.find('small')
    tender_no = small.get_text(strip=True).replace('Tender no:', '').strip() if small else ''

    # Direct text nodes inside h4 (skip <small> child)
    title_raw = ' '.join(
        str(c).strip()
        for c in h4.children
        if isinstance(c, NavigableString) and str(c).strip()
    )
    # Strip PHP artifact "echo $status; ?>"
    title = _PHP_RE.sub('', title_raw).strip()
    if not title:
        return None

    # ── Deadline ─────────────────────────────────────────────────────────────
    left_text = left.get_text(' ', strip=True)
    deadline_raw = ''
    m = re.search(r'Deadline:\s*(.+?)(?:\[|$)', left_text, re.I)
    if m:
        deadline_raw = m.group(1).strip()

    # ── Status ───────────────────────────────────────────────────────────────
    status_span = left.find('span')
    status_text = status_span.get_text(strip=True) if status_span else ''
    status = 'Closed' if 'closed' in status_text.lower() else 'Open'

    # ── Uploaded date ────────────────────────────────────────────────────────
    right_text = right.get_text(' ', strip=True)
    pub_raw = ''
    m2 = re.search(r'Uploaded on:\s*(.+?)(?:\n|$|Download)', right_text, re.I)
    if m2:
        pub_raw = m2.group(1).strip()

    # ── PDF download link ────────────────────────────────────────────────────
    pdf_link = right.find('a', href=re.compile(r'/uploads/tenders/', re.I))
    url = pdf_link['href'] if pdf_link else ''
    if not url:
        return None

    # ── Snippet ──────────────────────────────────────────────────────────────
    snippet_parts = [p for p in [tender_no, deadline_raw, status_text.strip('[] ')] if p]
    snippet = ' | '.join(snippet_parts)

    return {
        'title':          title,
        'url':            url,
        'published_date': _to_iso(pub_raw),
        'deadline_date':  _to_iso(deadline_raw),
        'status':         status,
        'snippet':        snippet,
        'tender_no':      tender_no,
    }


def parse(country: str = 'Kenya', iso3: str = 'KEN') -> list[dict]:
    session = requests.Session()
    try:
        r = session.get(URL, headers=HEADERS, timeout=40, verify=False)
        r.raise_for_status()
    except Exception as e:
        print(f'  [iebc_kenya] fetch error: {e}')
        return []

    soup = BeautifulSoup(r.text, 'lxml')

    # All tenders are in div.row blocks that contain a PDF download link
    rows = soup.find_all('div', class_='row')
    results = []
    seen: set[str] = set()

    for row in rows:
        data = _parse_row(row)
        if not data:
            continue
        url = data['url']
        if url in seen:
            continue
        seen.add(url)

        # All IEBC tenders are election-commission procurement → min score 15
        s = max(score(data['title'], data['snippet']), 15)

        results.append({
            'country':        country,
            'iso3':           iso3,
            'portal_name':    PORTAL,
            'title':          data['title'],
            'url':            url,
            'published_date': data['published_date'],
            'deadline_date':  data['deadline_date'],
            'status':         data['status'],
            'buyer':          BUYER,
            'amount':         None,
            'currency':       'KES',
            'snippet':        data['snippet'][:300],
            'score':          s,
        })

    print(f'  [iebc_kenya] {len(results)} notices found')
    return results
