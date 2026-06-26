import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'election_intel_tenders.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS tenders (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    notice_key    TEXT    UNIQUE NOT NULL,
    country       TEXT,
    iso3          TEXT,
    portal_name   TEXT,
    title         TEXT,
    title_en      TEXT,
    url           TEXT,
    published_date TEXT,
    deadline_date  TEXT,
    status        TEXT,
    buyer         TEXT,
    amount        REAL,
    currency      TEXT,
    snippet       TEXT,
    score         INTEGER DEFAULT 0,
    crawled_at    TEXT
);
-- Migrate: add title_en column if it doesn't exist yet
CREATE TABLE IF NOT EXISTS _dummy_migration(id INTEGER);
CREATE INDEX IF NOT EXISTS idx_iso3 ON tenders(iso3);
CREATE INDEX IF NOT EXISTS idx_crawled ON tenders(crawled_at);
"""


def make_key(iso3: str, url: str, title: str) -> str:
    raw = f"{iso3}|{url}|{title[:120]}"
    return hashlib.sha1(raw.encode()).hexdigest()[:20]


def get_conn():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    # Add title_en column if missing (migration for existing DBs)
    try:
        conn.execute('ALTER TABLE tenders ADD COLUMN title_en TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists
    return conn


def upsert(conn, records: list[dict]) -> int:
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    inserted = 0
    for r in records:
        key = make_key(r.get('iso3', ''), r.get('url', ''), r.get('title', ''))
        try:
            conn.execute("""
                INSERT INTO tenders
                    (notice_key, country, iso3, portal_name, title, title_en, url,
                     published_date, deadline_date, status, buyer, amount,
                     currency, snippet, score, crawled_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(notice_key) DO UPDATE SET
                    title=excluded.title,
                    title_en=excluded.title_en,
                    deadline_date=excluded.deadline_date,
                    status=excluded.status,
                    snippet=excluded.snippet,
                    score=excluded.score,
                    crawled_at=excluded.crawled_at
            """, (
                key,
                r.get('country'), r.get('iso3'), r.get('portal_name'),
                r.get('title'), r.get('title_en'),
                r.get('url'),
                r.get('published_date'), r.get('deadline_date'),
                r.get('status'), r.get('buyer'),
                r.get('amount'), r.get('currency'),
                r.get('snippet'), r.get('score', 0),
                now
            ))
            inserted += 1
        except Exception as e:
            print(f"  [storage] upsert error: {e}")
    conn.commit()
    return inserted
