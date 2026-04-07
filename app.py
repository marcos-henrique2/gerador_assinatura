# app.py
from flask import Flask, render_template, abort, request
import json
from datetime import datetime

app = Flask(__name__)


@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}


MARCAS = {
    "Administração": {
        "logo": "admin.png",
        "concessionarias": {
            "GRUPO NAVESA": {
                "endereco": "Av. Pires Fernandes, 656 - St. Aeroporto",
                "cidade": "Goiânia - GO", "cep": "74070-030",
                "telefone": "(62) 3018-1313",
                "site": "www.navesa.com.br"
            }
        }
    },
    "Auditoria": {
        "logo": "admin.png",
        "concessionarias": {
            "GRUPO NAVESA": {
                "endereco": "Av. Pires Fernandes, 656 - St. Aeroporto",
                "cidade": "Goiânia - GO", "cep": "74070-030",
                "telefone": "(62) 3018-1313",
                "site": "www.navesa.com.br"
            }
        }
    },
    "GWM": {
        "logo": "gwm.png",
        "concessionarias": {
            "Navesa GWM - Goiânia": {
                "endereco": "R. T-55, 317 - St. Bueno",
                "cidade": "Goiânia - GO", "cep": "74215-170",
                "telefone": "(62) 3413-0600",
                "site": "www.navesa.com.br"
            },
            "Navesa GWM - Anápolis": {
                "endereco": "Av. Brasil Sul, 2750 - CHÁCARAS JONAS DUARTE",
                "cidade": "Anápolis - GO", "cep": "75120-792",
                "telefone": "(62) 3772-1200",
                "site": "www.navesa.com.br"
            },
            "Navesa GWM - Rio Verde": {
                "endereco": "R. Marcha p/ o Oeste, 405",
                "cidade": "Rio Verde - GO", "cep": "75905-700",
                "telefone": "(64) 3051-5284",
                "site": "www.navesa.com.br"
            }
        }
    },
    "Geely": {
        "logo": "geely.jpeg",
        "concessionarias": {
            "Navesa Geely": {
                "endereco": "Av. Mutirão, 3015 - St. Bueno",
                "cidade": "Goiânia - GO", "cep": "74150-340",
                "telefone": "(62) 3121-4730",
                "site": "www.navesa.com.br"
            }
        }
    },
    "GAC": {
        "logo": "gac.jpeg",
        "concessionarias": {
            "Navesa GAC": {
                "endereco": "Av. Mutirão, 3300 - St. Bueno",
                "cidade": "Goiânia - GO", "cep": "74215-240",
                "telefone": "(62) 3121-4730",
                "site": "www.navesa.com.br"
            }
        }
    },
    "Ciaasa": {
        "logo": "ciaasa.png",
        "concessionarias": {
            "Ford - Goiânia": {
                "endereco": "Av. Castelo Branco, 87 - St. Bueno",
                "cidade": "Goiânia - GO", "cep": "74210-185",
                "telefone": "(62) 3018-1919",
                "site": "www.navesa.com.br"
            }
        }
    },
    "Corretora": {
        "logo": "corretora.png",
        "concessionarias": {
            "GRUPO NAVESA": {
                "endereco": "Av. Pires Fernandes, 656 - St. Aeroporto",
                "cidade": "Goiânia - GO", "cep": "74070-030",
                "telefone": "(62) 3018-1313",
                "site": "www.navesa.com.br"
            }
        }
    },
    "Despachante": {
        "logo": "despachante.png",
        "concessionarias": {
            "Despachante - Goiânia": {
                "endereco": "Av. Pires Fernandes, 656 - St. Aeroporto",
                "cidade": "Goiânia - GO", "cep": "74070-030",
                "telefone": "(62) 3018-1313",
                "site": "www.navesa.com.br"
            },
            "Despachante - Anápolis": {
                "endereco": "Av. Brasil Sul, 4088 - St. Sul Jamil Miguel",
                "cidade": "Anápolis - GO", "cep": "75124-820",
                "telefone": "(62) 3310-3700",
                "site": "www.navesa.com.br"
            }
        }
    },
    "Ford": {
        "logo": "ford.png",
        "concessionarias": {
            "Ford - Goiânia": {
                "endereco": "Av. Pires Fernandes, 656 - St. Aeroporto",
                "cidade": "Goiânia - GO", "cep": "74070-030",
                "telefone": "(62) 3018-1313",
                "site": "www.navesa.com.br"
            },
            "Ford - Anápolis": {
                "endereco": "Av. Brasil Sul, 4088 - St. Sul Jamil Miguel",
                "cidade": "Anápolis - GO", "cep": "75124-820",
                "telefone": "(62) 3310-3700",
                "site": "www.navesa.com.br"
            },
            "Ford - Campo Grande": {
                "endereco": "Av. Eduardo Elias Zahran, 240 - Jardim Paulista",
                "cidade": "Campo Grande - MS", "cep": "79050-000",
                "telefone": "(67) 3047-1250",
                "site": "www.navesa.com.br"
            },
            "Ford - Aparecida": {
                "endereco": "Av. Rio Verde, S/N - Vila Rosa",
                "cidade": "Aparecida de Goiânia - GO", "cep": "79050-000",
                "telefone": "(67) 3047-1250",
                "site": "www.navesa.com.br"
            }
        }
    },
    "TI": {
        "logo": "dept-ti.png",
        "concessionarias": {
            "GRUPO NAVESA": {
                "endereco": "Av. Pires Fernandes, 656 - St. Aeroporto",
                "cidade": "Goiânia - GO", "cep": "74070-030",
                "telefone": "(62) 3018-1313",
                "site": "www.navesa.com.br"
            }
        }
    },
    "Peugeot": {
        "logo": "peugeot.png",
        "concessionarias": {
            "Peugeot - Aparecida": {
                "endereco": "Av. Rio Verde, S/N - Vila Rosa",
                "cidade": "Aparecida de Goiânia - GO", "cep": "74070-030",
                "telefone": "(62) 3270-6000",
                "site": "www.navesa.com.br"
            }
        }
    },
    "Renault": {
        "logo": "renault.png",
        "concessionarias": {
            "Renault - T63": {
                "endereco": "Av. T-63, 1707 - quadra 587 - lote 24 - Nova Suíça",
                "cidade": "Goiânia - GO", "cep": "74280-235",
                "telefone": "(62) 3235-8888",
                "site": "www.navesa.com.br"
            }
        }
    }
}


@app.route('/')
def index():
    lista_marcas = MARCAS.keys()
    return render_template('index.html', marcas=lista_marcas)


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
                           dados_json=dados_json_para_frontend)


@app.route('/resultado', methods=['POST'])
def resultado():
    dados_formulario = request.form
    marca_nome = dados_formulario.get('marca_selecionada')

    logo_arquivo = None
    if marca_nome in MARCAS:
        logo_arquivo = MARCAS[marca_nome]['logo']

    logo_url = None
    if logo_arquivo:
        url_base = "https://navesa.com.br/uploads/imagens/"
        logo_url = f"{url_base}{logo_arquivo}"

    return render_template('resultado.html', dados=dados_formulario, logo_url=logo_url)


if __name__ == '__main__':
    # host='0.0.0.0' permite que a aplicação seja acessada por outros PCs na rede
    app.run(host='0.0.0.0', port=5000, debug=True)