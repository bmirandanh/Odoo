import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua 'token' pelo valor real do token
token_personalizado = "token"
# Substitua pelo código real da disciplina que deseja buscar
cod_disciplina = "regre"
get_disciplina_url = f"{odooserver_url}/api/disciplina/{cod_disciplina}"
# Iniciar sessão
session = requests.Session()
# Headers para incluir o token personalizado
headers = {
    "Token": token_personalizado
}
# Realizando a requisição GET para buscar a disciplina específica
response_disciplina = session.get(get_disciplina_url, headers=headers)
disciplina_data = response_disciplina.json()
print("Busca da disciplina bem-sucedida:", disciplina_data)
