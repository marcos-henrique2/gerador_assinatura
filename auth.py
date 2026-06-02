# auth.py
"""Blueprint do painel administrativo (/admin).

Autenticação por senha única compartilhada (hash em ADMIN_PASSWORD_HASH).
Inclui login/logout, dashboard e CRUD de marcas e unidades.
"""
import copy
import os
from functools import wraps

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, session, url_for)
from werkzeug.security import check_password_hash

import storage
from forms import LoginForm, MarcaCriarForm, MarcaForm, UnidadeForm
from logos import (PASTA_LOGOS, TAMANHO_ALVO, LogoInvalida,
                   processar_upload)
from utils import gerar_slug

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _info_logo(nome_arquivo: str | None) -> dict | None:
    """Retorna dados da logo atual para preview (nome + cache-buster).

    O cache-buster usa o mtime do arquivo, garantindo que o navegador
    recarregue a imagem assim que uma nova logo for gravada.
    """
    if not nome_arquivo:
        return None
    caminho = os.path.join(PASTA_LOGOS, nome_arquivo)
    if not os.path.exists(caminho):
        return None
    return {
        'nome': nome_arquivo,
        'tamanho': os.path.getsize(caminho),
        'v': int(os.path.getmtime(caminho)),
    }


def _flash_otimizacao(resultado: dict) -> None:
    """Emite um flash informando o tamanho final da logo otimizada."""
    kb = resultado['tamanho'] / 1024
    if resultado['excedeu']:
        limite_kb = TAMANHO_ALVO / 1024
        flash(
            f'Atenção: a logo ficou com {kb:.1f} KB, acima do ideal '
            f'({limite_kb:.0f} KB) para o Zimbra. '
            f'Considere uma imagem mais simples.',
            'warning')
    else:
        flash(f'Logo otimizada: {kb:.1f} KB — pronta para o Zimbra.',
              'success')


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get('autenticado'):
            return redirect(url_for('admin.login', next=request.path))
        return view(*args, **kwargs)
    return wrapper


@admin_bp.before_request
def exigir_login():
    """Exige login em todas as rotas do blueprint, exceto a de login."""
    if request.endpoint == 'admin.login':
        return None
    if not session.get('autenticado'):
        return redirect(url_for('admin.login', next=request.path))
    return None


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('autenticado'):
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        hash_senha = os.environ.get('ADMIN_PASSWORD_HASH', '')
        if hash_senha and check_password_hash(hash_senha, form.senha.data):
            session.permanent = True
            session['autenticado'] = True
            destino = request.args.get('next')
            if not destino or not destino.startswith('/admin'):
                destino = url_for('admin.dashboard')
            return redirect(destino)
        flash('Senha incorreta.', 'error')
    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@login_required
def dashboard():
    marcas = storage.get_marcas()
    return render_template('admin/dashboard.html', marcas=marcas)


# ──────────────────────────── MARCAS ────────────────────────────

@admin_bp.route('/marca/nova', methods=['GET', 'POST'])
@login_required
def marca_nova():
    form = MarcaCriarForm()
    if form.validate_on_submit():
        nome = form.nome.data.strip()
        marcas = storage.get_marcas()
        if nome in marcas:
            flash('Já existe uma marca com esse nome.', 'error')
            return render_template('admin/marca_form.html', form=form,
                                   modo='nova')
        slug = gerar_slug(nome)
        try:
            resultado_logo = processar_upload(form.logo.data, slug)
        except LogoInvalida as e:
            flash(f'Erro na logo: {e}', 'error')
            return render_template('admin/marca_form.html', form=form,
                                   modo='nova')
        _flash_otimizacao(resultado_logo)

        nova = {
            'logo': resultado_logo['nome'],
            'categoria': form.categoria.data,
            'icone': form.icone.data,
            'concessionarias': {},
        }
        if form.logo_tem_barra.data:
            nova['logo_tem_barra'] = True

        dados = copy.deepcopy(marcas)
        dados[nome] = nova
        storage.salvar_marcas(dados)
        flash(f'Marca "{nome}" criada. Agora adicione as unidades.', 'success')
        return redirect(url_for('admin.marca_editar', marca=nome))
    return render_template('admin/marca_form.html', form=form, modo='nova')


