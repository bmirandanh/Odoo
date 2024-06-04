import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua 'seu_token_aqui' pelo valor real do token
token_personalizado = "token"
# Substitua pelo código real do tipo de cancelamento que deseja deletar
cod_curso = "34tt3t4"  # Ajuste este valor conforme necessário
delete_cursos_url = f"{odooserver_url}/api/cursos/delete/{cod_curso}"
# Iniciar sessão
session = requests.Session()
headers = {
    "Token": token_personalizado
}
# Realizando a requisição DELETE para deletar o tipo de cancelamento específico
response_delete = session.delete(delete_cursos_url, headers=headers)
result = response_delete.json()
print("Deleção do tipo de cancelamento bem-sucedida:", result)

