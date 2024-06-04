import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
create_curso_url = f"{odooserver_url}/api/cursos/create"  # URL atualizada para a API de cursos
token = "token"  # Assumindo que você já obteve o token de autenticação
# Iniciar sessão
session = requests.Session()
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
print("Criação do curso bem-sucedida:", response.json())
