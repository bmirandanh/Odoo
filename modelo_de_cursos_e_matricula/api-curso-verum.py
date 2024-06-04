import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua pelo código real do tipo de cancelamento que deseja buscar
cod_curriculo = "1d12"  # Substitua pelo valor correto
get_curso_url = f"{odooserver_url}/api/cursos/{cod_curriculo}"
# Iniciar sessão
session = requests.Session()
# Assumindo que o token personalizado é um Bearer token esperado no cabeçalho Authorization
token_personalizado = "token"  # Substitua pelo seu token real
headers = {
    "Token": token_personalizado  # Inclua o token personalizado aqui
}
# Realizando a requisição GET para buscar o tipo de cancelamento específico
response_curso = session.get(get_curso_url, headers=headers)
tipo_curso_data = response_curso.json()
print("Busca do curso bem-sucedida:", tipo_curso_data)

