"""Philippines — PhilGEPS Open Notices Portal (Playwright, ASP.NET WebForms)

Portal: https://notices.philgeps.gov.ph/GEPSNONPILOT/Tender/SplashOpenOpportunitiesUI.aspx
English interface. Searches for election/COMELEC keywords via form submission.
All search results are saved regardless of score.
"""
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from crawler.keywords import score

BASE_URL = (
    'https://notices.philgeps.gov.ph/GEPSNONPILOT/Tender/SplashOpenOpportunitiesUI.aspx'
    '?ClickFrom=OpenOpp&menuIndex=3'
)
DETAIL_BASE = 'https://notices.philgeps.gov.ph'
DETAIL_PATH = '/GEPSNONPILOT/Tender/'
PORTAL = 'philgeps.gov.ph'

# Broad election procurement keywords for COMELEC and related agencies
SEARCH_KEYWORDS = [
    'COMELEC',    # Commission on Elections — main election body
    'election',   # general election procurement
    'ballot',     # ballot boxes / ballot paper
    'voting',     # voting machines / VCM
    'biometric',  # biometric voter registration equipment
    'precinct',   # precinct count optical scan (PCOS/VCM)
]

MAX_PAGES_PER_KEYWORD = 10  # ~200-250 tenders max per keyword


def _parse_table(html: str) -> list[dict]:
    """Extract tender rows from the search results table."""
    soup = BeautifulSoup(html, 'lxml')
    rows = []
    seen_titles = set()

    # The results table: No | Publish | Closing | Title (with link)
    for table in soup.find_all('table'):
        trs = table.find_all('tr')
        data_rows = [tr for tr in trs if len(tr.find_all('td')) >= 3]
        if len(data_rows) < 2:
            continue

        for tr in data_rows:
            tds = tr.find_all('td')
            link = tr.find('a', href=True)
            if not link:
                title = tds[-1].get_text(strip=True)
                href = ''
            else:
                title = link.get_text(strip=True)
                href = link.get('href', '')

            if not title or len(title) < 5:
                continue
            if title in seen_titles:
                continue
            seen_titles.add(title)

            if href.startswith('http'):
                url = href
            elif href.startswith('/'):
                url = DETAIL_BASE + href
            elif href and not href.startswith('javascript'):
                # relative to /GEPSNONPILOT/Tender/
                url = DETAIL_BASE + DETAIL_PATH + href
            else:
                m = re.search(r"refID=(\d+)", href or '')
                url = (f'{DETAIL_BASE}{DETAIL_PATH}SplashBidNoticeAbstractUI.aspx?menuIndex=3&refID={m.group(1)}' if m
                       else BASE_URL + '#' + re.sub(r'\W+', '-', title[:40]))

            td_texts = [td.get_text(strip=True) for td in tds]
            pub = _to_iso(td_texts[1] if len(td_texts) > 1 else '')
            close_raw = td_texts[2] if len(td_texts) > 2 else ''
            deadline = _to_iso(close_raw.split()[0] if close_raw.split() else '')

            # Skip header/nav rows — real tender detail URLs always contain refID=
            if 'refID=' not in url:
                continue

            rows.append({
                'title': title,
                'url': url,
                'published_date': pub,
                'deadline_date': deadline,
                'snippet': ' | '.join(td_texts[:4])[:300],
            })

    return rows


def _to_iso(raw: str) -> str:
    """Convert DD/MM/YYYY → YYYY-MM-DD, pass through ISO, return '' on fail."""
    if not raw:
        return ''
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', raw.strip())
    if m:
        return f'{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}'
    if re.match(r'\d{4}-\d{2}-\d{2}', raw):
        return raw[:10]
    return ''


def _has_next(page) -> bool:
    """Return True if a clickable Next page link exists."""
    next_el = page.query_selector('#pgCtrlDetailedSearch_nextLB')
    if not next_el:
        return False
    return next_el.get_attribute('disabled') is None


def _search_keyword(keyword: str) -> list[dict]:
    """Open PhilGEPS, search for keyword, paginate and return all rows."""
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
        ctx = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            ignore_https_errors=True,
        )
        page = ctx.new_page()
        try:
            page.goto(BASE_URL, timeout=30000, wait_until='domcontentloaded')
            page.wait_for_timeout(1500)
            page.click('a[id="lbtnSearch"]')
            page.wait_for_timeout(1500)
            page.fill('input[name="txtKeyword"]', keyword)
            page.click('input[id="btnSearch"]')
            page.wait_for_timeout(3000)

            for page_num in range(1, MAX_PAGES_PER_KEYWORD + 1):
                html = page.content()
                page_rows = _parse_table(html)
                rows.extend(page_rows)
                if page_num >= MAX_PAGES_PER_KEYWORD or not _has_next(page):
                    break
                page.click('#pgCtrlDetailedSearch_nextLB')
                page.wait_for_timeout(2500)

        except Exception as e:
            print(f'  [philgeps] Playwright error ({keyword!r}): {e}')
        finally:
            browser.close()

    return rows


def parse(country: str = 'Philippines', iso3: str = 'PHL') -> list[dict]:
    # url → result dict, so later rows with better dates can replace earlier ones
    seen_urls: dict[str, dict] = {}

    for keyword in SEARCH_KEYWORDS:
        kw_rows = _search_keyword(keyword)
        for row in kw_rows:
            title = row['title']
            url = row['url']
            existing = seen_urls.get(url)
            # Prefer rows that have publication dates over those that don't
            if existing and existing.get('published_date'):
                continue

            snippet = row.get('snippet', title)
            seen_urls[url] = {
                'country': country,
                'iso3': iso3,
                'portal_name': PORTAL,
                'title': title,
                'url': url,
                'published_date': row.get('published_date', ''),
                'deadline_date': row.get('deadline_date', ''),
                'status': 'Open',
                'buyer': 'PhilGEPS',
                'amount': None,
                'currency': 'PHP',
                'snippet': snippet,
                'score': score(title, snippet),
            }

    results = list(seen_urls.values())
    print(f'  [philgeps] {len(results)} notices found')
    return results
