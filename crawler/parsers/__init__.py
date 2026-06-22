from .goszakup   import parse as parse_goszakup
from .pncp       import parse as parse_pncp
from .ghaneps    import parse as parse_ghaneps
from .bahrain    import parse as parse_bahrain
from .wp_portals import parse_ecb_bhutan, parse_kqz_albania
from .gojep      import parse as parse_gojep
from .zakupki_kg import parse as parse_zakupki_kg

PARSERS = [
    ('Kazakhstan',  'KAZ', parse_goszakup),
    ('Brazil',      'BRA', parse_pncp),
    ('Ghana',       'GHA', parse_ghaneps),
    ('Bahrain',     'BHR', parse_bahrain),
    ('Bhutan',      'BTN', parse_ecb_bhutan),
    ('Albania',     'ALB', parse_kqz_albania),
    ('Jamaica',     'JAM', parse_gojep),
    ('Kyrgyzstan',  'KGZ', parse_zakupki_kg),
]
