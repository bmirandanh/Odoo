import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
get_all_disciplinas_url = f"{odooserver_url}/api/disciplina/all"

# Iniciar sessão
session = requests.Session()
token_personalizado = "token"
headers = {
    "Token": token_personalizado
}
response_disciplinas = session.get(get_all_disciplinas_url, headers=headers)

disciplinas_data = response_disciplinas.json()
print("Busca de disciplinas bem-sucedida:", disciplinas_data)

