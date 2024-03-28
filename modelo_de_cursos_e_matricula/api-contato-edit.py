import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
token = "token"
headers = {"Content-Type": "application/json", "Token": token}

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
response_login = session.post(login_url, headers=headers, json=login_data)
if response_login.status_code == 200:
    print("Login bem-sucedido!")

    # Configuração para edição
    matricula = "2024017884"
    edit_partner_url = f"{odooserver_url}/api/res_partner/edit_by_matricula/{matricula}"

    # Dados para atualização
    data_to_update = {
        "name": "Nome Atualizado 666",  # Exemplo de atualização de nome
        "email": "novoemail@dominio.com"  # Exemplo de atualização de email
        # Inclua outros campos que deseja atualizar
    }

    # Executar requisição POST para editar o contato
    response_edit = session.put(edit_partner_url, headers=headers, json=data_to_update)
    
    if response_edit.status_code == 200:
        print("Edição de parceiro bem-sucedida!", response_edit.json())
    else:
        print("Erro na edição do parceiro:", response_edit.text)
else:
    print("Falha no login:", response_login.text)