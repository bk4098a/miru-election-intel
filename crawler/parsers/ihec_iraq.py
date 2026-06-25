"""Iraq — IHEC (Independent High Electoral Commission) procurement portal.

Site: https://ihec.iq/
Tenders page: https://ihec.iq/tenders-and-contracts/ (Arabic/English WordPress site)

Assessment: IHEC publishes only occasional PDF summaries of concluded contracts,
not a structured live tender listing.  The parser therefore:
  1. Tries multiple candidate URLs (English + Arabic paths).
  2. Scans each page for any links whose anchor text or href matches election
     keywords — these could be tender notice posts, PDF attachments, or
     category archive pages that appear in future updates.
  3. Scores every candidate against the keyword engine; items with score <= 0
     are dropped.
  4. Returns [] gracefully if the site is unreachable or empty — it is
     expected that this parser will return 0 notices most of the time until
     IHEC expands its online procurement publication.
"""

import re
import requests
from bs4 import BeautifulSoup
from crawler.keywords import score, is_election_related

import urllib3
urllib3.disable_warnings()

BASE = 'https://ihec.iq'
PORTAL = 'ihec.iq'
BUYER = 'Independent High Electoral Commission (IHEC)'

# Candidate URLs, tried in order — first non-empty HTML wins for the main scan.
# The Arabic slug is the canonical tenders page; English mirrors are also tried.
CANDIDATE_URLS = [
    f'{BASE}/tenders-and-contracts/',          # confirmed live (Arabic content, July 2022)
    f'{BASE}/en/tenders-and-contracts/',
    f'{BASE}/en/tenders/',
    f'{BASE}/en/procurement/',
    f'{BASE}/',
    f'{BASE}/en/',
    # WordPress JSON API — may expose posts tagged as tenders
    f'{BASE}/wp-json/wp/v2/posts?per_page=50&search=tender',
    f'{BASE}/wp-json/wp/v2/posts?per_page=50&search=%D8%AA%D9%86%D8%AF%D8%B1',  # Arabic "tender"
    f'{BASE}/wp-json/wp/v2/posts?per_page=50&search=%D8%A7%D9%86%D8%AA%D8%AE%D8%A7%D8%A8',  # انتخاب
]

# Local election keywords for Iraq context (Arabic + English)
_IRAQ_KW = re.compile(
    r'انتخابات|تصويت|مناقصة|عقود|تعاقد|procurement|tender|contract|'
    r'election|voting|ballot|electoral|biometric|IHEC|ihec|'
    r'EVM|DRE|VVPAT|scanner|tabulation',
    re.I,
)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              'application/json,*/*;q=0.8',
    'Accept-Language': 'ar,en;q=0.9',
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fetch(session: requests.Session, url: str, as_json: bool = False):
    """Return response text / parsed JSON, or None on error."""
    try:
        r = session.get(url, headers=HEADERS, timeout=30, verify=False)
        r.raise_for_status()
        if as_json:
            return r.json()
        return r.text
    except Exception as e:
        print(f'  [ihec_iraq] fetch error ({url}): {e}')
        return None


def _extract_date(text: str) -> str:
    """Pull the first YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY date from text."""
    m = re.search(
        r'\d{4}-\d{2}-\d{2}'        # ISO
        r'|\d{1,2}/\d{1,2}/\d{4}'  # DMY or MDY with slashes
        r'|\d{1,2}-\d{1,2}-\d{4}', # DMY with dashes
        text,
    )
    return m.group(0) if m else ''


def _html_rows(html: str, page_url: str) -> list:
    """Parse an HTML page and return candidate tender rows."""
    soup = BeautifulSoup(html, 'lxml')
    rows = []

    # --- 1. Structured tables (best case) ---
    for table in soup.find_all('table'):
        for tr in table.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if len(tds) < 2:
                continue
            link = tr.find('a', href=True)
            title = (link.get_text(strip=True) if link
                     else tds[0].get_text(strip=True))
            href = link['href'] if link else ''
            url = _resolve(href, page_url)
            td_texts = [td.get_text(strip=True) for td in tds]
            snippet = ' | '.join(td_texts[:5])
            rows.append({
                'title': title, 'url': url, 'snippet': snippet,
                'published_date': _extract_date(td_texts[1]) if len(td_texts) > 1 else '',
                'deadline_date': _extract_date(td_texts[2]) if len(td_texts) > 2 else '',
            })

    # --- 2. List items / article cards ---
    for item in soup.select('li, article, .tender-item, .post, .entry'):
        link = item.find('a', href=True)
        if not link:
            continue
        title = link.get_text(strip=True)
        if not title:
            continue
        href = link['href']
        url = _resolve(href, page_url)
        # Skip nav / menu links — typically very short or contain base URL only
        if url in (BASE, BASE + '/', page_url):
            continue
        snippet = item.get_text(' ', strip=True)[:300]
        rows.append({
            'title': title, 'url': url, 'snippet': snippet,
            'published_date': _extract_date(snippet),
            'deadline_date': '',
        })

    # --- 3. Any PDF links whose text or href hints at tenders / contracts ---
    for a in soup.find_all('a', href=True):
        href = a['href']
        if not (href.endswith('.pdf') or '/pdf/' in href.lower()):
            continue
        title = a.get_text(strip=True) or href.split('/')[-1]
        url = _resolve(href, page_url)
        snippet = title
        rows.append({
            'title': title, 'url': url, 'snippet': snippet,
            'published_date': '',
            'deadline_date': '',
        })

    return rows


