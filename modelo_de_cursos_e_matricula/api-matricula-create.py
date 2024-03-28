import requests
import json
from datetime import datetime

# Função auxiliar para converter datetime para string no formato ISO
def datetime_to_iso(dt):
    return dt.isoformat() if isinstance(dt, datetime) else dt

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
create_matricula_url = f"{odooserver_url}/api/matricula/create"
token = "token"  # Substitua pelo seu token real após o login

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
    
    # Dados da matrícula a serem criados
    matricula_data = {
        "cod_ingresso": "WDQD5041",  # Código do tipo de ingresso
        "cod_curriculo": "www",  # Código do currículo relacionado
        "cod_variante": "21e21",  # Código da variante do currículo (se aplicável)
        "nome_do_aluno": 26,
        "curso": 1,
        "inscricao_ava": datetime_to_iso(datetime.strptime("02/12/2024", "%m/%d/%Y")),
        "email": "emaildoaluno@example.com",
        "telefone": "1234567890",
        "numero_matricula": "MATR123456",  # Número de matrícula do aluno
    }

    # Cabeçalhos para a requisição POST, incluindo o token de autenticação
    headers = {
        "Token": token  # Token da sessão após login bem-sucedido
    }

    # Realizando a requisição POST para criar uma nova matrícula
    response = session.post(create_matricula_url, headers=headers, json=matricula_data)

    # Avaliando a resposta
    if response.status_code == 200:
        try:
            result = response.json()
            print("Criação da matrícula bem-sucedida:", result)
        except ValueError as e:
            print("Resposta recebida não é JSON válido:", response.text)
            print("Erro detalhado:", e)
    else:
        print(f"Erro na criação da matrícula: {response.status_code}", response.text)
else:
    print("Falha no login:", response_login.text)
