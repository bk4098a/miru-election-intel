"""Kenya — tenders.go.ke (Vue 3 SPA + Laravel REST API)

Architecture notes:
  - The site renders only <div id="app"></div> without JS — HTML scraping is useless.
  - All data comes from a public Laravel REST API (no auth required).
  - Working public endpoints: /api/active-tenders, /api/closed-tenders,
    /api/agpo-tenders, /api/terminated-tenders, /api/restricted-tenders
  - The /api/tenders and /api/tenders/published routes return 401 (auth required).
  - Pagination params: perpage=<n>&page=<n>  (standard Laravel pagination)
  - Response: {current_page, last_page, total, data[], links[]}
  - search= param does NOT filter server-side on active-tenders — filtering is
    done client-side by matching titles against keywords.
  - Rate limit: 429 after rapid requests — enforce a 2 s delay between pages.
  - Record schema: id, ocid, title, tender_ref, published_at, close_at,
    pe.name (procuring entity), procurement_method.title,
    procurement_category.title, terminated, addendum_added
"""
import time
import requests
from crawler.keywords import score, is_election_related

import urllib3
urllib3.disable_warnings()

BASE = 'https://tenders.go.ke'
PORTAL = 'tenders.go.ke'

# Public endpoints (no auth required), in priority order.
# active-tenders is checked first; closed-tenders covers historical IEBC procurements.
API_ENDPOINTS = [
    f'{BASE}/api/active-tenders',
    f'{BASE}/api/agpo-tenders',
    f'{BASE}/api/closed-tenders',
]

# Items per page — 50 keeps page count reasonable (~24 pages for 1,167 active).
PERPAGE = 50
# Maximum pages to fetch per endpoint (3 pages × 50 items = up to 150 items checked).
MAX_PAGES = 3
# Seconds between requests — portal enforces 429 above ~1 req/s.
REQUEST_DELAY = 2.0

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': BASE,
    'X-Requested-With': 'XMLHttpRequest',
}

# Election-related keywords used for client-side title matching.
# IEBC = Independent Electoral and Boundaries Commission (Kenya's election body).
# KIEMS = Kenya Integrated Election Management System.
# BVR = Biometric Voter Registration kit.
KEYWORDS = [
    'election', 'iebc', 'biometric', 'voter', 'ballot', 'electoral',
    'voting machine', 'voting system', 'polling', 'registration kit',
    'bvr', 'kiems', 'kie', 'boundaries commission', 'referendum',
]


def _is_election_row(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in KEYWORDS)


def _fetch_page(session: requests.Session, endpoint: str, page: int):
    """Fetch one page from a Laravel-paginated API endpoint.
    Returns the parsed JSON dict or None on error.
    """
    params = {'perpage': PERPAGE, 'page': page}
    try:
        r = session.get(endpoint, params=params, headers=HEADERS,
                        timeout=30, verify=False)
        if r.status_code == 429:
            print(f'  [tenders_kenya] rate limited on {endpoint} page {page} — backing off 5 s')
            time.sleep(5.0)
            r = session.get(endpoint, params=params, headers=HEADERS,
                            timeout=30, verify=False)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f'  [tenders_kenya] fetch error ({endpoint} p{page}): {e}')
        return None


