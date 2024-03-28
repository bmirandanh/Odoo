import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
token_personalizado = "token"  # Substitua pelo seu token real

# Substitua pelo código real da variante do currículo que deseja atualizar
cod_variante = "VAR001"
update_variant_url = f"{odooserver_url}/api/curriculovariant/update/{cod_variante}"

# Dados de autenticação
login_data = {
    "jsonrpc": "2.0",
    "params": {
        "login": "admin",
        "password": "admin",
        "db": "devpostgresql001"
    }
}

# Preparando os dados para atualização
update_data = {
    "name": "Nova Variante Atualizada",  # Exemplo de atualização
    # Adicione outros campos conforme necessário
}

# Iniciar sessão e realizar login
session = requests.Session()
response_login = session.post(login_url, json=login_data)

if response_login.status_code == 200 and response_login.json().get("result"):
    print("Login bem-sucedido!")

    # Headers para incluir o token personalizado
    headers = {
        "Content-Type": "application/json",
        "Token": token_personalizado
    }

    # Realizando a requisição PUT para atualizar a variante do currículo
    response_update = session.put(update_variant_url, headers=headers, data=json.dumps(update_data))

    if response_update.status_code == 200:
        print("Atualização da variante do currículo bem-sucedida:", response_update.json())
    else:
        print("Erro ao atualizar a variante do currículo:", response_update.status_code, response_update.text)
else:
    print("Falha no login:", response_login.text)
