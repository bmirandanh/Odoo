import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
cod_ingresso = "VIP8021"  # Substitua pelo código do tipo de ingresso que deseja atualizar
attribute = None  # Atributo específico a ser atualizado, se aplicável
# Substitua 'token' pelo valor real do token
token_personalizado = "token"
# Montando a URL da API para atualização do tipo de ingresso
update_tipoingresso_url = f"{odooserver_url}/api/tipoingresso/update/{cod_ingresso}" + (f"/{attribute}" if attribute else "")
# Preparando os dados para atualização
update_data = {
    "nome": "Nome Atualizado do Tipo de Ingresso",  # Ajuste conforme necessário
    # Adicione outros campos de acordo com os requisitos
}
# Iniciar sessão
session = requests.Session()
headers = {
    "Token": token_personalizado,  # Enviando o token personalizado para autenticação
}
# Realizando a requisição PUT para atualizar o tipo de ingresso
response_update = session.put(update_tipoingresso_url, headers=headers, data=json.dumps(update_data))  
# Usando data= ao invés de json=
if response_update.status_code == 200:
    print("Atualização do tipo de ingresso bem-sucedida:", response_update.json())
else:
    print(f"Erro ao atualizar o tipo de ingresso: {response_update.status_code}", response_update.text)