"""South Korea — 나라장터 G2B via data.go.kr Open API

Portal:   https://www.g2b.go.kr  (Next-Gen G2B, OIDC-only — no public HTML scraping)
Open API: https://apis.data.go.kr/1230000/BidPublicInfoService/getBidPblancListInfoServ

Auth requirement
----------------
The G2B portal itself requires OIDC login for every page; HTML scraping is not viable.
The public Open API hosted at data.go.kr works without login but requires a free
`serviceKey` obtained by:
  1. Visit https://www.data.go.kr
  2. Search: "나라장터 입찰공고정보서비스"
  3. Click "활용 신청" — approval in 1-2 business days (free)
  4. Set env var: G2B_SERVICE_KEY=<URL-encoded key>

Without the key this parser returns an empty list and prints a reminder.

API behaviour notes
-------------------
- Default response is XML; passing `type=json` returns JSON.
- `items` can be:
    - A list of dicts when multiple records match
    - A single dict when exactly one record matches
    - An empty string "" when zero records match  (not null / not [])
- Pagination: `pageNo` + `numOfRows`; stop when returned row count < numOfRows.
- Date range: `inqryBgnDt` / `inqryEndDt` in `YYYYMMDD0000` format.
  We query the last 365 days so the result set stays bounded.
- Duplicate notices can appear across keyword searches; deduplicate by `bidNtceNo`.
"""

import os
import re
import requests
from datetime import datetime, timedelta
from crawler.keywords import score, is_election_related

import urllib3
urllib3.disable_warnings()

# ── Constants ────────────────────────────────────────────────────────────────

API_BASE = (
    'https://apis.data.go.kr/1230000/BidPublicInfoService/getBidPblancListInfoServ'
)
PORTAL = 'g2b.go.kr'

# Search terms: Korean election/voting vocabulary + English terms that may appear
# in international-standard tenders issued by 중앙선거관리위원회 (NEC).
SEARCH_TERMS = [
    '선거',           # election (broad — highest recall)
    '투표',           # voting / vote
    '선거관리위원회', # National Election Commission
    '전자개표',       # electronic counting
    '선거장비',       # election equipment
    '투표기',         # voting machine
    'KIEMS',          # Korea Integrated Election Management System
    '투표단말',       # voting terminal
    'election',       # English (appears in some bilingual tenders)
    'voting machine', # English
]

ROWS_PER_PAGE = 100  # maximum allowed by the API
MAX_PAGES = 5        # cap per keyword to avoid runaway pagination

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _date_range():
    """Return (begin, end) in YYYYMMDD0000 format covering the last 365 days."""
    end = datetime.utcnow()
    begin = end - timedelta(days=365)
    fmt = '%Y%m%d0000'
    return begin.strftime(fmt), end.strftime(fmt)


def _parse_amount(val):
    """Convert a raw price string / number to float KRW, or None."""
    if val is None or val == '':
        return None
    try:
        return float(re.sub(r'[^\d.]', '', str(val)))
    except Exception:
        return None


def _coerce_date(raw):
    """Return first 10 chars of a date string (YYYY-MM-DD or YYYYMMDDHHMI)."""
    if not raw:
        return ''
    s = str(raw).strip()
    # YYYYMMDDHHMI → YYYY-MM-DD
    if re.match(r'^\d{12}$', s):
        return f'{s[:4]}-{s[4:6]}-{s[6:8]}'
    # Already ISO-ish
    return s[:10]


def _normalise_items(raw_items):
    """Normalise the 'item' field: always return a list of dicts."""
    if not raw_items:
        return []
    if isinstance(raw_items, list):
        return [i for i in raw_items if isinstance(i, dict)]
    if isinstance(raw_items, dict):
        return [raw_items]
    return []


def _detail_url(item):
    """Build the best available URL for a bid notice."""
    # The API sometimes provides a direct document URL
    doc_url = (item.get('ntceSpecDocUrl') or '').strip()
    if doc_url and doc_url.startswith('http'):
        return doc_url
    # Fall back to the G2B search page filtered to the specific notice number
    bid_no = item.get('bidNtceNo', '')
    if bid_no:
        return f'https://www.g2b.go.kr/ep/tbid/tbBidPbancListFwd.do?bidNtceNo={bid_no}'
    return 'https://www.g2b.go.kr'


