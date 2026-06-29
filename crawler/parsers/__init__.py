from .goszakup         import parse as parse_goszakup
from .pncp             import parse as parse_pncp
from .ghaneps          import parse as parse_ghaneps
from .bahrain          import parse as parse_bahrain
from .wp_portals       import parse_ecb_bhutan, parse_kqz_albania
from .gojep            import parse as parse_gojep
from .zakupki_kg       import parse as parse_zakupki_kg
from .philgeps         import parse as parse_philgeps
from .g2b_korea        import parse as parse_g2b_korea
from .tenders_kenya    import parse as parse_tenders_kenya
from .ihec_iraq        import parse as parse_ihec_iraq
from .dncp_paraguay    import parse as parse_dncp_paraguay
from .samgov_usa       import parse as parse_samgov_usa
from .etenders_za      import parse as parse_etenders_za
# ── New parsers (8 countries) ───────────────────────────────────────────────
from .compr_ar         import parse as parse_compr_ar
from .riigihanked_est  import parse as parse_riigihanked_est
from .spa_georgia      import parse as parse_spa_georgia
from .tenderboard_omn  import parse as parse_tenderboard_omn
from .cppp_india       import parse as parse_cppp_india
from .armp_drc         import parse as parse_armp_drc
from .ejn_bosnia       import parse as parse_ejn_bosnia
from .gpa_mongolia     import parse as parse_gpa_mongolia
from .bcn_barcelona    import parse as parse_bcn_barcelona

# Each entry: (country, iso3, parse_fn, mode)
# mode = 'static'     → requests / lxml / BeautifulSoup only
# mode = 'playwright' → requires Chromium (JS rendering)
PARSERS = [
    # ── Static portals ──────────────────────────────────────────────────────
    ('Kazakhstan',              'KAZ', parse_goszakup,         'static'),  # needs GOSZAKUP_TOKEN
    ('Brazil',                  'BRA', parse_pncp,             'static'),  # WAF — alt endpoint added
    ('Ghana',                   'GHA', parse_ghaneps,          'static'),  # login wall
    ('Bahrain',                 'BHR', parse_bahrain,          'static'),  # ✅ HTML table
    ('Bhutan',                  'BTN', parse_ecb_bhutan,       'static'),  # WP API / static fallback
    ('Kyrgyzstan',              'KGZ', parse_zakupki_kg,       'static'),  # OCDS API
    ('South Korea',             'KOR', parse_g2b_korea,        'static'),  # needs G2B_SERVICE_KEY
    ('Kenya',                   'KEN', parse_tenders_kenya,    'static'),  # ✅ iebc.or.ke
    ('Iraq',                    'IRQ', parse_ihec_iraq,        'static'),  # ✅ WP site
    ('Paraguay',                'PRY', parse_dncp_paraguay,    'static'),  # ✅ OCDS API + EN translation
    ('United States',           'USA', parse_samgov_usa,       'static'),  # needs SAMGOV_API_KEY
    ('South Africa',            'ZAF', parse_etenders_za,      'static'),  # ✅ etenders DataTables
    ('Argentina',               'ARG', parse_compr_ar,         'static'),  # OCDS API (same as PRY)
    ('Estonia',                 'EST', parse_riigihanked_est,  'static'),  # Riigihangete API
    ('Georgia',                 'GEO', parse_spa_georgia,      'static'),  # SPA REST API
    ('Oman',                    'OMN', parse_tenderboard_omn,  'static'),  # Tender Board HTML
    ('India',                   'IND', parse_cppp_india,       'static'),  # ECI tenders + CPPP
    ('Dem. Rep. Congo',         'COD', parse_armp_drc,         'static'),  # ARMP HTML + FR→EN
    ('Bosnia and Herzegovina',  'BIH', parse_ejn_bosnia,       'static'),  # eJN HTML + BS→EN
    ('Mongolia',                'MNG', parse_gpa_mongolia,     'static'),  # GPA API/HTML + MN→EN
    ('Spain',                   'ESP', parse_bcn_barcelona,    'static'),      # ✅ Barcelona City procurement
    # ── Playwright portals ─────────────────────────────────────────────────
    ('Philippines',             'PHL', parse_philgeps,         'playwright'),  # ✅ PhilGEPS keyword search
    ('Jamaica',                 'JAM', parse_gojep,            'playwright'),  # JSF app
    ('Albania',                 'ALB', parse_kqz_albania,      'playwright'),  # ✅ Next.js
]
