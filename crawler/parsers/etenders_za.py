"""South Africa — eTenders Portal (National Treasury)

Site: https://www.etenders.gov.za
Government: Yes — National Treasury, Republic of South Africa

Architecture:
  - Main page: GET /Home/opportunities?id=1  (DataTables-powered SPA)
  - Data API: GET /Home/PaginatedTenderOpportunities
              params: draw, start, length, status
              status: 1=open, 2=awarded, 3=closed, 4=cancelled
  - Returns all records in one call with length=2000 (1873+ records)
  - Server-side search[value] param does NOT filter — DataTables does it client-side
  - Document download /home/Download/?blobName={guid} requires authentication

Strategy:
  1. Fetch ALL open tenders (status=1) and recent closed (status=3, last 500)
  2. Client-side filter: IEC (Electoral Commission) dept OR election keywords
  3. URL = portal page; tender_No in snippet so user can search on-site
"""

import re
import requests
import urllib3
from crawler.keywords import score

urllib3.disable_warnings()

BASE   = 'https://www.etenders.gov.za'
EP     = '/Home/PaginatedTenderOpportunities'
PORTAL = 'etenders.gov.za'
BUYER_DEFAULT = 'South Africa National Treasury'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': f'{BASE}/Home/opportunities?id=1',
}

# IEC = Independent Electoral Commission of South Africa
_IEC_DEPTS = {'electoral commission (iec)', 'electoral commission', 'iec'}

# "election" regex — \belect(?!r) matches election/electoral/elected but NOT electricity/electrical
_ELECTION_RE = re.compile(
    r'\belect(?!r)\w*|ballot|\bbiometric|\bvoter\b|\bvoting\b|polling\s+station'
    r'|voter\s+registration|election\s+management|demarcation|tabulation',
    re.I,
)


def _is_election(item: dict) -> bool:
    dept = (item.get('department') or item.get('organ_of_State') or '').lower()
    if any(d in dept for d in _IEC_DEPTS):
        return True
    # Search description only — category field ("Services: Electrical") causes false positives
    desc = (item.get('description') or '')
    return bool(_ELECTION_RE.search(desc))


def _fetch_status(session: requests.Session, status: int, max_length: int) -> list:
    """Fetch up to max_length tenders for the given status code."""
    try:
        r = session.get(
            BASE + EP,
            params={'draw': 1, 'start': 0, 'length': max_length, 'status': status},
            headers=HEADERS,
            timeout=60,
            verify=False,
        )
        if r.status_code in (500, 503):
            # Portal returns 500 for some status codes (e.g. closed tenders)
            return []
        r.raise_for_status()
        return r.json().get('data', [])
    except Exception as e:
        print(f'  [etenders_za] fetch error (status={status}): {e}')
        return []


def parse(country: str = 'South Africa', iso3: str = 'ZAF') -> list[dict]:
    session = requests.Session()
    # Hit the portal page once to get session cookies
    session.get(f'{BASE}/Home/opportunities?id=1', timeout=30, verify=False)

    seen:    set[str] = set()
    results: list[dict] = []

    # Fetch open (status=1) and recent closed (status=3)
    batches = [
        (1, 2000, 'Open'),
        (3, 500,  'Closed'),
    ]

    for status_code, max_len, status_label in batches:
        items = _fetch_status(session, status_code, max_len)
        for item in items:
            if not _is_election(item):
                continue

            desc    = (item.get('description') or '').strip()
            if not desc:
                continue

            tender_no = (item.get('tender_No') or '').strip()
            dept      = (item.get('department') or item.get('organ_of_State') or BUYER_DEFAULT).strip()
            category  = (item.get('category') or '').strip()
            province  = (item.get('province') or '').strip()

            # Unique key: use tender_No + description for dedup
            dedup_key = f'{tender_no}|{desc[:80]}'
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            # URL: portal page (document download requires auth)
            url = f'{BASE}/Home/opportunities?id=1'

            pub      = (item.get('date_Published') or '')[:10]
            deadline = (item.get('closing_Date')   or '')[:10]

            snippet_parts = [p for p in [tender_no, dept, category, province] if p]
            snippet = ' | '.join(snippet_parts)

            s = score(desc, snippet)
            # IEC tenders are all election-infrastructure → min score 15
            if any(d in dept.lower() for d in _IEC_DEPTS):
                s = max(s, 15)

            results.append({
                'country':        country,
                'iso3':           iso3,
                'portal_name':    PORTAL,
                'title':          desc,
                'url':            url,
                'published_date': pub,
                'deadline_date':  deadline,
                'status':         status_label,
                'buyer':          dept,
                'amount':         None,
                'currency':       'ZAR',
                'snippet':        snippet[:300],
                'score':          s,
            })

    print(f'  [etenders_za] {len(results)} notices found')
    return results
