import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
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

# Tentativa de login
response_login = session.post(login_url, json=login_data)

if response_login.status_code == 200 and response_login.json().get("result"):
    print("Login bem-sucedido!")

    # Substitua 'token' pelo token real obtido após autenticação
    token_personalizado = "token"  # Substitua pelo seu token real
    headers = {
        "Token": token_personalizado
    }

    # Realizando a requisição GET para buscar todas as variantes de currículo
    response_curriculovariant = session.get(get_all_curriculovariant_url, headers=headers)

    if response_curriculovariant.status_code == 200:
        try:
            curriculovariant_data = response_curriculovariant.json()
            print("Busca de variantes de currículo bem-sucedida:", curriculovariant_data)
        except ValueError:
            print("Resposta recebida não é JSON válido:", response_curriculovariant.text)
    else:
        print(f"Erro ao buscar variantes de currículo: {response_curriculovariant.status_code}", response_curriculovariant.text)
else:
    print("Falha no login:", response_login.text)
