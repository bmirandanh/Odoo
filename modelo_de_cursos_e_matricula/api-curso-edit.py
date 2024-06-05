import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
cod_curso = "34tt3t4"  # Substitua pelo código do tipo de cancelamento que deseja atualizar
attribute = None  # Atributo específico a ser atualizado, se aplicável
# Substitua 'seu_token_aqui' pelo valor real do token
token_personalizado = "token"
# Montando a URL da API para atualização do tipo de cancelamento
update_cursos_url = f"{odooserver_url}/api/cursos/update/{cod_curso}" + (f"/{attribute}" if attribute else "")
# Preparando os dados para atualização
update_data = {
    "nome": "Nome Atualizado do curso",  # Ajuste conforme necessário
    # Adicione outros campos de acordo com os requisitos
}
# Iniciar sessão
session = requests.Session()
# Realizando a requisição de login
headers = {
    "Token": token_personalizado,  # Enviando o token personalizado para autenticação
}
# Realizando a requisição PUT para atualizar o tipo de cancelamento
response_update = session.put(update_cursos_url, headers=headers, data=json.dumps(update_data))
print("Atualização do tipo de cancelamento bem-sucedida:", response_update.json())

