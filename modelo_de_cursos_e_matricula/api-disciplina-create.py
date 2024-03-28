import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
create_disciplina_url = f"{odooserver_url}/api/disciplina/create"
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
    
    # Dados da disciplina a serem criados
    disciplina_data = {
        "name": "Nome da Disciplina",
        "media": 7.0,
        "cod_disciplina": "DISC001"
    }

    # Cabeçalhos para a requisição POST, incluindo o token de autenticação
    headers = {
        "Content-Type": "application/json",
        "Token": token  # Token da sessão após login bem-sucedido
    }

    # Realizando a requisição POST para criar uma nova disciplina
    response = session.post(create_disciplina_url, headers=headers, json=disciplina_data)

    # Avaliando a resposta
    if response.status_code == 200:
        print("Criação da disciplina bem-sucedida:", response.json())
    else:
        print(f"Erro na criação da disciplina: {response.status_code}", response.text)
else:
    print("Falha no login:", response_login.text)
