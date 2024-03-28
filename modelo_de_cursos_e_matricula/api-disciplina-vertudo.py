import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
get_all_disciplinas_url = f"{odooserver_url}/api/disciplina/all"

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
    token_personalizado = "token"
    headers = {
        "Token": token_personalizado
    }

    # Realizando a requisição GET para buscar todas as disciplinas
    response_disciplinas = session.get(get_all_disciplinas_url, headers=headers)

    if response_disciplinas.status_code == 200:
        try:
            disciplinas_data = response_disciplinas.json()
            print("Busca de disciplinas bem-sucedida:", disciplinas_data)
        except ValueError:
            print("Resposta recebida não é JSON válido:", response_disciplinas.text)
    else:
        print(f"Erro ao buscar disciplinas: {response_disciplinas.status_code}", response_disciplinas.text)
else:
    print("Falha no login:", response_login.text)
