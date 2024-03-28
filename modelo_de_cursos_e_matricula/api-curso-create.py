import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
create_curso_url = f"{odooserver_url}/api/cursos/create"  # URL atualizada para a API de cursos
token = "token"  # Assumindo que você já obteve o token de autenticação

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
    
    # Dados do curso a serem criados
    curso_data = {
        "name": "Nome do Curso",
        "cod_curso": "CRS123",  # Código do curso
        "cod_curriculo": "CURR001",  # Código do currículo relacionado
        "cod_variante": "VAR001",  #Código da variante do currículo
        "tempo_de_conclusao": "06M", # ou ('03M/90D', '03M/90D'), ('06M', '06M'), ('12M', '12M'), ('24M', '24M'), ('36M', '36M'), ('48M', '48M')
        "formato_nota": "normal" # ou porcentagem
    }

    # Cabeçalhos para a requisição POST, incluindo o token de autenticação
    headers = {
        "Content-Type": "application/json",
        "Token": token  # Token da sessão após login bem-sucedido
    }

    # Realizando a requisição POST para criar um novo curso
    response = session.post(create_curso_url, headers=headers, json=curso_data)

    # Avaliando a resposta
    if response.status_code == 200:
        print("Criação do curso bem-sucedida:", response.json())
    else:
        print(f"Erro na criação do curso: {response.status_code}", response.text)
else:
    print("Falha no login:", response_login.text)
