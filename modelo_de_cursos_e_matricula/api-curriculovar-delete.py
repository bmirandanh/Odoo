import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua 'seu_token_aqui' pelo valor real do token
token_personalizado = "token"
# Substitua pelo código real da variante do currículo que deseja deletar
cod_variante = "VAR001"
delete_curriculovariant_url = f"{odooserver_url}/api/curriculovariant/delete/{cod_variante}"
# Iniciar sessão
session = requests.Session()
# Headers para incluir o token personalizado
headers = {
    "Token": token_personalizado  # Substitua pelo seu token real de autenticação
}
# Realizando a requisição DELETE para deletar a variante de currículo específica
response_delete = session.delete(delete_curriculovariant_url, headers=headers)
result = response_delete.json()
print("Deleção da variante de currículo bem-sucedida:", result)