def _extract_records(data) -> list[dict]:
    """Pull the list of tender dicts out of whatever the API returned."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Standard Laravel pagination: data.data[]
        for key in ('data', 'tenders', 'results', 'items'):
            val = data.get(key)
            if isinstance(val, list):
                return val
            # Nested pagination object: data.data.data[]
            if isinstance(val, dict):
                inner = val.get('data')
                if isinstance(inner, list):
                    return inner
    return []


def _build_url(item: dict) -> str:
    """Construct a detail URL for a tender record."""
    # Try explicit url/link fields first.
    for field in ('url', 'link', 'detail_url'):
        v = item.get(field)
        if v and isinstance(v, str) and v.startswith('http'):
            return v
    # Derive from ocid or id — the SPA routes tenders as /tenders/<ocid> or /tenders/<id>
    ocid = item.get('ocid') or ''
    tender_id = item.get('id') or ''
    if ocid:
        return f'{BASE}/tenders/{ocid}'
    if tender_id:
        return f'{BASE}/tenders/{tender_id}'
    return BASE


def _extract_buyer(item: dict) -> str:
    """Extract procuring entity name from nested or flat fields."""
    # Nested: pe.name (the most common shape from the confirmed endpoint)
    pe = item.get('pe')
    if isinstance(pe, dict):
        for f in ('name', 'title', 'organisation_name'):
            v = pe.get(f)
            if v:
                return str(v).strip()
    # Flat alternatives
    for field in ('procuring_entity', 'entity', 'organisation', 'buyer', 'contracting_authority'):
        v = item.get(field)
        if v and isinstance(v, str):
            return v.strip()
        if isinstance(v, dict):
            for f in ('name', 'title'):
                name = v.get(f)
                if name:
                    return str(name).strip()
    return 'Government of Kenya'


def _extract_date(item: dict, *fields) -> str:
    """Return the first non-empty date string from the given field names."""
    for field in fields:
        v = item.get(field)
        if v and isinstance(v, str):
            # Trim to YYYY-MM-DD if it includes time component
            return v[:10]
    return ''


def _extract_amount(item: dict):
    """Return tender amount as float if available, else None."""
    for field in ('amount', 'estimated_value', 'contract_value', 'budget'):
        v = item.get(field)
        if v is not None:
            try:
                return float(str(v).replace(',', '').strip())
            except (ValueError, TypeError):
                pass
    return None


def _build_snippet(item: dict, buyer: str, pub: str, deadline: str) -> str:
    method = ''
    pm = item.get('procurement_method')
    if isinstance(pm, dict):
        method = pm.get('title') or pm.get('name') or ''
    elif isinstance(pm, str):
        method = pm

    category = ''
    pc = item.get('procurement_category')
    if isinstance(pc, dict):
        category = pc.get('title') or pc.get('name') or ''
    elif isinstance(pc, str):
        category = pc

    ref = item.get('tender_ref') or item.get('reference') or ''
    parts = [p for p in [buyer, ref, method, category, pub, deadline] if p]
    return ' | '.join(parts)


def parse(country: str = 'Kenya', iso3: str = 'KEN') -> list[dict]:
    session = requests.Session()
    seen: set[str] = set()
    results: list[dict] = []

    for endpoint in API_ENDPOINTS:
        endpoint_hits = 0
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(REQUEST_DELAY)

            data = _fetch_page(session, endpoint, page)
            if data is None:
                break

            records = _extract_records(data)
            if not records:
                break

            for item in records:
                if not isinstance(item, dict):
                    continue

                title = (
                    item.get('title') or
                    item.get('name') or
                    item.get('tender_name') or
                    item.get('subject') or
                    ''
                ).strip()

                if not title:
                    continue
                if not _is_election_row(title):
                    continue

                url = _build_url(item)
                if url in seen:
                    continue
                seen.add(url)

                buyer = _extract_buyer(item)
                pub = _extract_date(item, 'published_at', 'published_date', 'created_at', 'date')
                deadline = _extract_date(item, 'close_at', 'closing_date', 'deadline', 'end_date')
                amount = _extract_amount(item)
                snippet = _build_snippet(item, buyer, pub, deadline)

                s = score(title, snippet)
                # Apply extra score boost for Kenya-specific election keywords
                if 'iebc' in title.lower() or 'kiems' in title.lower():
                    s = max(s, 40)

                results.append({
                    'country': country,
                    'iso3': iso3,
                    'portal_name': PORTAL,
                    'title': title,
                    'url': url,
                    'published_date': pub,
                    'deadline_date': deadline,
                    'status': 'Closed' if 'closed' in endpoint else 'Open',
                    'buyer': buyer,
                    'amount': amount,
                    'currency': 'KES',
                    'snippet': snippet[:300],
                    'score': s,
                })
                endpoint_hits += 1

            # Detect last page: Laravel sets last_page in the root or nested object.
            last_page = None
            if isinstance(data, dict):
                last_page = data.get('last_page')
                if last_page is None:
                    nested = data.get('data')
                    if isinstance(nested, dict):
                        last_page = nested.get('last_page')
            if last_page is not None and page >= int(last_page):
                break

        if endpoint_hits:
            # If we found election tenders in active, skip closed to save quota.
            # Remove this break to always check closed-tenders for historical data.
            break

        time.sleep(REQUEST_DELAY)

    print(f'  [tenders_kenya] {len(results)} notices found')
    return results
