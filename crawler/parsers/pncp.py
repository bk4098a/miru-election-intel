"""Brazil — PNCP REST API (Plataforma Nacional de Contratações Públicas)
Tries v2 endpoint first, falls back to v1 consulta endpoint.
"""
import requests
import urllib3
urllib3.disable_warnings()
from crawler.keywords import score

# Primary: v2 public search
BASE_V2   = 'https://pncp.gov.br/api/pncp/v1/orgaos/compras'
# Fallback: v1 consulta (may cause ConnectionReset / WAF block)
BASE_V1   = 'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacoes'
PORTAL = 'pncp.gov.br'
KEYWORDS = ['eleitoral', 'eleição', 'votação', 'urna', 'biometria', 'election', 'ballot']

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Referer': 'https://pncp.gov.br/',
}


def _fetch_page(session, keyword, page=1, size=50):
    # Try v2 search endpoint
    try:
        r = session.get(
            'https://pncp.gov.br/api/pncp/v1/editais/search',
            params={'q': keyword, 'pagina': page, 'tamanhoPagina': size},
            timeout=20, verify=False,
        )
        if r.status_code == 200:
            data = r.json()
            items = data.get('data') or data.get('content') or (data if isinstance(data, list) else [])
            if items:
                return items
    except Exception:
        pass

    # Fallback: consulta v1
    try:
        r = session.get(BASE_V1, params={
            'q': keyword, 'pagina': page, 'tamanhoPagina': size
        }, timeout=20, verify=False)
        if r.status_code == 200:
            data = r.json()
            return data.get('data', data) if isinstance(data, dict) else data
    except Exception as e:
        print(f'  [pncp] error ({keyword} p{page}): {e}')
    return []


def parse(country='Brazil', iso3='BRA'):
    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = False

    seen = set()
    results = []

    for kw in KEYWORDS:
        items = _fetch_page(session, kw)
        for item in items:
            url = item.get('linkSistemaOrigem') or \
                  f"https://pncp.gov.br/app/editais/{item.get('numeroControlePNCP','')}"
            title = item.get('objetoCompra') or item.get('descricao', '')
            if not title or url in seen:
                continue
            seen.add(url)
            amount = None
            try:
                amount = float(item.get('valorTotalEstimado') or 0) or None
            except Exception:
                pass

            results.append({
                'country': country, 'iso3': iso3, 'portal_name': PORTAL,
                'title': title, 'url': url,
                'published_date': item.get('dataPublicacaoPncp', ''),
                'deadline_date': item.get('dataEncerramentoProposta', ''),
                'status': item.get('situacaoCompraNome', ''),
                'buyer': item.get('orgaoEntidade', {}).get('razaoSocial', '') if isinstance(item.get('orgaoEntidade'), dict) else '',
                'amount': amount, 'currency': 'BRL',
                'snippet': item.get('informacaoComplementar', '')[:300],
                'score': score(title),
            })

    print(f'  [pncp] {len(results)} notices found')
    return results
