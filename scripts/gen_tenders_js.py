"""Generate data/tenders_data.js from election_intel_tenders.db.
Usage: python scripts/gen_tenders_js.py
"""
import json
import os
import sqlite3
import re
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'election_intel_tenders.db')
OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'tenders_data.js')
LIMIT = 2000

REGION_MAP = {
    # East Asia
    'KOR': 'East Asia', 'JPN': 'East Asia', 'CHN': 'East Asia', 'MNG': 'East Asia', 'TWN': 'East Asia',
    # Southeast Asia
    'PHL': 'Southeast Asia', 'THA': 'Southeast Asia', 'VNM': 'Southeast Asia', 'IDN': 'Southeast Asia',
    'MYS': 'Southeast Asia', 'MMR': 'Southeast Asia', 'KHM': 'Southeast Asia', 'LAO': 'Southeast Asia',
    'SGP': 'Southeast Asia', 'BRN': 'Southeast Asia', 'TLS': 'Southeast Asia',
    # South Asia
    'IND': 'South Asia', 'BGD': 'South Asia', 'PAK': 'South Asia', 'LKA': 'South Asia',
    'NPL': 'South Asia', 'BTN': 'South Asia', 'MDV': 'South Asia',
    # Central Asia
    'KAZ': 'Central Asia', 'KGZ': 'Central Asia', 'UZB': 'Central Asia', 'TJK': 'Central Asia',
    'TKM': 'Central Asia', 'AFG': 'Central Asia',
    # Middle East
    'IRQ': 'Middle East', 'BHR': 'Middle East', 'KWT': 'Middle East', 'SAU': 'Middle East',
    'ARE': 'Middle East', 'OMN': 'Middle East', 'YEM': 'Middle East', 'JOR': 'Middle East',
    'LBN': 'Middle East', 'SYR': 'Middle East', 'PSE': 'Middle East', 'ISR': 'Middle East',
    # East Africa
    'KEN': 'East Africa', 'TZA': 'East Africa', 'UGA': 'East Africa', 'ETH': 'East Africa',
    'RWA': 'East Africa', 'BDI': 'East Africa', 'SOM': 'East Africa', 'DJI': 'East Africa',
    # West Africa
    'GHA': 'West Africa', 'NGA': 'West Africa', 'SEN': 'West Africa', 'CIV': 'West Africa',
    'MLI': 'West Africa', 'BFA': 'West Africa', 'GIN': 'West Africa', 'SLE': 'West Africa',
    'LBR': 'West Africa', 'TGO': 'West Africa', 'BEN': 'West Africa', 'GMB': 'West Africa',
    'GNB': 'West Africa', 'CPV': 'West Africa', 'MRT': 'West Africa',
    # Central Africa
    'COD': 'Central Africa', 'COG': 'Central Africa', 'CMR': 'Central Africa', 'CAF': 'Central Africa',
    'TCD': 'Central Africa', 'GAB': 'Central Africa', 'GNQ': 'Central Africa', 'STP': 'Central Africa',
    # Southern Africa
    'ZAF': 'Southern Africa', 'ZWE': 'Southern Africa', 'ZMB': 'Southern Africa', 'MOZ': 'Southern Africa',
    'BWA': 'Southern Africa', 'NAM': 'Southern Africa', 'LSO': 'Southern Africa', 'SWZ': 'Southern Africa',
    'MWI': 'Southern Africa', 'AGO': 'Southern Africa', 'MDG': 'Southern Africa',
    # North Africa
    'EGY': 'North Africa', 'MAR': 'North Africa', 'TUN': 'North Africa', 'DZA': 'North Africa',
    'LBY': 'North Africa', 'SDN': 'North Africa', 'SSD': 'North Africa',
    # Europe
    'ALB': 'Europe', 'SRB': 'Europe', 'BIH': 'Europe', 'MKD': 'Europe', 'MNE': 'Europe',
    'KOS': 'Europe', 'MDA': 'Europe', 'UKR': 'Europe', 'GEO': 'Europe', 'ARM': 'Europe', 'AZE': 'Europe',
    'BLR': 'Europe', 'RUS': 'Europe',
    # Americas
    'BRA': 'Latin America', 'MEX': 'Latin America', 'ARG': 'Latin America', 'COL': 'Latin America',
    'VEN': 'Latin America', 'PER': 'Latin America', 'CHL': 'Latin America', 'ECU': 'Latin America',
    'BOL': 'Latin America', 'PRY': 'Latin America', 'URY': 'Latin America', 'GTM': 'Latin America',
    'CRI': 'Latin America', 'PAN': 'Latin America', 'HND': 'Latin America', 'SLV': 'Latin America',
    'NIC': 'Latin America', 'DOM': 'Latin America', 'HTI': 'Latin America', 'JAM': 'Caribbean',
    'CUB': 'Caribbean', 'TTO': 'Caribbean',
    'USA': 'North America', 'CAN': 'North America',
}

