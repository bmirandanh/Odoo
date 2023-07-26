import requests
import json

url_login = "http://odooserver:8069/web/session/authenticate"
url_search = "http://odooserver:8069/api/fgmed/canvas/search"
headers = {"Content-Type": "application/json"}

# Dados para a autenticação
data_login = {
    "params": {
        "db": "devpostgresql30",
        "login": "admin",
        "password": "admin"
    }
}

# Crie uma sessão que será usada para se autenticar e realizar a chamada à API
session = requests.Session()

# Autenticar
response_login = session.post(url_login, data=json.dumps(data_login), headers=headers)

# Verificar se a autenticação foi bem sucedida
if response_login.status_code == 200:
    result = response_login.json().get("result", {})
    if result.get("uid"):
        print("Autenticado com sucesso.")
        # Substitua 'valor_de_busca' pelo valor que você está buscando
        data_search = {
            "params": {
                "search_value": "medic"
            }
        }

        # Realizar a chamada à API
        response_search = session.post(url_search, data=json.dumps(data_search), headers=headers)

        # Verificar se a solicitação foi bem sucedida
        if response_search.status_code == 200:
            print(response_search.json())
        else:
            print(f"Erro na chamada à API: {response_search.status_code}")
    else:
        print("Falha na autenticação.")
else:
    print(f"Erro na autenticação: {response_login.status_code}")
