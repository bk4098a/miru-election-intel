from .goszakup       import parse as parse_goszakup
from .pncp           import parse as parse_pncp
from .ghaneps        import parse as parse_ghaneps
from .bahrain        import parse as parse_bahrain
from .wp_portals     import parse_ecb_bhutan, parse_kqz_albania
from .gojep          import parse as parse_gojep
from .zakupki_kg     import parse as parse_zakupki_kg
from .philgeps       import parse as parse_philgeps
from .g2b_korea      import parse as parse_g2b_korea
from .tenders_kenya  import parse as parse_tenders_kenya
from .ihec_iraq      import parse as parse_ihec_iraq
from .dncp_paraguay  import parse as parse_dncp_paraguay
from .samgov_usa     import parse as parse_samgov_usa
from .etenders_za    import parse as parse_etenders_za

# Each entry: (country, iso3, parse_fn, mode)
# mode = 'static'     → requests / lxml / BeautifulSoup only
# mode = 'playwright' → requires Chromium (JS rendering)
PARSERS = [
    # ── Static portals ──────────────────────────────────────────────────────
    ('Kazakhstan',  'KAZ', parse_goszakup,    'static'),    # needs GOSZAKUP_TOKEN
    ('Brazil',      'BRA', parse_pncp,        'static'),    # ConnectionReset / WAF issues
    ('Ghana',       'GHA', parse_ghaneps,     'static'),    # login wall on search
    ('Bahrain',     'BHR', parse_bahrain,     'static'),    # HTML table (no current election tenders)
    ('Bhutan',      'BTN', parse_ecb_bhutan,  'static'),    # WP REST API (may timeout)
    ('Kyrgyzstan',  'KGZ', parse_zakupki_kg,  'static'),    # OCDS API (timeout) → SPA needs Playwright
    ('Philippines', 'PHL', parse_philgeps,    'playwright'), # ✅ notices.philgeps.gov.ph keyword search
    ('South Korea', 'KOR', parse_g2b_korea,   'static'),    # needs G2B_SERVICE_KEY
    ('Kenya',       'KEN', parse_tenders_kenya,'static'),   # ✅ iebc.or.ke static HTML → PDF links
    ('Iraq',        'IRQ', parse_ihec_iraq,   'static'),    # ✅ WP site, 67 notices
    ('Paraguay',    'PRY', parse_dncp_paraguay,'static'),   # ✅ OCDS API
    ('United States','USA', parse_samgov_usa, 'static'),    # needs SAMGOV_API_KEY
    ('South Africa','ZAF', parse_etenders_za, 'static'),   # ✅ etenders.gov.za DataTables API, IEC + election keywords
    # ── Playwright portals ─────────────────────────────────────────────────
    ('Jamaica',     'JAM', parse_gojep,       'playwright'),  # JSF app
    ('Albania',     'ALB', parse_kqz_albania, 'playwright'),  # ✅ Next.js, 3 notices
]