CPV_PATTERNS = [
    ('election_equipment', re.compile(
        r'EVM|DRE|VVPAT|VCM|ACM|투표기|전자투표|투표단말|voting machine|ballot machine'
        r'|optical scanner|tabulator|ballot paper|용지|잉크|ink|ribbon|카트리지', re.I)),
    ('biometric', re.compile(
        r'biometric|fingerprint|facial|iris|BVR|voter registration kit|등록기|생체', re.I)),
    ('software', re.compile(
        r'software|system|platform|KIEMS|application|portal|결과전송|집계', re.I)),
    ('services', re.compile(
        r'training|maintenance|support|consulting|service|용역|교육|유지', re.I)),
]


def get_category(title, snippet):
    text = f'{title} {snippet}'
    for cat, pat in CPV_PATTERNS:
        if pat.search(text):
            return cat
    return 'other'


def main():
    if not os.path.exists(DB_PATH):
        print(f'DB not found: {DB_PATH}')
        print('Run crawler first: python crawler/crawl.py')
        with open(OUT_PATH, 'w', encoding='utf-8') as f:
            f.write('window.MIRU_TENDERS=[];\nwindow.MIRU_TENDERS_META={total:0,countries:[],last_crawled:null,generated_at:null};\n')
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        f'SELECT * FROM tenders ORDER BY crawled_at DESC, score DESC LIMIT {LIMIT}'
    ).fetchall()
    conn.close()

    tenders = []
    countries_seen = set()
    last_crawled = None

    for r in rows:
        iso3 = r['iso3'] or ''
        title = r['title'] or ''
        snippet = r['snippet'] or ''
        crawled = r['crawled_at'] or ''

        if crawled and (not last_crawled or crawled > last_crawled):
            last_crawled = crawled

        countries_seen.add(iso3)
        region = REGION_MAP.get(iso3, 'Other')
        category = get_category(title, snippet)

        tenders.append({
            'id': r['id'],
            'notice_key': r['notice_key'],
            'country': r['country'],
            'iso3': iso3,
            'region': region,
            'portal_name': r['portal_name'],
            'title': title,
            'url': r['url'],
            'published_date': r['published_date'] or '',
            'deadline_date': r['deadline_date'] or '',
            'status': r['status'] or 'Unknown',
            'buyer': r['buyer'] or '',
            'amount': r['amount'],
            'currency': r['currency'] or '',
            'snippet': snippet,
            'score': r['score'] or 0,
            'crawled_at': crawled,
            'category': category,
        })

    meta = {
        'total': len(tenders),
        'countries': sorted(countries_seen),
        'last_crawled': last_crawled,
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

    js = (
        '// Auto-generated by scripts/gen_tenders_js.py — do not edit\n'
        f'window.MIRU_TENDERS = {json.dumps(tenders, ensure_ascii=False, indent=2)};\n'
        f'window.MIRU_TENDERS_META = {json.dumps(meta, ensure_ascii=False)};\n'
    )

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(js)

    print(f'Generated {OUT_PATH}')
    print(f'Tenders: {len(tenders)}, Countries: {len(countries_seen)}, Last crawled: {last_crawled}')


if __name__ == '__main__':
    main()
