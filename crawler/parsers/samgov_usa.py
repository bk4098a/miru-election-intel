"""USA — SAM.gov Opportunities API v2
API key required: register free at https://api.sam.gov
Set env var: SAMGOV_API_KEY=<your-key>

Without a key this parser returns [] with a reminder.
"""
import os
import requests
from datetime import datetime, timedelta, timezone
from crawler.keywords import score

import urllib3
urllib3.disable_warnings()

API_URL = 'https://api.sam.gov/opportunities/v2/search'
PORTAL = 'sam.gov'

SEARCH_QUERY = (
    'election OR electoral OR ballot OR "voting machine" OR "voting equipment" '
    'OR "voter registration" OR "election management" OR EVM OR DRE OR VVPAT'
)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}


def _days_back():
    since = (datetime.now(timezone.utc) - timedelta(days=365)).strftime('%m/%d/%Y')
    return since


def parse(country='United States', iso3='USA'):
    api_key = os.environ.get('SAMGOV_API_KEY', '').strip()
    if not api_key:
        print('  [samgov_usa] SAMGOV_API_KEY not set - skipping (register at api.sam.gov)')
        return []

    params = {
        'limit': 100,
        'api_key': api_key,
        'postedFrom': _days_back(),
        'q': SEARCH_QUERY,
    }

    try:
        r = requests.get(API_URL, params=params, headers=HEADERS, timeout=30, verify=False)
        if r.status_code in (401, 403):
            print(f'  [samgov_usa] API auth error ({r.status_code}) - check SAMGOV_API_KEY')
            return []
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f'  [samgov_usa] API error: {e}')
        return []

    results = []
    for n in data.get('opportunitiesData', []):
        title = (n.get('title') or '').strip()
        if not title:
            continue
        desc = (n.get('description') or '')[:300]
        dept = (n.get('organizationName') or n.get('department') or '').strip()
        nid = n.get('noticeId') or n.get('solicitationNumber') or ''
        url = n.get('uiLink') or f'https://sam.gov/opp/{nid}/view'
        pub = (n.get('postedDate') or '')[:10]
        deadline = (n.get('responseDeadLine') or '')[:10]
        snippet = f"{title} | {dept} | {desc[:200]}"

        results.append({
            'country': country, 'iso3': iso3, 'portal_name': PORTAL,
            'title': title, 'url': url,
            'published_date': pub,
            'deadline_date': deadline,
            'status': n.get('type', 'Open'),
            'buyer': dept,
            'amount': None, 'currency': 'USD',
            'snippet': snippet[:300],
            'score': score(title, snippet),
        })

    print(f'  [samgov_usa] {len(results)} notices found')
    return results
