"""Translate existing Paraguay (PRY) titles in the DB to English.
Run once: python scripts/translate_pry_titles.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sqlite3
import time
import requests
import urllib3
import os
urllib3.disable_warnings()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'election_intel_tenders.db')


def translate_es_en(text):
    if not text:
        return text
    try:
        r = requests.get(
            'https://translate.googleapis.com/translate_a/single',
            params={'client': 'gtx', 'sl': 'es', 'tl': 'en', 'dt': 't', 'q': text},
            timeout=8, verify=False,
        )
        data = r.json()
        return ''.join(seg[0] for seg in data[0] if seg[0])
    except Exception as e:
        print(f'  translate error: {e}')
        return None


def main():
    conn = sqlite3.connect(DB_PATH)

    # Ensure column exists
    try:
        conn.execute('ALTER TABLE tenders ADD COLUMN title_en TEXT')
        conn.commit()
        print('Added title_en column')
    except sqlite3.OperationalError:
        pass

    rows = conn.execute(
        "SELECT id, title FROM tenders WHERE iso3='PRY' AND (title_en IS NULL OR title_en='')"
    ).fetchall()
    print(f'Translating {len(rows)} Paraguay records...')

    for i, (rid, title) in enumerate(rows):
        translated = translate_es_en(title)
        if translated and translated != title:
            conn.execute('UPDATE tenders SET title_en=? WHERE id=?', (translated, rid))
            print(f'  [{i+1}/{len(rows)}] {title[:50]} → {translated[:50]}')
        else:
            print(f'  [{i+1}/{len(rows)}] (skipped) {title[:60]}')
        if i % 10 == 9:
            conn.commit()
        time.sleep(0.05)

    conn.commit()
    conn.close()
    print('Done.')


if __name__ == '__main__':
    main()
