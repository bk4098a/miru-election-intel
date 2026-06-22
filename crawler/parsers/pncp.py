"""Brazil — PNCP REST API (Plataforma Nacional de Contratações Públicas)"""
import requests
from crawler.keywords import score, is_election_related

BASE = 'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacoes'
PORTAL = 'pncp.gov.br'
KEYWORDS = ['eleitoral', 'eleição', 'votação', 'urna', 'biometria', 'election', 'ballot']


def _fetch_page(session, keyword, page=1, size=50):
    try:
        r = session.get(BASE, params={
            'q': keyword, 'pagina': page, 'tamanhoPagina': size
        }, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get('data', data) if isinstance(data, dict) else data
    except Exception as e:
        print(f'  [pncp] error ({keyword} p{page}): {e}')
        return []


def parse(country='Brazil', iso3='BRA'):
    session = requests.Session()
    session.headers['Accept'] = 'application/json'

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
            if not is_election_related(title):
                continue

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
