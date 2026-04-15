# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Script de otimização de logos para assinaturas de e-mail (Zimbra).
Limite do Zimbra: 10.240 caracteres. 
Meta: cada logo abaixo de ~6 KB (= ~8.000 chars em Base64).
"""

import os
import sys
from PIL import Image

# Garante saida UTF-8 no Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PASTA_LOGOS = os.path.join(os.path.dirname(__file__), "static", "images")
LARGURA_MAX = 200      # px — largura máxima da logo na assinatura
ALTURA_MAX  = 80       # px — altura máxima
TAMANHO_ALVO = 5_000   # bytes — limite alvo (~6.700 chars Base64 + ~1.200 HTML < 10.240 Zimbra)


def otimizar_imagem(caminho: str) -> int:
    """Redimensiona e comprime uma imagem PNG para ficar abaixo de TAMANHO_ALVO bytes."""
    img = Image.open(caminho).convert("RGBA")

    # 1. Compoe sobre fundo branco para preservar logos com transparencia
    fundo = Image.new("RGBA", img.size, (255, 255, 255, 255))
    fundo.paste(img, mask=img.split()[3])  # usa canal alpha como mascara
    img_rgb = fundo.convert("RGB")

    # 2. Redimensiona mantendo proporcao
    img_rgb.thumbnail((LARGURA_MAX, ALTURA_MAX), Image.LANCZOS)

    # 3. Converte para paleta (modo P) — drastica reducao de tamanho
    img_p = img_rgb.convert("P", palette=Image.ADAPTIVE, colors=256)
    img_p.save(caminho, format="PNG", optimize=True, compress_level=9)
    tamanho = os.path.getsize(caminho)

    # 4. Se ainda for grande, reduz o numero de cores progressivamente
    if tamanho > TAMANHO_ALVO:
        for cores in [128, 64, 32]:
            img_p = img_rgb.convert("P", palette=Image.ADAPTIVE, colors=cores)
            img_p.save(caminho, format="PNG", optimize=True, compress_level=9)
            tamanho = os.path.getsize(caminho)
            if tamanho <= TAMANHO_ALVO:
                break

    return tamanho


def main():
    print("=" * 55)
    print("  Otimizador de Logos — Gerador de Assinaturas Navesa")
    print("=" * 55)

    arquivos = [f for f in os.listdir(PASTA_LOGOS) if f.lower().endswith(".png")]

    if not arquivos:
        print("Nenhum arquivo .png encontrado em static/images/")
        return

    total_antes = 0
    total_depois = 0

    for nome in sorted(arquivos):
        caminho = os.path.join(PASTA_LOGOS, nome)
        antes = os.path.getsize(caminho)
        total_antes += antes

        depois = otimizar_imagem(caminho)
        total_depois += depois

        base64_chars = int(depois * 1.3333)
        status = "[OK]" if depois <= TAMANHO_ALVO else "[!!]"

        print(f"{status} {nome:<30} {antes/1024:>6.1f} KB -> {depois/1024:>5.1f} KB  (~{base64_chars:,} chars Base64)")

    print("-" * 55)
    print(f"   Total: {total_antes/1024:.1f} KB → {total_depois/1024:.1f} KB")
    print()
    print("Logos otimizadas com sucesso! Execute app.py normalmente.")
    print("=" * 55)


if __name__ == "__main__":
    main()
