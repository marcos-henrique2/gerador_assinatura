# app.py
import base64
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from flask import Flask, abort, render_template, request
from flask_wtf import CSRFProtect

import storage
from auth import admin_bp
from utils import normalizar_site_para_href

load_dotenv()

app = Flask(__name__)

# ── Configuração ──
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise RuntimeError(
        'SECRET_KEY não definida. Configure o arquivo .env '
        '(rode configurar_admin.bat para gerar as chaves).')

app.config.update(
    SECRET_KEY=secret_key,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,  # HTTP em rede local (sem HTTPS)
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5 MB
)

csrf = CSRFProtect(app)

app.register_blueprint(admin_bp)


@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}


@app.route('/')
def index():
    return render_template('index.html', marcas=storage.get_marcas())


@app.route('/gerar/<marca>')
def formulario(marca):
    dados_marca = storage.get_marcas().get(marca)
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
    marcas = storage.get_marcas()

    logo_arquivo = None
    if marca_nome in marcas:
        logo_arquivo = marcas[marca_nome]['logo']

    logo_url = logo_para_base64(logo_arquivo) if logo_arquivo else None

    # Verifica se a logo ja tem barra propria (para nao duplicar o separador)
    logo_tem_barra = False
    if marca_nome in marcas:
        logo_tem_barra = marcas[marca_nome].get('logo_tem_barra', False)

    site_href = normalizar_site_para_href(dados_formulario.get('site', ''))

    return render_template('resultado.html',
                           dados=dados_formulario,
                           logo_url=logo_url,
                           logo_tem_barra=logo_tem_barra,
                           site_href=site_href)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,
            debug=os.environ.get("FLASK_DEBUG", "0") == "1")
