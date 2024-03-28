import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
get_all_curso_url = f"{odooserver_url}/api/cursos/all"

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
        "token": token_personalizado,
    }

    # Realizando a requisição GET para buscar todos os cursos
    response_curso = session.get(get_all_curso_url, headers=headers)

    try:
        curso_data = response_curso.json()
        print("Busca de cursos bem-sucedida:", curso_data)
    except ValueError:
        print("Resposta recebida não é JSON válido:", response_curso.text)
