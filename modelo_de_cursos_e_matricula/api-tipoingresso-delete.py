import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua 'token' pelo valor real do token
token_personalizado = "token"
# Substitua pelo código real do tipo de ingresso que deseja deletar
cod_ingresso = "VIP8021"
delete_tipoingresso_url = f"{odooserver_url}/api/tipoingresso/delete/{cod_ingresso}"
# Iniciar sessão
session = requests.Session()
# Headers para incluir o token personalizado
headers = {
    "Token": token_personalizado
}
# Realizando a requisição DELETE para deletar o tipo de ingresso específico
response_delete = session.delete(delete_tipoingresso_url, headers=headers)
if response_delete.status_code == 200:
    try:
        result = response_delete.json()
        print("Deleção do tipo de ingresso bem-sucedida:", result)
    except ValueError as e:
        print("Resposta recebida não é JSON válido:", response_delete.text)
else:
    print(f"Erro ao deletar o tipo de ingresso: {response_delete.status_code}", response_delete.text)
