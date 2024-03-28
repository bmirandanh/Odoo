import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"

# Substitua pelo código real do tipo de cancelamento que deseja buscar
cod_curriculo = "1d12"  # Substitua pelo valor correto
get_curso_url = f"{odooserver_url}/api/cursos/{cod_curriculo}"

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

    # Realizando a requisição GET para buscar o tipo de cancelamento específico
    response_curso = session.get(get_curso_url, headers=headers)

    if response_curso.status_code == 200:
        try:
            tipo_curso_data = response_curso.json()
            print("Busca do curso bem-sucedida:", tipo_curso_data)
        except ValueError:
            print("Resposta recebida não é JSON válido:", response_curso.text)
    else:
        print(f"Erro ao buscar o curso: {response_curso.status_code}", response_curso.text)
else:
    print("Falha no login:", response_login.text)
