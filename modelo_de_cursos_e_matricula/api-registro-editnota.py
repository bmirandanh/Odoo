import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"

# Substitua com os valores corretos
numero_matricula = "qwqw4013159"
cod_disciplina = "tess"
nova_nota = "7"  # nota como string, ajuste conforme o esperado pela API, ou seja seu ID no Odoo

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

# Realizando a requisição de login
response_login = session.post(login_url, json=login_data)
if response_login.status_code == 200 and response_login.json().get("result"):
    print("Login bem-sucedido!")
    
    # Substitua 'seu_token_aqui' pelo valor real do token
    token_personalizado = "token"
    
    # Montando a URL da API para atualização da nota do registro de disciplina
    edit_nota_url = f"{odooserver_url}/api/registrodisciplina/editnota/{numero_matricula}/{cod_disciplina}/{nova_nota}"

    
    # Preparando os dados para atualização
    headers = {
        "Token": token_personalizado,  # Enviando o token personalizado para autenticação
    }

    # Preparando os dados para atualização
    update_data = {
        "numero_matricula": numero_matricula,
        "cod_disciplina": cod_disciplina,
        "nova_nota": nova_nota,
    }

    # Realizando a requisição PUT para atualizar a nota
    response_update = session.put(edit_nota_url, headers=headers, json=update_data)
 
    if response_update.status_code == 200:
        print("Atualização da nota bem-sucedida:", response_update.json())
    else:
        print(f"Erro ao atualizar a nota: {response_update.status_code}", response_update.text)
else:
    print("Falha no login:", response_login.text)
