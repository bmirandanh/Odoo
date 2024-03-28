import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"

# Substitua pelo código real do currículo que deseja buscar
cod_curriculo = "CURR001"  # Substitua pelo valor correto
get_curriculo_url = f"{odooserver_url}/api/curriculo/{cod_curriculo}"

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
    token_personalizado = "token"  # Substitua pelo seu token real
    headers = {
        "Token": token_personalizado  # Inclua o token personalizado aqui
    }

    # Realizando a requisição GET para buscar o currículo específico
    response_curriculo = session.get(get_curriculo_url, headers=headers)

    if response_curriculo.status_code == 200:
        try:
            curriculo_data = response_curriculo.json()
            print("Busca do currículo bem-sucedida:", curriculo_data)
        except ValueError:
            print("Resposta recebida não é JSON válido:", response_curriculo.text)
    else:
        print(f"Erro ao buscar o currículo: {response_curriculo.status_code}", response_curriculo.text)
else:
    print("Falha no login:", response_login.text)
