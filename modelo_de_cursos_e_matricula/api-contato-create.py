import requests
import json

# Dados de autenticação
login_url = "http://odooserver:8069/web/session/authenticate"
create_partner_url = "http://odooserver:8069/api/res_partner/create"

# Token de autenticação para a API customizada
token = "token"

# Cabeçalhos para a requisição
headers = {
    "Content-Type": "application/json",
    "Token": token  # Incluindo o token no cabeçalho
}

# Executando a requisição de login
session = requests.Session()
response_login = session.post(login_url, headers=headers, json={
    "jsonrpc": "2.0",
    "params": {
        "login": "admin",
        "password": "admin",
        "db": "devpostgresql001"
    }
})

if response_login.status_code == 200:
    print("Login bem-sucedido!")

    # Dados do parceiro a ser criado
    partner_data = {
        "l10n_br_cnpj_cpf_formatted": "09842964094",
        "aluno": True,
        "professor": False,
        "name": "Aluno5",
        "email": "email@dominio.com"
    }

    # Executando a requisição POST para criar o parceiro
    response_partner = session.post(create_partner_url, headers=headers, json=partner_data)

    if response_partner.status_code == 200:
        print("Criação de parceiro bem-sucedida!", response_partner.json())
    else:
        print("Erro na criação do parceiro:", response_partner.text)
else:
    print("Falha no login:", response_login.text)
