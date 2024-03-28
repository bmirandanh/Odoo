import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
get_all_matricula_url = f"{odooserver_url}/api/matricula/all"  # Certifique-se de que este é o URL correto para o método GET

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
    
    # Realizando a requisição GET para buscar todas as matrículas
    response_matricula = session.get(get_all_matricula_url, headers=headers)

    # Verificar a resposta
    if response_matricula.status_code == 200:
        try:
            matricula_data = response_matricula.json()
            print("Busca de matrículas bem-sucedida:", matricula_data)
        except ValueError:
            print("Resposta recebida não é JSON válido:", response_matricula.text)
    else:
        print(f"Erro ao buscar matrículas: {response_matricula.status_code}", response_matricula.text)
else:
    print("Falha no login:", response_login.text)
    