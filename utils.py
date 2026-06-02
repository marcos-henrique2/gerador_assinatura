# utils.py
"""Funções auxiliares compartilhadas (slug e normalização de site)."""
import re
import unicodedata
from urllib.parse import urlparse

# Esquemas de URL bloqueados por segurança (XSS)
_ESQUEMAS_PERIGOSOS = ('javascript:', 'data:', 'vbscript:', 'file:')


def gerar_slug(nome: str) -> str:
    """Gera um slug ASCII a partir do nome de exibição da marca.

    Ex.: 'Citroën' -> 'citroen', 'Navesa Porangatu' -> 'navesa-porangatu'.
    Usado como chave de arquivo de logo (imutável após criada).
    """
    texto = unicodedata.normalize('NFKD', nome)
    texto = texto.encode('ascii', 'ignore').decode('ascii')
    texto = texto.lower().strip()
    texto = re.sub(r'[^a-z0-9]+', '-', texto)
    texto = texto.strip('-')
    return texto or 'marca'


def site_eh_seguro(valor: str) -> bool:
    """Valida um domínio/URL de site, bloqueando esquemas perigosos."""
    if not valor:
        return True  # campo opcional
    bruto = valor.strip().lower()
    if any(bruto.startswith(esq) for esq in _ESQUEMAS_PERIGOSOS):
        return False
    # Domínio simples: letras/números/hífen + ao menos um ponto + TLD
    candidato = bruto
    if candidato.startswith(('http://', 'https://')):
        candidato = urlparse(bruto).netloc
    candidato = candidato.split('/')[0]
    padrao = re.compile(r'^([a-z0-9](-?[a-z0-9])*\.)+[a-z]{2,}$')
    return bool(padrao.match(candidato))


def normalizar_site_para_href(valor: str) -> str:
    """Normaliza um site para um href https seguro.

    Retorna string vazia se o valor for inseguro/ inválido — o template
    deve então omitir o link.
    """
    if not valor or not site_eh_seguro(valor):
        return ''
    bruto = valor.strip()
    if bruto.lower().startswith(('http://', 'https://')):
        parsed = urlparse(bruto)
        dominio = parsed.netloc + parsed.path
    else:
        dominio = bruto
    dominio = dominio.strip('/')
    return f'https://{dominio}'
