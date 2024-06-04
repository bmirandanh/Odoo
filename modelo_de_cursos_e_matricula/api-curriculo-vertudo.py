import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
get_all_curriculo_url = f"{odooserver_url}/api/curriculo/all"
# Iniciar sessão
session = requests.Session()
token_personalizado = "token"  # Substitua pelo seu token real
headers = {
    "Token": token_personalizado
}
#Realizando a requisição GET para buscar todos os currículos
response_curriculo = session.get(get_all_curriculo_url, headers=headers)
curriculo_data = response_curriculo.json()
print("Busca de currículos bem-sucedida:", curriculo_data)
