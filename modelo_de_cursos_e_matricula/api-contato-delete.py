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
response_login = session.post(login_url, headers={"Content-Type": "application/json"}, json=login_data)

if response_login.status_code == 200 and response_login.json().get("result"):
    print("Login bem-sucedido!")

    # Após login bem-sucedido, realize a requisição GET para buscar todas as disciplinas
    # Nota: Não é necessário definir 'Content-Type': 'application/json' para GET
    # Como estamos usando a sessão, o token ou cookies de sessão já estão incluídos automaticamente
    response_disciplinas = session.get(get_all_disciplinas_url)

    # Avaliando a resposta
    if response_disciplinas.status_code == 200:
        try:
            disciplinas_data = response_disciplinas.json()
            print("Busca de disciplinas bem-sucedida:", disciplinas_data)
        except Exception as e:
            print("Falha ao decodificar a resposta como JSON:", e)
    else:
        print(f"Erro ao buscar disciplinas: {response_disciplinas.status_code}", response_disciplinas.text)
else:
    print("Falha no login:", response_login.text)
