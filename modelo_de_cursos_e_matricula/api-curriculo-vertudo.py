import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
get_all_curriculo_url = f"{odooserver_url}/api/curriculo/all"

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
    # Certifique-se de que 'token_personalizado' é o token obtido da maneira correta após a autenticação
    token_personalizado = "token"  # Substitua pelo seu token real
    headers = {
        "Token": token_personalizado
    }

    # Realizando a requisição GET para buscar todos os currículos
    response_curriculo = session.get(get_all_curriculo_url, headers=headers)

    if response_curriculo.status_code == 200:
        try:
            curriculo_data = response_curriculo.json()
            print("Busca de currículos bem-sucedida:", curriculo_data)
        except ValueError:
            print("Resposta recebida não é JSON válido:", response_curriculo.text)
    else:
        print(f"Erro ao buscar currículos: {response_curriculo.status_code}", response_curriculo.text)
else:
    print("Falha no login:", response_login.text)
