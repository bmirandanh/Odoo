import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
create_disciplina_url = f"{odooserver_url}/api/disciplina/create"
token = "token"
# Iniciar sessão
session = requests.Session()
# Dados da disciplina a serem criados
disciplina_data = {
    "name": "Nome da Disciplina",
    "media": 7.0,
    "professor": 7,
    "duracao_horas": 77,
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
print("Criação da disciplina bem-sucedida:", response.json())
