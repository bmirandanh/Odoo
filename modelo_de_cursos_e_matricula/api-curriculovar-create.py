import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
create_curriculovariant_url = f"{odooserver_url}/api/curriculovariant/create"
token = "token"
# Iniciar sessão
session = requests.Session()
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
print("Criação do variant do currículo bem-sucedida:", response.json())