import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"

# Substitua pelo número de matrícula real que deseja buscar
numero_matricula = "MATR123456"  # Substitua pelo valor correto
get_matricula_url = f"{odooserver_url}/api/matricula/{numero_matricula}"

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
response_login = session.post(login_url, json=login_data)

if response_login.status_code == 200 and response_login.json().get("result"):
    print("Login bem-sucedido!")

    # Assumindo que o token personalizado é um Bearer token esperado no cabeçalho Authorization
    token_personalizado = "token"  # Substitua pelo seu token real
    headers = {

        "Token": token_personalizado  # Inclua o token personalizado aqui
    }

    # Realizando a requisição GET para buscar a matrícula específica
    response_matricula = session.get(get_matricula_url, headers=headers)

    if response_matricula.status_code == 200:
        try:
            matricula_data = response_matricula.json()
            print("Busca da matrícula bem-sucedida:", matricula_data)
        except ValueError:
            print("Resposta recebida não é JSON válido:", response_matricula.text)
    else:
        print(f"Erro ao buscar a matrícula: {response_matricula.status_code}", response_matricula.text)
else:
    print("Falha no login:", response_login.text)
