import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"

# Substitua 'seu_token_aqui' pelo valor real do token
token_personalizado = "token"

# Substitua pelo código real do tipo de cancelamento que deseja deletar
cod_curso = "34tt3t4"  # Ajuste este valor conforme necessário
delete_cursos_url = f"{odooserver_url}/api/cursos/delete/{cod_curso}"

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

    # Realizando a requisição DELETE para deletar o tipo de cancelamento específico
    response_delete = session.delete(delete_cursos_url, headers=headers)

    if response_delete.status_code == 200:
        try:
            result = response_delete.json()
            print("Deleção do tipo de cancelamento bem-sucedida:", result)
        except ValueError as e:
            print("Resposta recebida não é JSON válido:", response_delete.text)
    else:
        print(f"Erro ao deletar o tipo de cancelamento: {response_delete.status_code}", response_delete.text)
else:
    print("Falha no login:", response_login.text)
