from .goszakup      import parse as parse_goszakup
from .pncp          import parse as parse_pncp
from .ghaneps       import parse as parse_ghaneps
from .bahrain       import parse as parse_bahrain
from .wp_portals    import parse_ecb_bhutan, parse_kqz_albania
from .gojep         import parse as parse_gojep
from .zakupki_kg    import parse as parse_zakupki_kg
from .philgeps      import parse as parse_philgeps
from .g2b_korea     import parse as parse_g2b_korea
from .tenders_kenya import parse as parse_tenders_kenya

PARSERS = [
    # Existing portals
    ('Kazakhstan',    'KAZ', parse_goszakup),
    ('Brazil',        'BRA', parse_pncp),
    ('Ghana',         'GHA', parse_ghaneps),
    ('Bahrain',       'BHR', parse_bahrain),
    ('Bhutan',        'BTN', parse_ecb_bhutan),
    ('Albania',       'ALB', parse_kqz_albania),
    ('Jamaica',       'JAM', parse_gojep),
    ('Kyrgyzstan',    'KGZ', parse_zakupki_kg),
    # New portals — Miru active markets + key election monitors
    ('Philippines',   'PHL', parse_philgeps),
    ('South Korea',   'KOR', parse_g2b_korea),
    ('Kenya',         'KEN', parse_tenders_kenya),
]
