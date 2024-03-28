import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"

# Substitua pelo código real do tipo de ingresso que deseja buscar
cod_ingresso = "VIP4951"
get_tipoingresso_url = f"{odooserver_url}/api/tipoingresso/{cod_ingresso}"

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

    # Assumindo que o token personalizado é um Bearer token esperado no cabeçalho Authorization
    token_personalizado = "token"
    headers = {
        "Token": token_personalizado  # Inclua o token personalizado aqui
    }

    # Realizando a requisição GET para buscar o tipo de ingresso específico
    response_tipoingresso = session.get(get_tipoingresso_url, headers=headers)

    if response_tipoingresso.status_code == 200:
        try:
            tipo_ingresso_data = response_tipoingresso.json()
            print("Busca do tipo de ingresso bem-sucedida:", tipo_ingresso_data)
        except ValueError:
            print("Resposta recebida não é JSON válido:", response_tipoingresso.text)
    else:
        print(f"Erro ao buscar o tipo de ingresso: {response_tipoingresso.status_code}", response_tipoingresso.text)
else:
    print("Falha no login:", response_login.text)