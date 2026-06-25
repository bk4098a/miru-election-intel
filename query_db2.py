# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('C:/Users/KIM/Downloads/miru-election-intel/data/election_technology_world.db')
cur = conn.cursor()

targets_iso3 = ['BRA','PRY','VEN','IND','COD','BTN','BEL','ALB','OMN','ARE']

print('--- portal_analysis ---')
cur.execute('PRAGMA table_info(portal_analysis)')
acols = [r[1] for r in cur.fetchall()]
print('cols:', acols)

cur.execute('SELECT * FROM portal_analysis WHERE iso3 IN ({})'.format(','.join('?' for _ in targets_iso3)), targets_iso3)
for r in cur.fetchall():
    print(r)

print('\n--- All portals for these countries ---')
cur.execute('SELECT iso3, portal_name, url, portal_type, notes FROM machine_voting_portals WHERE iso3 IN ({})'.format(','.join('?' for _ in targets_iso3)), targets_iso3)
for r in cur.fetchall():
    print(r)

conn.close()
