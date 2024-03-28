import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"

# Substitua pelo código real da variante do currículo que deseja buscar
cod_variante = "VAR001"  # Substitua pelo valor correto
get_curriculo_var_url = f"{odooserver_url}/api/curriculovariant/{cod_variante}"

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

    # Realizando a requisição GET para buscar a variante do currículo específica
    response_curriculo_var = session.get(get_curriculo_var_url, headers=headers)

    if response_curriculo_var.status_code == 200:
        try:
            curriculo_var_data = response_curriculo_var.json()
            print("Busca da variante do currículo bem-sucedida:", curriculo_var_data)
        except ValueError:
            print("Resposta recebida não é JSON válido:", response_curriculo_var.text)
    else:
        print(f"Erro ao buscar a variante do currículo: {response_curriculo_var.status_code}", response_curriculo_var.text)
else:
    print("Falha no login:", response_login.text)
