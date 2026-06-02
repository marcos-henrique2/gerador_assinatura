# storage.py
"""Camada de persistência das marcas.

Fonte de verdade = data/marcas.json (não versionado no servidor).
Todas as gravações são serializadas por um Lock, fazem backup do estado
anterior e usam escrita atômica (arquivo temporário + os.replace).
"""
import json
import os
import shutil
import tempfile
import threading
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MARCAS_PATH = os.path.join(DATA_DIR, 'marcas.json')
EXEMPLO_PATH = os.path.join(DATA_DIR, 'marcas.example.json')
BACKUPS_DIR = os.path.join(DATA_DIR, 'backups')

MAX_BACKUPS = 20

_lock = threading.Lock()
_marcas: dict = {}


def _garantir_fonte_de_dados() -> None:
    """Garante que data/marcas.json exista no primeiro boot.

    Em um clone novo, marcas.json (gitignored) não existe — só a seed
    versionada marcas.example.json. Nesse caso, copia o exemplo para
    marcas.json. Se marcas.json já existe (caso normal/servidor em uso),
    nada é alterado: NUNCA sobrescreve o arquivo real com o exemplo.
    """
    if os.path.exists(MARCAS_PATH):
        return
    if not os.path.exists(EXEMPLO_PATH):
        raise RuntimeError(
            "Nenhuma fonte de dados encontrada: faltam "
            "data/marcas.json e data/marcas.example.json."
        )
    os.makedirs(DATA_DIR, exist_ok=True)
    shutil.copyfile(EXEMPLO_PATH, MARCAS_PATH)


def _carregar_do_disco() -> dict:
    _garantir_fonte_de_dados()
    with open(MARCAS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def reload() -> dict:
    """Recarrega o dicionário de marcas a partir do disco."""
    global _marcas
    with _lock:
        _marcas = _carregar_do_disco()
    return _marcas


def get_marcas() -> dict:
    """Retorna o dicionário de marcas em memória."""
    return _marcas


def _fazer_backup() -> None:
    """Copia o marcas.json atual para data/backups, mantendo os últimos 20."""
    if not os.path.exists(MARCAS_PATH):
        return
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    carimbo = datetime.now().strftime('%Y%m%d-%H%M%S')
    destino = os.path.join(BACKUPS_DIR, f'marcas-{carimbo}.json')
    # Evita sobrescrever se houver duas gravações no mesmo segundo
    contador = 1
    while os.path.exists(destino):
        destino = os.path.join(BACKUPS_DIR, f'marcas-{carimbo}-{contador}.json')
        contador += 1
    with open(MARCAS_PATH, 'r', encoding='utf-8') as origem:
        conteudo = origem.read()
    with open(destino, 'w', encoding='utf-8') as saida:
        saida.write(conteudo)
    _limpar_backups_antigos()


def _limpar_backups_antigos() -> None:
    if not os.path.isdir(BACKUPS_DIR):
        return
    backups = sorted(
        f for f in os.listdir(BACKUPS_DIR)
        if f.startswith('marcas-') and f.endswith('.json')
    )
    excedente = len(backups) - MAX_BACKUPS
    for nome in backups[:max(0, excedente)]:
        try:
            os.remove(os.path.join(BACKUPS_DIR, nome))
        except OSError:
            pass


def salvar_marcas(dados: dict) -> None:
    """Persiste o dicionário de marcas de forma atômica e com backup.

    Preserva a ordem de inserção e os acentos (UTF-8, sem sort_keys).
    Atualiza o dicionário em memória após gravar.
    """
    global _marcas
    with _lock:
        os.makedirs(DATA_DIR, exist_ok=True)
        _fazer_backup()
        # Escrita atômica: grava em arquivo temporário no MESMO diretório
        fd, tmp_path = tempfile.mkstemp(
            dir=DATA_DIR, prefix='.marcas-', suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as tmp:
                json.dump(dados, tmp, ensure_ascii=False, indent=2)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(tmp_path, MARCAS_PATH)
        except BaseException:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise
        _marcas = dados


# Carrega ao importar o módulo
reload()
