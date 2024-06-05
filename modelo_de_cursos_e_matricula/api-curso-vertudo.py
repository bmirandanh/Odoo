import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
get_all_curso_url = f"{odooserver_url}/api/cursos/all"
# Iniciar sessão
session = requests.Session()
# Certifique-se de que 'token_personalizado' é o token
token_personalizado = "token"  # Substitua pelo seu token real
headers = {
    "token": token_personalizado,
}
# Realizando a requisição GET para buscar todos os cursos
response_curso = session.get(get_all_curso_url, headers=headers)
curso_data = response_curso.json()
print("Busca de cursos bem-sucedida:", curso_data)

