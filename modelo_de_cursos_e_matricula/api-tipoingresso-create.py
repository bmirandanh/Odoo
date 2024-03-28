import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
create_tipoingresso_url = f"{odooserver_url}/api/tipoingresso/create"

# Dados para o novo tipo de ingresso
tipo_ingresso_data = {
    "nome": "VIP",
    "descricao": "Acesso VIP com benefícios exclusivos",
    "color": 10,  # Este é um exemplo, ajuste conforme necessário
    "cod_ingresso": "VIP2024"
}

# Dados de autenticação
login_data = {
    "jsonrpc": "2.0",
    "params": {
        "login": "admin",
        "password": "admin",
        "db": "devpostgresql001"
    }
}

# Token personalizado para autenticação nas requisições à API
token_personalizado = "token"  # Substitua pelo seu token real

# Cabeçalhos para incluir o token personalizado
headers = {
    "Content-Type": "application/json",
    "Token": token_personalizado
}

# Iniciar sessão
session = requests.Session()

# Realizando a requisição de login
response_login = session.post(login_url, json=login_data)

if response_login.status_code == 200 and response_login.json().get("result"):
    print("Login bem-sucedido!")

    # Realizando a requisição POST para criar o tipo de ingresso
    response_create = session.post(create_tipoingresso_url, headers=headers, json=tipo_ingresso_data)

    if response_create.status_code == 200:
        try:
            tipo_ingresso_created = response_create.json()
            print("Criação do tipo de ingresso bem-sucedida:", tipo_ingresso_created)
        except ValueError:
            print("Resposta recebida não é JSON válido:", response_create.text)
    else:
        print(f"Erro ao criar o tipo de ingresso: {response_create.status_code}", response_create.text)
else:
    print("Falha no login:", response_login.text)