def _wp_json_rows(posts: list) -> list:
    """Convert WordPress REST API post objects to candidate rows."""
    rows = []
    for post in posts:
        if not isinstance(post, dict):
            continue
        title = (post.get('title', {}) or {}).get('rendered', '').strip()
        if not title:
            continue
        url = post.get('link', '') or BASE
        excerpt_html = (post.get('excerpt', {}) or {}).get('rendered', '')
        try:
            snippet = BeautifulSoup(excerpt_html, 'lxml').get_text(strip=True)
        except Exception:
            snippet = re.sub(r'<[^>]+>', '', excerpt_html).strip()
        date = (post.get('date', '') or '')[:10]
        rows.append({
            'title': title, 'url': url, 'snippet': snippet,
            'published_date': date, 'deadline_date': '',
        })
    return rows


def _resolve(href: str, page_url: str) -> str:
    """Make a relative href absolute."""
    if not href:
        return page_url
    if href.startswith('http'):
        return href
    if href.startswith('/'):
        return BASE + href
    # relative to page directory
    base_dir = page_url.rsplit('/', 1)[0]
    return base_dir + '/' + href


def _is_relevant(title: str, snippet: str) -> bool:
    """Return True if the item passes the Iraq-specific keyword check OR the
    generic election keyword engine."""
    combined = f'{title} {snippet}'
    return bool(_IRAQ_KW.search(combined)) or is_election_related(title, snippet)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def parse(country: str = 'Iraq', iso3: str = 'IRQ') -> list:
    """Fetch IHEC tender/contract notices and return scored result dicts.

    Returns an empty list if the site is unreachable or contains no
    structured procurement data — this is expected given IHEC's current
    minimal online publication.
    """
    session = requests.Session()
    all_rows = []
    fetched_urls: set = set()

    for url in CANDIDATE_URLS:
        if url in fetched_urls:
            continue
        fetched_urls.add(url)

        is_wp_api = '/wp-json/' in url
        if is_wp_api:
            data = _fetch(session, url, as_json=True)
            if not data or not isinstance(data, list):
                continue
            rows = _wp_json_rows(data)
        else:
            html = _fetch(session, url)
            if not html:
                continue
            rows = _html_rows(html, url)

        # Keep only election-relevant candidates
        for row in rows:
            if _is_relevant(row['title'], row['snippet']):
                all_rows.append(row)

        # If we already found notices from a working HTML page, no need to
        # continue scanning every URL — but do still try WP JSON endpoints so
        # we don't miss API-only content.
        if all_rows and not is_wp_api:
            # Only skip remaining HTML URLs; WP JSON will still be attempted
            # on next iterations because the check above only breaks HTML ones.
            pass  # intentionally continue loop — WP endpoints may add more

    # De-duplicate by URL
    seen: set = set()
    results = []
    for row in all_rows:
        title = row['title']
        url = row['url']
        if not title or url in seen:
            continue
        seen.add(url)

        s = score(title, row['snippet'])
        # For Iraq/IHEC context, give a minimum score to items that matched
        # our local keyword filter even if the generic scorer gave 0, so they
        # are not silently dropped when the generic keywords list doesn't cover
        # Arabic terms that are present only in snippet.
        if s <= 0 and _IRAQ_KW.search(f"{title} {row['snippet']}"):
            s = 15  # treat as weak-keyword match

        if s <= 0:
            continue

        results.append({
            'country': country,
            'iso3': iso3,
            'portal_name': PORTAL,
            'title': title,
            'url': url,
            'published_date': row.get('published_date', ''),
            'deadline_date': row.get('deadline_date', ''),
            'status': 'Published',
            'buyer': BUYER,
            'amount': None,
            'currency': 'IQD',
            'snippet': row.get('snippet', '')[:300],
            'score': s,
        })

    print(f'  [ihec_iraq] {len(results)} notices found')
    return results
