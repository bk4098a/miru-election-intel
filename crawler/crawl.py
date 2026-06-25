"""
miru-election-intel — P1 portal crawler
Portals: KAZ, BRA, GHA, BHR, BTN, KGZ, PHL, KOR, KEN, IRQ, JAM, ALB

Modes:
  --mode static     → requests/lxml parsers only (default)
  --mode playwright → Playwright (headless Chromium) parsers only
  --mode all        → all parsers in sequence (static first, then playwright)
"""
import sys
import os
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.parsers import PARSERS
from crawler import storage


def run(targets=None, dry_run=False, delay=1.0, mode='all'):
    conn = None if dry_run else storage.get_conn()
    total_new = 0
    summary = []

    # Filter by target countries/iso3
    active = [
        (c, iso, fn, m) for c, iso, fn, m in PARSERS
        if (not targets or iso in targets or c in targets)
        and (mode == 'all' or m == mode)
    ]

    if not active:
        print(f'No parsers matched mode={mode!r} targets={targets}')
        return

    for country, iso3, parse_fn, pmode in active:
        print(f'\n[{iso3}] {country}  ({pmode})')
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
            summary.append((country, iso3, len(records), n, elapsed, pmode))
        else:
            summary.append((country, iso3, len(records), 0, elapsed, pmode))

        if delay > 0 and active.index((country, iso3, parse_fn, pmode)) < len(active) - 1:
            time.sleep(delay)

    if conn:
        conn.close()

    print('\n' + '='*68)
    print(f'{"Country":<15} {"ISO":>4}  {"Mode":>10}  {"Found":>6}  {"Saved":>6}  {"Time":>5}s')
    print('-'*68)
    for c, iso, found, saved, t, m in summary:
        print(f'{c:<15} {iso:>4}  {m:>10}  {found:>6}  {saved:>6}  {t:>5.1f}')
    print('='*68)
    print(f'Total saved: {total_new}')
    if not dry_run:
        print(f'DB: {os.path.abspath(storage.DB_PATH)}')


def main():
    p = argparse.ArgumentParser(description='miru-election-intel crawler')
    p.add_argument('--targets', nargs='+', help='ISO3 or country names (default: all)')
    p.add_argument('--dry-run', action='store_true', help='Parse but do not write to DB')
    p.add_argument('--delay', type=float, default=1.0, help='Seconds between portals')
    p.add_argument('--mode', choices=['static', 'playwright', 'all'], default='all',
                   help='static=requests only, playwright=Chromium only, all=both')
    args = p.parse_args()
    run(targets=args.targets, dry_run=args.dry_run, delay=args.delay, mode=args.mode)


if __name__ == '__main__':
    main()
