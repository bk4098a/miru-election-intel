"""Backfill title_en for Albania (ALB) and Iraq (IRQ) records in the DB.
Run once: python scripts/translate_alb_irq_titles.py
Then regenerate: python scripts/gen_tenders_js.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os
import sqlite3
import time
import requests
import urllib3
urllib3.disable_warnings()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'election_intel_tenders.db')

LANG_MAP = {'ALB': 'sq', 'IRQ': 'ar'}


def translate(text, sl):
    if not text:
        return text
    try:
        r = requests.get(
            'https://translate.googleapis.com/translate_a/single',
            params={'client': 'gtx', 'sl': sl, 'tl': 'en', 'dt': 't', 'q': text[:500]},
            timeout=8, verify=False,
        )
        data = r.json()
        return ''.join(seg[0] for seg in data[0] if seg[0]).strip()
    except Exception as e:
        print(f'  translate error: {e}')
        return None


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('ALTER TABLE tenders ADD COLUMN title_en TEXT')
        conn.commit()
        print('Added title_en column')
    except sqlite3.OperationalError:
        pass

    for iso3, sl in LANG_MAP.items():
        rows = conn.execute(
            "SELECT id, title FROM tenders WHERE iso3=? AND (title_en IS NULL OR title_en='')",
            (iso3,)
        ).fetchall()
        print(f'\nTranslating {len(rows)} {iso3} records (sl={sl})...')

        for i, (rid, title) in enumerate(rows):
            translated = translate(title, sl)
            if translated and translated != title:
                conn.execute('UPDATE tenders SET title_en=? WHERE id=?', (translated, rid))
                print(f'  [{i+1}/{len(rows)}] {title[:50]} → {translated[:50]}')
            else:
                print(f'  [{i+1}/{len(rows)}] (skipped) {title[:60]}')
            if i % 10 == 9:
                conn.commit()
            time.sleep(0.06)

    conn.commit()
    conn.close()
    print('\nDone. Run: python scripts/gen_tenders_js.py')


if __name__ == '__main__':
    main()
