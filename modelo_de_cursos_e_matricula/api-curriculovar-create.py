import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
create_curriculovariant_url = f"{odooserver_url}/api/curriculovariant/create"
token = "token"

# Dados de autenticação
login_data = {
    "jsonrpc": "2.0",
    "params": {
        "login": "admin",
        "password": "admin",
        "db": "devpostgresql001"
    }
}

# Iniciar sessão
session = requests.Session()

# Tentativa de login
response_login = session.post(login_url, headers={"Content-Type": "application/json"}, json=login_data)

# Verifica se o login foi bem-sucedido
if response_login.status_code == 200 and response_login.json().get("result"):
    print("Login bem-sucedido!")
    
    # Dados do variant do currículo a serem criados
    curriculovariant_data = {
        "name": "Nome do Variant do Currículo",
        "disciplina_codigos": ["res"],  # Lista de códigos das disciplinas
        "sequence": 0,
        "days_to_release": 0,
        "cod_curriculo": "CURR001",  # Código do currículo ao qual o variant pertence
        "cod_variante": "VAR001"
    }

    # Cabeçalhos para a requisição POST, incluindo o token de autenticação
    headers = {
        "Token": token  # Token da sessão após login bem-sucedido
    }

    # Realizando a requisição POST para criar um novo variant do currículo
    response = session.post(create_curriculovariant_url, headers=headers, json=curriculovariant_data)

    # Avaliando a resposta
    if response.status_code == 200:
        print("Criação do variant do currículo bem-sucedida:", response.json())
    else:
        print(f"Erro na criação do variant do currículo: {response.status_code}", response.text)
else:
    print("Falha no login:", response_login.text)
