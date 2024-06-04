import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
create_tipocancelamento_url = f"{odooserver_url}/api/tipocancelamento/create"
# Dados para o novo tipo de cancelamento
tipo_cancelamento_data = {
    "nome": "Estorno",
    "descricao": "Estorno completo do valor",
    "color": 3,  # 1 a 10
    "cod_cancelamento": "EST2024"
}
# Token personalizado para autenticação nas requisições à API
token_personalizado = "token"  # Substitua pelo seu token real
# Cabeçalhos para incluir o token personalizado
headers = {
    "Content-Type": "application/json",
    "Token": token_personalizado
}
# Iniciar sessão
session = requests.Session()
# Realizando a requisição POST para criar o tipo de cancelamento
response_create = session.post(create_tipocancelamento_url, headers=headers, json=tipo_cancelamento_data)
if response_create.status_code == 200:
    try:
        tipo_cancelamento_created = response_create.json()
        print("Criação do tipo de cancelamento bem-sucedida:", tipo_cancelamento_created)
    except ValueError:
        print("Resposta recebida não é JSON válido:", response_create.text)
else:
    print(f"Erro ao criar o tipo de cancelamento: {response_create.status_code}", response_create.text)

