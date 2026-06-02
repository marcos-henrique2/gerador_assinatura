# Gerador de Assinaturas — Grupo Navesa

Aplicação Flask para gerar assinaturas de e-mail padronizadas, com um
**painel administrativo** para gerenciar marcas e unidades.

## Requisitos

- Windows
- Python 3.12+

## 1. Instalar

Abra o terminal na pasta do projeto e rode uma vez:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configurar a senha do admin

Dê um duplo clique em **`configurar_admin.bat`** (ou rode no terminal).
Ele vai:

- pedir a senha do painel (não aparece na tela enquanto digita);
- gerar automaticamente a `SECRET_KEY` e o hash da senha;
- criar/atualizar o arquivo `.env`.

> Para trocar a senha depois, basta rodar o `configurar_admin.bat` de novo.

## 3. Iniciar

Dê um duplo clique em **`iniciar_gerador.bat`**. O servidor sobe com
**waitress** (modo produção, sem debug) e fica disponível em:

- Site público: `http://localhost:5000`
- Painel admin: `http://localhost:5000/admin`

Para acessar de outro computador na rede, use o IP desta máquina
(ex.: `http://192.168.0.10:5000`). Deixe a janela aberta enquanto
o sistema estiver em uso.

## Dados e backups

- **Fonte de verdade:** `data/marcas.json` (no servidor). Esse arquivo
  **não é versionado** — ele é editado pelo painel admin.
- A cada alteração no painel, um **backup automático** é gravado em
  `data/backups/` (mantém os últimos 20).
- `data/marcas.example.json` é uma cópia inicial versionada, usada como
  semente caso seja preciso recriar o `marcas.json`.

## Estrutura

| Arquivo | Função |
|---|---|
| `app.py` | App Flask, rotas públicas e configuração |
| `auth.py` | Blueprint `/admin`: login e CRUD |
| `forms.py` | Formulários e validação (WTForms) |
| `storage.py` | Leitura/gravação atômica de `marcas.json` + backups |
| `logos.py` | Validação e otimização de logos enviadas (PNG) |
| `utils.py` | Slug e normalização segura de sites |
