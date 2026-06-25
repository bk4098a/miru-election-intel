"""Philippines — PhilGEPS (Philippine Government Electronic Procurement System)

Primary target: philgeps.gov.ph/Indexes/ (newer Laravel-style HTML tables, no login)
Fallback: notices.philgeps.gov.ph (ASP.NET WebForms, first page only — no ViewState)

COMELEC (Commission on Elections) is the key procuring entity for election technology.
Target keywords include ACM (Automated Counting Machine), VCM (Vote Counting Machine),
VVPAT, biometric voter registration kits, and related election technology.

No API key required. Uses requests + BeautifulSoup (lxml).
"""
import re
import time
import requests
from bs4 import BeautifulSoup
from crawler.keywords import score, is_election_related

import urllib3
urllib3.disable_warnings()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_INDEXES = 'https://philgeps.gov.ph'
BASE_NOTICES = 'https://notices.philgeps.gov.ph'
PORTAL = 'philgeps.gov.ph'

# Ordered by preference — getFormerOpportunities has the richest historical set
# which is where most completed COMELEC procurements will be found.
INDEXES_ENDPOINTS = [
    f'{BASE_INDEXES}/Indexes/getFormerOpportunities',
    f'{BASE_INDEXES}/Indexes/index',
    f'{BASE_INDEXES}/Indexes/getAwardNotices',
]

# notices.philgeps.gov.ph — classic ASP.NET. First page loads without ViewState.
NOTICES_ENDPOINTS = [
    f'{BASE_NOTICES}/GEPSNONPILOT/Tender/SplashOpenOpportunitiesUI.aspx?ClickFrom=OpenOpp&menuIndex=3',
    f'{BASE_NOTICES}/GEPSNONPILOT/Tender/SplashOpenOpportunitiesUI.aspx',
]

# Detail URL template — used when a reference number is available in the table
DETAIL_URL_TEMPLATE = f'{BASE_INDEXES}/Indexes/viewLiveTenderDetails/{{ref_no}}'

# Election-domain keywords for pre-filter (case-insensitive substring match).
# Broader than the central keywords.py regexes so we catch Filipino variations.
KEYWORDS = [
    'election', 'electoral', 'comelec',
    'voting machine', 'vote counting', 'automated counting',
    'ballot', 'precinct', 'canvass',
    'biometric voter', 'voter registration', 'fingerprint',
    'acm', 'vcm', 'vvpat',
    'halalan',       # Filipino: election
    'boto',          # Filipino: vote
    'bilang',        # Filipino: count/tally (as in "pagbibilang ng boto")
]

MAX_PAGES = 5
REQUEST_DELAY = 1.0  # seconds between requests

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,fil;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_election_row(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in KEYWORDS)


def _fetch(session: requests.Session, url: str, params: dict = None) -> str:
    """Fetch HTML, return empty string on any error."""
    try:
        r = session.get(
            url, headers=HEADERS, params=params,
            timeout=30, verify=False, allow_redirects=True,
        )
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f'  [philgeps] fetch error ({url}): {e}')
        return ''