# ── API layer ────────────────────────────────────────────────────────────────

def _fetch_page(session, service_key, keyword, page, begin_dt, end_dt):
    """Fetch one page of results for a keyword. Returns list of item dicts."""
    params = {
        'serviceKey':  service_key,
        'bidNtceNm':   keyword,
        'numOfRows':   ROWS_PER_PAGE,
        'pageNo':      page,
        'type':        'json',
        'inqryBgnDt':  begin_dt,
        'inqryEndDt':  end_dt,
    }
    try:
        r = session.get(
            API_BASE, params=params, headers=HEADERS,
            timeout=30, verify=False,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f'  [g2b_korea] API error (keyword={keyword!r}, page={page}): {e}')
        return [], 0

    body = data.get('response', {}).get('body', {})
    total = int(body.get('totalCount', 0) or 0)

    # 'items' is a dict {"item": ...} or empty string when no results
    raw = body.get('items', '')
    if not raw or raw == '':
        return [], total

    item_list = _normalise_items(raw.get('item') if isinstance(raw, dict) else raw)
    return item_list, total


def _fetch_keyword(session, service_key, keyword, begin_dt, end_dt):
    """Fetch all pages for a single keyword. Returns raw item dicts."""
    all_items = []
    for page in range(1, MAX_PAGES + 1):
        items, total = _fetch_page(session, service_key, keyword, page, begin_dt, end_dt)
        all_items.extend(items)
        # Stop if we've received all items or got an empty page
        if not items or len(all_items) >= total:
            break
    return all_items


# ── Main parse function ──────────────────────────────────────────────────────

def parse(country='South Korea', iso3='KOR'):
    """Fetch Korean G2B election-related bid notices via data.go.kr Open API.

    Returns a list of notice dicts conforming to the election_intel_tenders schema.
    Returns [] if G2B_SERVICE_KEY is not set.
    """
    service_key = os.environ.get('G2B_SERVICE_KEY', '').strip()
    if not service_key:
        print('  [g2b_korea] G2B_SERVICE_KEY not set - skipping (register at data.go.kr)')
        return []

    session = requests.Session()
    begin_dt, end_dt = _date_range()

    # Collect raw items across all keywords; deduplicate by bidNtceNo
    seen_ids = set()   # bidNtceNo dedup across keyword searches
    seen_urls = set()  # secondary URL dedup
    raw_pool = []

    for term in SEARCH_TERMS:
        items = _fetch_keyword(session, service_key, term, begin_dt, end_dt)
        for item in items:
            bid_no = item.get('bidNtceNo', '')
            # Prefer bidNtceNo dedup; fall back to URL dedup
            if bid_no:
                if bid_no in seen_ids:
                    continue
                seen_ids.add(bid_no)
            else:
                url = _detail_url(item)
                if url in seen_urls:
                    continue
                seen_urls.add(url)
            raw_pool.append(item)

    results = []
    for item in raw_pool:
        title = (item.get('bidNtceNm') or '').strip()
        if not title:
            continue

        buyer    = (item.get('ntceInsttNm') or '').strip()
        pub_date = _coerce_date(item.get('bidNtceDt'))
        deadline = _coerce_date(item.get('bidClseDt'))
        amount   = _parse_amount(item.get('presmptPrce'))
        method   = (item.get('bidMethdNm') or '').strip()
        contract = (item.get('cntrctCnclsMthdNm') or '').strip()
        detail   = _detail_url(item)

        snippet = ' | '.join(filter(None, [buyer, method, contract, pub_date]))

        # Apply election-relevance filter — skip notices that slipped through
        # keyword search but are not election-related (e.g. '선거' appearing in
        # an unrelated context).
        if not is_election_related(title, snippet):
            continue

        results.append({
            'country':        country,
            'iso3':           iso3,
            'portal_name':    PORTAL,
            'title':          title,
            'url':            detail,
            'published_date': pub_date,
            'deadline_date':  deadline,
            'status':         'Open',
            'buyer':          buyer,
            'amount':         amount,
            'currency':       'KRW',
            'snippet':        snippet[:300],
            'score':          score(title, snippet),
        })

    print(f'  [g2b_korea] {len(results)} notices found')
    return results
