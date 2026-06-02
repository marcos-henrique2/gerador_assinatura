# app.py
from flask import Flask, render_template, abort, request
import json
import base64
import os
from datetime import datetime

app = Flask(__name__)


@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}


def carregar_marcas() -> dict:
    """Carrega o dicionário de marcas a partir de data/marcas.json."""
    caminho = os.path.join(os.path.dirname(__file__), 'data', 'marcas.json')
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)


MARCAS = carregar_marcas()


@app.route('/')
def index():
    return render_template('index.html', marcas=MARCAS)


@app.route('/gerar/<marca>')
def formulario(marca):
    dados_marca = MARCAS.get(marca)
    if not dados_marca:
        abort(404)
    lista_concessionarias = dados_marca['concessionarias'].keys()
    dados_json_para_frontend = dados_marca['concessionarias']
    return render_template('form.html',
                           nome_marca=marca,
                           concessionarias=lista_concessionarias,
                           dados_json=dados_json_para_frontend,
                           icone=dados_marca.get('icone', 'building'))


def logo_para_base64(nome_arquivo: str) -> str | None:
    """Lê a logo da pasta static/images e retorna como data URI Base64."""
    caminho = os.path.join(app.root_path, 'static', 'images', nome_arquivo)
    if not os.path.exists(caminho):
        return None
    ext = os.path.splitext(nome_arquivo)[1].lower().lstrip('.')
    mime = 'jpeg' if ext in ('jpg', 'jpeg') else ext
    with open(caminho, 'rb') as f:
        dados = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/{mime};base64,{dados}"


@app.route('/resultado', methods=['POST'])
def resultado():
    dados_formulario = request.form
    marca_nome = dados_formulario.get('marca_selecionada')

    logo_arquivo = None
    if marca_nome in MARCAS:
        logo_arquivo = MARCAS[marca_nome]['logo']

    logo_url = logo_para_base64(logo_arquivo) if logo_arquivo else None

    # Verifica se a logo ja tem barra propria (para nao duplicar o separador)
    logo_tem_barra = False
    if marca_nome in MARCAS:
        logo_tem_barra = MARCAS[marca_nome].get('logo_tem_barra', False)

    return render_template('resultado.html',
                           dados=dados_formulario,
                           logo_url=logo_url,
                           logo_tem_barra=logo_tem_barra)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,
            debug=os.environ.get("FLASK_DEBUG", "0") == "1")