@admin_bp.route('/marca/<marca>/editar', methods=['GET', 'POST'])
@login_required
def marca_editar(marca):
    marcas = storage.get_marcas()
    if marca not in marcas:
        abort(404)

    form = MarcaForm(data={
        'nome': marca,
        'categoria': marcas[marca].get('categoria', 'Concessionária'),
        'icone': marcas[marca].get('icone', 'car'),
        'logo_tem_barra': marcas[marca].get('logo_tem_barra', False),
    })

    if form.validate_on_submit():
        slug = gerar_slug(marca)  # chave/slug imutável: sempre derivado do nome original
        dados = copy.deepcopy(marcas)
        registro = dados[marca]
        registro['categoria'] = form.categoria.data
        registro['icone'] = form.icone.data
        if form.logo_tem_barra.data:
            registro['logo_tem_barra'] = True
        else:
            registro.pop('logo_tem_barra', None)

        resultado_logo = None
        if form.logo.data:
            try:
                resultado_logo = processar_upload(form.logo.data, slug)
            except LogoInvalida as e:
                flash(f'Erro na logo: {e}', 'error')
                return render_template('admin/marca_form.html', form=form,
                                       modo='editar', marca=marca,
                                       dados_marca=marcas[marca])
            registro['logo'] = resultado_logo['nome']
        storage.salvar_marcas(dados)
        flash('Marca atualizada.', 'success')
        if resultado_logo:
            _flash_otimizacao(resultado_logo)
        return redirect(url_for('admin.marca_editar', marca=marca))

    return render_template('admin/marca_form.html', form=form, modo='editar',
                           marca=marca, dados_marca=marcas[marca],
                           logo_info=_info_logo(marcas[marca].get('logo')))


@admin_bp.route('/marca/<marca>/excluir', methods=['POST'])
@login_required
def marca_excluir(marca):
    marcas = storage.get_marcas()
    if marca not in marcas:
        abort(404)
    dados = copy.deepcopy(marcas)
    del dados[marca]
    storage.salvar_marcas(dados)
    flash(f'Marca "{marca}" excluída.', 'success')
    return redirect(url_for('admin.dashboard'))


# ─────────────────────────── UNIDADES ───────────────────────────

@admin_bp.route('/marca/<marca>/unidade/nova', methods=['GET', 'POST'])
@login_required
def unidade_nova(marca):
    marcas = storage.get_marcas()
    if marca not in marcas:
        abort(404)
    form = UnidadeForm()
    if form.validate_on_submit():
        nome_unidade = form.nome.data.strip()
        if nome_unidade in marcas[marca]['concessionarias']:
            flash('Já existe uma unidade com esse nome nesta marca.', 'error')
            return render_template('admin/unidade_form.html', form=form,
                                   modo='nova', marca=marca)
        dados = copy.deepcopy(marcas)
        dados[marca]['concessionarias'][nome_unidade] = _unidade_de_form(form)
        storage.salvar_marcas(dados)
        flash('Unidade adicionada.', 'success')
        return redirect(url_for('admin.marca_editar', marca=marca))
    return render_template('admin/unidade_form.html', form=form, modo='nova',
                           marca=marca)


@admin_bp.route('/marca/<marca>/unidade/<unidade>/editar',
                methods=['GET', 'POST'])
@login_required
def unidade_editar(marca, unidade):
    marcas = storage.get_marcas()
    if marca not in marcas or unidade not in marcas[marca]['concessionarias']:
        abort(404)
    atual = marcas[marca]['concessionarias'][unidade]
    form = UnidadeForm(data={
        'nome': unidade,
        'endereco': atual.get('endereco', ''),
        'cidade': atual.get('cidade', ''),
        'cep': atual.get('cep', ''),
        'telefone': atual.get('telefone', ''),
        'site': atual.get('site', ''),
    })
    if form.validate_on_submit():
        novo_nome = form.nome.data.strip()
        dados = copy.deepcopy(marcas)
        unidades = dados[marca]['concessionarias']
        if novo_nome != unidade and novo_nome in unidades:
            flash('Já existe uma unidade com esse nome nesta marca.', 'error')
            return render_template('admin/unidade_form.html', form=form,
                                   modo='editar', marca=marca, unidade=unidade)
        # Remove a chave antiga e regrava preservando a ordem aproximada
        novas = {}
        for chave, valor in unidades.items():
            if chave == unidade:
                novas[novo_nome] = _unidade_de_form(form)
            else:
                novas[chave] = valor
        dados[marca]['concessionarias'] = novas
        storage.salvar_marcas(dados)
        flash('Unidade atualizada.', 'success')
        return redirect(url_for('admin.marca_editar', marca=marca))
    return render_template('admin/unidade_form.html', form=form, modo='editar',
                           marca=marca, unidade=unidade)


@admin_bp.route('/marca/<marca>/unidade/<unidade>/excluir', methods=['POST'])
@login_required
def unidade_excluir(marca, unidade):
    marcas = storage.get_marcas()
    if marca not in marcas or unidade not in marcas[marca]['concessionarias']:
        abort(404)
    dados = copy.deepcopy(marcas)
    del dados[marca]['concessionarias'][unidade]
    storage.salvar_marcas(dados)
    flash('Unidade excluída.', 'success')
    return redirect(url_for('admin.marca_editar', marca=marca))


def _unidade_de_form(form: UnidadeForm) -> dict:
    return {
        'endereco': form.endereco.data.strip(),
        'cidade': form.cidade.data.strip(),
        'cep': (form.cep.data or '').strip(),
        'telefone': (form.telefone.data or '').strip(),
        'site': (form.site.data or '').strip(),
    }
