# app.py
from flask import Flask, render_template, abort, request
import json
import base64
import os
from datetime import datetime  # <--- ADICIONADO

app = Flask(__name__)

# Este processador de contexto injeta o ano atual em todos os templates


@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}


# Nosso "banco de dados" completo com todas as informações coletadas.
# SUBSTITUA SEU DICIONÁRIO 'MARCAS' POR ESTE BLOCO COMPLETO

MARCAS = {
    "Administração": {
        "logo": "grupo_navesa.png",
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
        "logo": "grupo_navesa.png",
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
    "Ciaasa": {
        "logo": "ciaasa.png",
        "concessionarias": {
            # --- CORREÇÃO APLICADA AQUI ---
            "Ciaasa - Castelo Branco": {
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
    "Ti": {
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
    },
    "Polaris": {
        "logo": "polares.png",
        "concessionarias": {
            "Polares": {
                "endereco": "Av. Castelo Branco, 3081 - St. Campinas",
                "cidade": "Goiânia - GO", "cep": "74513-101",
                "telefone": "(62) 3018-1212",
                "site": "www.navesa.com.br"
            }
        }
    }
}


@app.route('/')
def index():
    """ Rota da página inicial que exibe a lista de Marcas/Departamentos. """
    lista_marcas = MARCAS.keys()
    return render_template('index.html', marcas=lista_marcas)


@app.route('/gerar/<marca>')
def formulario(marca):
    """ Exibe o formulário de preenchimento para uma marca específica. """
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
    # 1. Coleta todos os dados enviados pelo formulário
    dados_formulario = request.form

    # 2. Lógica para encontrar o nome do arquivo do logo
    logo_arquivo = None
    concessionaria_selecionada = dados_formulario.get(
        'concessionaria_selecionada')
    for marca, dados_marca in MARCAS.items():
        if concessionaria_selecionada in dados_marca['concessionarias']:
            logo_arquivo = dados_marca['logo']
            break

    # 3. Lógica para codificar a imagem em Base64
    logo_base64 = None
    if logo_arquivo:
        try:
            # Constrói o caminho completo para o arquivo de imagem
            caminho_logo = os.path.join(
                app.static_folder, 'images', logo_arquivo)
            with open(caminho_logo, 'rb') as f:
                # Lê o arquivo e codifica em Base64
                logo_base64 = base64.b64encode(f.read()).decode('utf-8')
        except FileNotFoundError:
            # Se o logo não for encontrado, não quebra a aplicação
            print(f"AVISO: Arquivo de logo não encontrado em: {caminho_logo}")
            logo_base64 = None

    # 4. Renderiza o template, passando a imagem codificada
    return render_template('resultado.html', dados=dados_formulario, logo_base64=logo_base64)


if __name__ == '__main__':
    app.run(debug=True)
