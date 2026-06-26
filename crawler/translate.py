"""Shared translation utility — unofficial Google Translate API.

Usage:
    from crawler.translate import translate_to_en
    title_en = translate_to_en("Contratación de sistema electoral", sl='es')
"""
import time
import requests
import urllib3
urllib3.disable_warnings()

_CACHE: dict = {}
_LAST_CALL = 0.0
_MIN_INTERVAL = 0.06  # 60ms between calls to avoid rate limiting


def translate_to_en(text: str, sl: str = 'auto') -> str:
    """Translate text to English via unofficial Google Translate.

    sl: ISO 639-1 source language code, or 'auto' for detection.
        Pass 'en' to skip translation (returns text unchanged).
    Returns original text on any error.
    """
    if not text or not text.strip():
        return text
    if sl == 'en':
        return text

    key = (text[:300], sl)
    if key in _CACHE:
        return _CACHE[key]

    global _LAST_CALL
    elapsed = time.time() - _LAST_CALL
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)

    try:
        r = requests.get(
            'https://translate.googleapis.com/translate_a/single',
            params={
                'client': 'gtx', 'sl': sl, 'tl': 'en', 'dt': 't',
                'q': text[:500],
            },
            timeout=8, verify=False,
        )
        _LAST_CALL = time.time()
        data = r.json()
        translated = ''.join(seg[0] for seg in data[0] if seg[0]).strip()
        result = translated or text
        _CACHE[key] = result
        return result
    except Exception:
        _LAST_CALL = time.time()
        return text
