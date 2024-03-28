import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"

cod_curso = "34tt3t4"  # Substitua pelo código do tipo de cancelamento que deseja atualizar
attribute = None  # Atributo específico a ser atualizado, se aplicável

# Dados de autenticação
login_data = {
    "jsonrpc": "2.0",
    "params": {
        "login": "admin",
        "password": "admin",
        "db": "devpostgresql001"
    }
}

# Substitua 'seu_token_aqui' pelo valor real do token
token_personalizado = "token"

# Montando a URL da API para atualização do tipo de cancelamento
update_cursos_url = f"{odooserver_url}/api/cursos/update/{cod_curso}" + (f"/{attribute}" if attribute else "")

# Preparando os dados para atualização
update_data = {
    "nome": "Nome Atualizado do curso",  # Ajuste conforme necessário
    # Adicione outros campos de acordo com os requisitos
}

# Iniciar sessão
session = requests.Session()

# Realizando a requisição de login
response_login = session.post(login_url, json=login_data)

if response_login.status_code == 200 and response_login.json().get("result"):
    print("Login bem-sucedido!")

    headers = {
        "Token": token_personalizado,  # Enviando o token personalizado para autenticação
    }

    # Realizando a requisição PUT para atualizar o tipo de cancelamento
    response_update = session.put(update_cursos_url, headers=headers, data=json.dumps(update_data))  # Usando data= ao invés de json=

    if response_update.status_code == 200:
        print("Atualização do tipo de cancelamento bem-sucedida:", response_update.json())
    else:
        print(f"Erro ao atualizar o tipo de cancelamento: {response_update.status_code}", response_update.text)
else:
    print("Falha no login:", response_login.text)
