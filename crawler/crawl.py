"""
miru-election-intel — P1 portal crawler
Targets: Kazakhstan, Brazil, Ghana, Bahrain, Bhutan, Albania, Jamaica, Kyrgyzstan
"""
import sys
import os
import time
import argparse

# allow `python crawler/crawl.py` from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.parsers import PARSERS
from crawler import storage


def run(targets=None, dry_run=False, delay=1.0):
    conn = None if dry_run else storage.get_conn()
    total_new = 0
    summary = []

    active = [(c, iso, fn) for c, iso, fn in PARSERS if not targets or iso in targets or c in targets]

    for country, iso3, parse_fn in active:
        print(f'\n[{iso3}] {country}')
        t0 = time.time()
        try:
            records = parse_fn(country=country, iso3=iso3)
        except Exception as e:
            print(f'  ERROR: {e}')
            records = []

        elapsed = time.time() - t0
        if not dry_run and records:
            n = storage.upsert(conn, records)
            total_new += n
            summary.append((country, iso3, len(records), n, elapsed))
        else:
            summary.append((country, iso3, len(records), 0, elapsed))

        if delay > 0:
            time.sleep(delay)

    if conn:
        conn.close()

    print('\n' + '='*60)
    print(f'{"Country":<15} {"ISO":>4}  {"Found":>6}  {"Saved":>6}  {"Time":>5}s')
    print('-'*60)
    for c, iso, found, saved, t in summary:
        print(f'{c:<15} {iso:>4}  {found:>6}  {saved:>6}  {t:>5.1f}')
    print('='*60)
    print(f'Total saved: {total_new}')
    print(f'DB: {os.path.abspath(storage.DB_PATH)}')


def main():
    parser = argparse.ArgumentParser(description='miru-election-intel crawler')
    parser.add_argument('--targets', nargs='+', help='ISO3 or country names to run (default: all)')
    parser.add_argument('--dry-run', action='store_true', help='Parse but do not write to DB')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between portals (seconds)')
    args = parser.parse_args()
    run(targets=args.targets, dry_run=args.dry_run, delay=args.delay)


if __name__ == '__main__':
    main()
