"""South Korea — 나라장터 G2B via data.go.kr Open API
Requires env var: G2B_SERVICE_KEY (free registration at https://www.data.go.kr)
Search: "나라장터 입찰공고정보서비스" → API key → paste in .env
"""
import os
import re
import requests
import xml.etree.ElementTree as ET
from crawler.keywords import score

import urllib3
urllib3.disable_warnings()

API_BASE = 'https://apis.data.go.kr/1230000/BidPublicInfoService/getBidPblancListInfoServ'
PORTAL = 'g2b.go.kr'
SEARCH_TERMS = ['선거', '투표기', '선거관리위원회', '전자개표', '선거장비', 'KIEMS', '투표단말']

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}


def _fetch_api(session, service_key, keyword, page=1):
    params = {
        'serviceKey': service_key,
        'bidNtceNm': keyword,
        'numOfRows': 100,
        'pageNo': page,
        'type': 'json',
    }
    try:
        r = session.get(API_BASE, params=params, headers=HEADERS, timeout=30, verify=False)
        r.raise_for_status()
        data = r.json()
        items = data.get('response', {}).get('body', {}).get('items', {})
        if isinstance(items, dict):
            item = items.get('item', [])
            return item if isinstance(item, list) else [item]
        return []
    except Exception as e:
        print(f'  [g2b_korea] API error ({keyword}): {e}')
        return []


def _parse_amount(val):
    if not val:
        return None
    try:
        return float(re.sub(r'[^\d.]', '', str(val)))
    except Exception:
        return None


def parse(country='South Korea', iso3='KOR'):
    service_key = os.environ.get('G2B_SERVICE_KEY', '')
    if not service_key:
        print('  [g2b_korea] G2B_SERVICE_KEY not set — skipping (register at data.go.kr)')
        return []

    session = requests.Session()
    seen = set()
    results = []

    for term in SEARCH_TERMS:
        items = _fetch_api(session, service_key, term)
        for item in items:
            bid_no = item.get('bidNtceNo', '')
            title = item.get('bidNtceNm', '').strip()
            detail_url = item.get('ntceSpecDocUrl', '') or f'https://www.g2b.go.kr/ep/tbid/tbBidPbancListFwd.do?bidNtceNo={bid_no}'
            if not title or detail_url in seen:
                continue
            seen.add(detail_url)
            buyer = item.get('ntceInsttNm', '')
            pub_date = item.get('bidNtceDt', '')[:10] if item.get('bidNtceDt') else ''
            deadline = item.get('bidClseDt', '')[:10] if item.get('bidClseDt') else ''
            amount = _parse_amount(item.get('presmptPrce'))
            snippet = f"{buyer} | {item.get('bidMethdNm','')} | {item.get('cntrctCnclsMthdNm','')} | {pub_date}"

            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'url': detail_url,
                'published_date': pub_date,
                'deadline_date': deadline,
                'status': 'Open',
                'buyer': buyer,
                'amount': amount, 'currency': 'KRW',
                'snippet': snippet[:300],
                'score': score(title, snippet),
            })

    print(f'  [g2b_korea] {len(results)} notices found')
    return results
