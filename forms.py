# forms.py
"""Formulários WTForms com validação server-side do painel admin."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import BooleanField, SelectField, StringField, PasswordField
from wtforms.validators import (DataRequired, Length, Optional, Regexp,
                                ValidationError)

from utils import site_eh_seguro

CATEGORIAS = [
    ('Concessionária', 'Concessionária'),
    ('Gestão', 'Gestão'),
    ('Serviços', 'Serviços'),
]

# Ícones Font Awesome usados no projeto
ICONES = [
    ('car', 'Carro (car)'),
    ('building', 'Prédio (building)'),
    ('clipboard-check', 'Auditoria (clipboard-check)'),
    ('shield-alt', 'Escudo (shield-alt)'),
    ('file-alt', 'Documento (file-alt)'),
    ('laptop-code', 'TI (laptop-code)'),
]


class LoginForm(FlaskForm):
    senha = PasswordField('Senha', validators=[DataRequired()])


def _validar_site(form, field):
    if field.data and not site_eh_seguro(field.data):
        raise ValidationError('Site inválido ou não permitido.')


class MarcaForm(FlaskForm):
    nome = StringField('Nome da marca', validators=[
        DataRequired(message='Informe o nome da marca.'),
        Length(max=60)])
    categoria = SelectField('Categoria', choices=CATEGORIAS,
                            validators=[DataRequired()])
    icone = SelectField('Ícone', choices=ICONES, default='car',
                        validators=[DataRequired()])
    logo_tem_barra = BooleanField('A logo já possui barra/separador próprio')
    logo = FileField('Logo (PNG)', validators=[
        FileAllowed(['png'], 'Apenas arquivos PNG são aceitos.')])


class MarcaCriarForm(MarcaForm):
    # Na criação a logo é obrigatória
    logo = FileField('Logo (PNG)', validators=[
        FileRequired(message='Envie a logo da marca (PNG).'),
        FileAllowed(['png'], 'Apenas arquivos PNG são aceitos.')])


class UnidadeForm(FlaskForm):
    nome = StringField('Nome da unidade', validators=[
        DataRequired(message='Informe o nome da unidade.'),
        Length(max=80)])
    endereco = StringField('Endereço', validators=[
        DataRequired(message='Informe o endereço.')])
    cidade = StringField('Cidade', validators=[
        DataRequired(message='Informe a cidade.')])
    cep = StringField('CEP', validators=[
        Optional(),
        Regexp(r'^\d{5}-?\d{3}$', message='CEP no formato 99999-999.')])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=30)])
    site = StringField('Site', validators=[Optional(), _validar_site])
