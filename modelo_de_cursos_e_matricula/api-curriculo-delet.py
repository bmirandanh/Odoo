import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
create_curriculo_url = f"{odooserver_url}/api/curriculo/create"
token = "token"
# Iniciar sessão
session = requests.Session()

# Dados do currículo a serem criados
curriculo_data = {
    "name": "Nome do Currículo",
    "cod_professor": "FG202447849",  # Substitua pelo código real do professor
    "cod_curriculo": "CURR001"
}
# Cabeçalhos para a requisição POST, incluindo o token de autenticação
headers = {
    "Content-Type": "application/json",
    "Token": token  # Token da sessão após login bem-sucedido
}
# Realizando a requisição POST para criar um novo currículo
response = session.post(create_curriculo_url, headers=headers, json=curriculo_data)
# Avaliando a resposta
if response.status_code == 200:
    print("Criação do currículo bem-sucedida:", response.json())
else:
    print(f"Erro na criação do currículo: {response.status_code}", response.text)