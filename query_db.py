import sqlite3

conn = sqlite3.connect('C:/Users/KIM/Downloads/miru-election-intel/data/election_technology_world.db')
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables:', cur.fetchall())

cur.execute('PRAGMA table_info(countries)')
cols = [r[1] for r in cur.fetchall()]
print('countries cols:', cols)

# Fetch the 10 target countries
targets = ['Brazil','Paraguay','Venezuela','India','Congo, Dem. Rep.','Congo','Bhutan','Belgium','Albania','Oman','United Arab Emirates','UAE']
targets_iso3 = ['BRA','PRY','VEN','IND','COD','BTN','BEL','ALB','OMN','ARE']

print('\n--- countries rows for targets ---')
cur.execute('SELECT * FROM countries WHERE iso3 IN ({})'.format(','.join('?' for _ in targets_iso3)), targets_iso3)
rows = cur.fetchall()
for r in rows:
    print(r)

print('\n--- machine_voting_portals ---')
cur.execute('PRAGMA table_info(machine_voting_portals)')
pcols = [r[1] for r in cur.fetchall()]
print('portal cols:', pcols)
cur.execute('SELECT * FROM machine_voting_portals WHERE iso3 IN ({})'.format(','.join('?' for _ in targets_iso3)), targets_iso3)
for r in cur.fetchall():
    print(r)

print('\n--- portal_analysis ---')
cur.execute('PRAGMA table_info(portal_analysis)')
acols = [r[1] for r in cur.fetchall()]
print('analysis cols:', acols)
cur.execute('SELECT * FROM portal_analysis WHERE iso3 IN ({})'.format(','.join('?' for _ in targets_iso3)), targets_iso3)
for r in cur.fetchall():
    print(r)

conn.close()
