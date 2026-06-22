import re

STRONG = [
    'election', 'electoral', 'ballot', 'polling', 'referendum',
    'выборы', 'избирательн', 'голосован',   # Russian
    'eleição', 'eleitoral', 'votação', 'urna eletrônica',  # Portuguese
    'شايلوو', 'шайлоо',    # Kyrgyz
    'انتخابات',             # Arabic
    'valimine', 'valimis',  # Estonian
    'EVM', 'DRE', 'VVPAT', 'e-voting', 'evoting',
]

WEAK = [
    'biometric', 'fingerprint', 'voter', 'vote', 'voting machine',
    'optical mark', 'OMR', 'scanner', 'tabulation', 'results transmission',
    'electronic poll', 'e-poll', 'KIEMS', 'BVD', 'BVMS',
    'ACM', 'VCM', 'precinct',
]

NOISE = [
    'employee election', 'board election', 'union election',
    'director election', 'officer election',
]

_strong_re = re.compile('|'.join(re.escape(k) for k in STRONG), re.I)
_weak_re   = re.compile('|'.join(re.escape(k) for k in WEAK), re.I)
_noise_re  = re.compile('|'.join(re.escape(k) for k in NOISE), re.I)


def score(title: str, snippet: str = '') -> int:
    text = f"{title} {snippet}"
    if _noise_re.search(text):
        return -30
    s = 0
    if _strong_re.search(text):
        s += 40
    if _weak_re.search(text):
        s += 15
    return s


def is_election_related(title: str, snippet: str = '') -> bool:
    return score(title, snippet) > 0
