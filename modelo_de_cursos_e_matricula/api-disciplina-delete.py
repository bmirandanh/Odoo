import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua 'seu_token_aqui' pelo valor real do token
token_personalizado = "token"
# Substitua pelo código real da disciplina que deseja deletar
cod_disciplina = "tes55"
delete_disciplina_url = f"{odooserver_url}/api/disciplina/delete/{cod_disciplina}"
# Iniciar sessão
session = requests.Session()
# Headers para incluir o token personalizado
headers = {
    "Token": token_personalizado
}
# Realizando a requisição DELETE para deletar a disciplina específica
response_delete = session.delete(delete_disciplina_url, headers=headers)
result = response_delete.json()
print("Deleção da disciplina bem-sucedida:", result)
