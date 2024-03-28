import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"

# Substitua 'seu_token_aqui' pelo valor real do token
token_personalizado = "token"

# Substitua pelo código real da disciplina que deseja buscar
cod_disciplina = "regre"
get_disciplina_url = f"{odooserver_url}/api/disciplina/{cod_disciplina}"

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

    # Headers para incluir o token personalizado
    headers = {
        "Token": token_personalizado
    }

    # Realizando a requisição GET para buscar a disciplina específica
    response_disciplina = session.get(get_disciplina_url, headers=headers)

    if response_disciplina.status_code == 200:
        try:
            disciplina_data = response_disciplina.json()
            print("Busca da disciplina bem-sucedida:", disciplina_data)
        except ValueError as e:
            print("Resposta recebida não é JSON válido:", response_disciplina.text)
    else:
        print(f"Erro ao buscar a disciplina: {response_disciplina.status_code}", response_disciplina.text)
else:
    print("Falha no login:", response_login.text)
