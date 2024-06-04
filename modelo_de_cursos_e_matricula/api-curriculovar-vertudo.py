import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
get_all_curriculovariant_url = f"{odooserver_url}/api/curriculovariant/all"  # URL atualizada para a API de variantes
# Dados de autenticação
login_data = {
    "jsonrpc": "2.0",
    "params": {
        "login": "admin",
        "password": "admin",
        "db": "devpostgresql001"
    }
}
# Iniciar sessão
session = requests.Session()
# Substitua 'token' pelo token real obtido após autenticação
token_personalizado = "token"  # Substitua pelo seu token real
headers = {
    "Token": token_personalizado
}
# Realizando a requisição GET para buscar todas as variantes de currículo
response_curriculovariant = session.get(get_all_curriculovariant_url, headers=headers)
curriculovariant_data = response_curriculovariant.json()
print("Busca de variantes de currículo bem-sucedida:", curriculovariant_data)