def _extract_date(text: str) -> str:
    """Parse MM/DD/YYYY or YYYY-MM-DD from a cell string."""
    if not text:
        return ''
    m = re.search(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', text)
    return m.group(0) if m else ''


def _normalize_header(h: str) -> str:
    return re.sub(r'\s+', ' ', h).strip().lower()


def _col_index(headers: list, *candidates: str) -> int:
    """Return the first column index whose normalized header contains any candidate substring."""
    for i, h in enumerate(headers):
        hn = _normalize_header(h)
        for c in candidates:
            if c in hn:
                return i
    return -1


def _build_detail_url(row_soup, base_url: str) -> str:
    """
    Try to build a direct detail URL.
    1. Follow <a href> in the row (preferred).
    2. Look for a ref-no cell and use the /Indexes/viewLiveTenderDetails/{ref} template.
    3. Fall back to base_url.
    """
    link = row_soup.find('a', href=True)
    if link:
        href = link['href'].strip()
        if href.startswith('http'):
            return href
        if href.startswith('/'):
            return BASE_INDEXES + href
        if href:
            return base_url + '/' + href.lstrip('/')

    # Try to extract numeric ref from any td that looks like a reference number
    for td in row_soup.find_all('td'):
        txt = td.get_text(strip=True)
        if re.fullmatch(r'\d{7,}', txt):  # PhilGEPS ref nos are typically 7+ digits
            return DETAIL_URL_TEMPLATE.format(ref_no=txt)

    return base_url


def _parse_indexes_table(html: str, endpoint: str) -> list:
    """
    Parse the HTML table returned by the /Indexes/ endpoints.

    Expected column order (may vary):
      Bid Notice Ref No | Notice Title | Mode of Procurement | Classification
      | Agency Name | Publish Date | Closing Date | Status

    Returns a list of raw row dicts for further processing.
    """
    if not html:
        return []

    soup = BeautifulSoup(html, 'lxml')
    rows_out = []

    for table in soup.find_all('table'):
        # Require a header row to avoid picking up nav/footer tables
        header_cells = table.find_all('th')
        if not header_cells:
            # Some PhilGEPS tables use <td> for headers in the first row
            first_row_tds = table.find('tr')
            if not first_row_tds:
                continue
            candidate_hdrs = first_row_tds.find_all('td')
            if not candidate_hdrs or len(candidate_hdrs) < 4:
                continue
            headers = [c.get_text(strip=True) for c in candidate_hdrs]
            data_rows = table.find_all('tr')[1:]
        else:
            headers = [th.get_text(strip=True) for th in header_cells]
            data_rows = table.find_all('tr')[1:]

        if not headers or len(headers) < 3:
            continue

        # Map known column names
        idx_ref    = _col_index(headers, 'ref', 'reference', 'notice no', 'bid no')
        idx_title  = _col_index(headers, 'title', 'notice title', 'description')
        idx_mode   = _col_index(headers, 'mode', 'procurement mode')
        idx_agency = _col_index(headers, 'agency', 'entity', 'procuring')
        idx_pub    = _col_index(headers, 'publish', 'posted', 'open date', 'date published')
        idx_close  = _col_index(headers, 'clos', 'deadline', 'end date', 'submission')
        idx_status = _col_index(headers, 'status')

        for tr in data_rows:
            tds = tr.find_all('td')
            if len(tds) < 3:
                continue

            def _td(i):
                if i < 0 or i >= len(tds):
                    return ''
                return tds[i].get_text(separator=' ', strip=True)

            # Title: prefer mapped column; fall back to first <a> text; then td[1]
            if idx_title >= 0:
                title = _td(idx_title)
            else:
                link = tr.find('a')
                title = link.get_text(strip=True) if link else _td(1)

            if not title:
                continue

            detail_url = _build_detail_url(tr, endpoint)
            td_texts = [td.get_text(separator=' ', strip=True) for td in tds]

            rows_out.append({
                'title':     title,
                'url':       detail_url,
                'ref_no':    _td(idx_ref) if idx_ref >= 0 else '',
                'agency':    _td(idx_agency) if idx_agency >= 0 else (td_texts[4] if len(td_texts) > 4 else ''),
                'pub_date':  _extract_date(_td(idx_pub)) if idx_pub >= 0 else _extract_date(td_texts[5] if len(td_texts) > 5 else ''),
                'deadline':  _extract_date(_td(idx_close)) if idx_close >= 0 else _extract_date(td_texts[6] if len(td_texts) > 6 else ''),
                'status':    _td(idx_status) if idx_status >= 0 else (td_texts[-1] if td_texts else 'Active'),
                'mode':      _td(idx_mode) if idx_mode >= 0 else '',
                'all_tds':   td_texts,
            })

        if rows_out:
            break  # found the data table; skip remaining tables in this page

    return rows_out


def _parse_notices_table(html: str) -> list:
    """
    Parse the initial HTML load of notices.philgeps.gov.ph (ASP.NET WebForms).
    The first-page DataGrid renders without needing a PostBack — this gives us
    one page of live open tenders. Not paginated (ViewState required for that).
    """
    if not html:
        return []

    soup = BeautifulSoup(html, 'lxml')
    rows_out = []

    # The grid id is dgSearchCatResult but we probe all tables defensively
    for table in soup.find_all('table'):
        header_cells = table.find_all('th')
        if not header_cells:
            continue
        headers = [th.get_text(strip=True) for th in header_cells]
        if len(headers) < 3:
            continue

        idx_title  = _col_index(headers, 'title', 'description')
        idx_agency = _col_index(headers, 'agency', 'entity')
        idx_pub    = _col_index(headers, 'publish', 'posted', 'date')
        idx_close  = _col_index(headers, 'clos', 'deadline')
        idx_status = _col_index(headers, 'status')

        for tr in table.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if len(tds) < 2:
                continue

            def _td(i):
                if i < 0 or i >= len(tds):
                    return ''
                return tds[i].get_text(separator=' ', strip=True)

            if idx_title >= 0:
                title = _td(idx_title)
            else:
                link = tr.find('a')
                title = link.get_text(strip=True) if link else _td(0)

            if not title:
                continue

            link = tr.find('a', href=True)
            href = link['href'].strip() if link else ''
            if href.startswith('http'):
                detail_url = href
            elif href.startswith('/'):
                detail_url = BASE_NOTICES + href
            else:
                detail_url = BASE_NOTICES

            td_texts = [td.get_text(separator=' ', strip=True) for td in tds]
            rows_out.append({
                'title':    title,
                'url':      detail_url,
                'ref_no':   '',
                'agency':   _td(idx_agency) if idx_agency >= 0 else (td_texts[1] if len(td_texts) > 1 else ''),
                'pub_date': _extract_date(_td(idx_pub)) if idx_pub >= 0 else '',
                'deadline': _extract_date(_td(idx_close)) if idx_close >= 0 else '',
                'status':   _td(idx_status) if idx_status >= 0 else 'Open',
                'mode':     '',
                'all_tds':  td_texts,
            })

        if rows_out:
            break

    return rows_out


def _has_more_pages(html: str, current_page: int) -> bool:
    """
    Check whether a "View More" / next-page indicator exists in the HTML.
    PhilGEPS /Indexes/ pages may use: a "View More" anchor, a "next" pagination
    link, or a page count. Returns True if more pages are likely.
    """
    if not html:
        return False
    soup = BeautifulSoup(html, 'lxml')
    text_lower = soup.get_text(' ').lower()

    # Explicit next-page / view-more indicators
    for a in soup.find_all('a'):
        anchor_text = a.get_text(strip=True).lower()
        if any(t in anchor_text for t in ('view more', 'next', 'next page', '>>')):
            return True

    # Pagination numbered links beyond current page
    for a in soup.find_all('a', href=True):
        href = a['href']
        m = re.search(r'[?&]page=(\d+)', href, re.I)
        if m and int(m.group(1)) > current_page:
            return True

    # If fewer than 5 rows in table, almost certainly the last (or only) page
    # (detect this upstream in the caller instead)
    return False


# ---------------------------------------------------------------------------
# Main crawler
# ---------------------------------------------------------------------------

def _crawl_indexes(session: requests.Session) -> list:
    """Scrape /Indexes/ endpoints with pagination up to MAX_PAGES."""
    all_rows = []

    for endpoint in INDEXES_ENDPOINTS:
        print(f'  [philgeps] trying {endpoint}')
        endpoint_rows = []

        for page in range(1, MAX_PAGES + 1):
            # Attempt several pagination parameter names — the actual one is
            # unconfirmed from static analysis; try the most common patterns.
            params = None
            if page > 1:
                params = {'page': page}

            html = _fetch(session, endpoint, params)
            if not html:
                # Retry once with alternative param style
                if page > 1:
                    html = _fetch(session, endpoint, {'p': page})
                if not html:
                    break

            page_rows = _parse_indexes_table(html, endpoint)
            if not page_rows:
                break

            endpoint_rows.extend(page_rows)

            # Stop if this page had very few rows (likely the last page)
            if len(page_rows) < 5:
                break

            # Stop if no pagination indicator found
            if not _has_more_pages(html, page):
                break

            time.sleep(REQUEST_DELAY)

        all_rows.extend(endpoint_rows)
        print(f'  [philgeps] {endpoint.split("/")[-1]}: {len(endpoint_rows)} rows scraped')

        # If we got results from this endpoint, no need to try the next one
        # (they overlap in content). Continue to getAwardNotices regardless.
        if endpoint_rows and 'getAwardNotices' not in endpoint:
            continue

    return all_rows


def _crawl_notices(session: requests.Session) -> list:
    """Scrape the notices.philgeps.gov.ph subdomain (first page only, no ViewState)."""
    for endpoint in NOTICES_ENDPOINTS:
        print(f'  [philgeps] trying notices subdomain: {endpoint}')
        html = _fetch(session, endpoint)
        if not html:
            continue
        rows = _parse_notices_table(html)
        if rows:
            print(f'  [philgeps] notices subdomain: {len(rows)} rows scraped')
            return rows
    return []


def parse(country: str = 'Philippines', iso3: str = 'PHL') -> list:
    """
    Parse PhilGEPS for election-related procurement notices.

    Strategy:
    1. Scrape /Indexes/getFormerOpportunities + /Indexes/index + /Indexes/getAwardNotices
       (HTML tables, no login, paginated up to MAX_PAGES).
    2. Fallback to notices.philgeps.gov.ph first-page static HTML if /Indexes/ is down.
    3. Filter all rows using KEYWORDS (broader pre-filter) + keywords.py score().
    4. Deduplicate by URL.

    Returns a list of tender dicts matching the election_intel_tenders schema.
    """
    session = requests.Session()
    # Warm up with a root request to establish session cookies
    _fetch(session, BASE_INDEXES)

    raw_rows = _crawl_indexes(session)

    # If /Indexes/ returned nothing, fall back to notices subdomain
    if not raw_rows:
        print('  [philgeps] /Indexes/ empty — trying notices subdomain fallback')
        raw_rows = _crawl_notices(session)

    # Filter to election-related rows
    election_rows = [r for r in raw_rows if _is_election_row(r['title'])]

    # Deduplicate by URL
    seen_urls = set()
    results = []
    for row in election_rows:
        title = row['title'].strip()
        url = row['url'].strip()
        if not title or url in seen_urls:
            continue
        seen_urls.add(url)

        all_tds = row.get('all_tds', [])
        snippet_parts = [p for p in [row.get('ref_no'), row.get('agency'), row.get('mode'),
                                      row.get('pub_date'), row.get('deadline')] if p]
        snippet = ' | '.join(snippet_parts) if snippet_parts else ' | '.join(all_tds[:5])

        results.append({
            'country':        country,
            'iso3':           iso3,
            'portal_name':    PORTAL,
            'title':          title,
            'url':            url,
            'published_date': row.get('pub_date', ''),
            'deadline_date':  row.get('deadline', ''),
            'status':         row.get('status', 'Active'),
            'buyer':          row.get('agency', 'Commission on Elections (COMELEC)'),
            'amount':         None,
            'currency':       'PHP',
            'snippet':        snippet[:300],
            'score':          score(title, snippet),
        })

    # Remove any results that scored 0 or below (noise filter from keywords.py)
    results = [r for r in results if r['score'] > 0]

    print(f'  [philgeps] {len(results)} notices found')
    return results
