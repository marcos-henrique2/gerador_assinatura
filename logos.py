# logos.py
"""Processamento e otimização de logos enviadas pelo painel admin.

Reaproveita os parâmetros e a lógica de otimização de otimizar_logos.py,
mas expõe uma função importável (processar_upload) que valida o PNG real,
otimiza e grava em static/images/<slug>.png.
"""
import io
import os

from PIL import Image
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_LOGOS = os.path.join(BASE_DIR, 'static', 'images')

LARGURA_MAX = 200      # px — largura máxima da logo na assinatura
ALTURA_MAX = 80        # px — altura máxima
TAMANHO_ALVO = 5_000   # bytes — limite alvo


class LogoInvalida(Exception):
    """Erro de validação/processamento de uma logo enviada."""


def _validar_png(file_storage) -> Image.Image:
    """Garante que o arquivo enviado é um PNG real. Retorna a imagem aberta."""
    file_storage.stream.seek(0)
    dados = file_storage.stream.read()
    if not dados:
        raise LogoInvalida('Arquivo vazio.')

    # 1ª passada: verify() valida a integridade mas invalida o objeto Image
    try:
        verificador = Image.open(io.BytesIO(dados))
        verificador.verify()
    except Exception:
        raise LogoInvalida('Arquivo não é uma imagem válida.')

    if verificador.format != 'PNG':
        raise LogoInvalida('A logo precisa estar no formato PNG.')

    # 2ª passada: reabre para uso real (verify() consome o stream)
    img = Image.open(io.BytesIO(dados))
    img.load()
    return img


def _otimizar(img: Image.Image) -> bytes:
    """Redimensiona/comprime a imagem e retorna os bytes do PNG final."""
    img = img.convert('RGBA')

    # Compoe sobre fundo branco para preservar logos com transparencia
    fundo = Image.new('RGBA', img.size, (255, 255, 255, 255))
    fundo.paste(img, mask=img.split()[3])
    img_rgb = fundo.convert('RGB')

    # Redimensiona mantendo proporcao
    img_rgb.thumbnail((LARGURA_MAX, ALTURA_MAX), Image.LANCZOS)

    def _render(cores: int) -> bytes:
        buf = io.BytesIO()
        img_p = img_rgb.convert('P', palette=Image.ADAPTIVE, colors=cores)
        img_p.save(buf, format='PNG', optimize=True, compress_level=9)
        return buf.getvalue()

    saida = _render(256)
    if len(saida) > TAMANHO_ALVO:
        for cores in (128, 64, 32):
            saida = _render(cores)
            if len(saida) <= TAMANHO_ALVO:
                break
    return saida


def processar_upload(file_storage, slug: str) -> str:
    """Valida, otimiza e grava a logo em static/images/<slug>.png.

    O nome do arquivo é derivado do slug (NÃO do nome enviado).
    Retorna o nome do arquivo gravado (ex.: 'renault.png').
    """
    slug_seguro = secure_filename(slug) or 'logo'
    img = _validar_png(file_storage)
    dados_png = _otimizar(img)

    os.makedirs(PASTA_LOGOS, exist_ok=True)
    nome_arquivo = f'{slug_seguro}.png'
    destino = os.path.join(PASTA_LOGOS, nome_arquivo)
    with open(destino, 'wb') as f:
        f.write(dados_png)
    return nome_arquivo
