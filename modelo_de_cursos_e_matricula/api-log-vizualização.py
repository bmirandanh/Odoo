import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# URL da API para buscar logs de auditoria
url_audit_logs = f"{odooserver_url}/api/audit_logs"
# Iniciar sessão
session = requests.Session()
# Assumindo que o token personalizado é um Bearer token esperado no cabeçalho Authorization
token_personalizado = "token"  # Substitua pelo seu token real após a autenticação
headers = {
    "token": token_personalizado
}
# Parâmetros de data para a busca de logs
date_from = ""  # Substitua pela data inicial desejada
date_to = ""  # Substitua pela data final desejada
model_code= "234323333333333"  # Substitua pelo código de personalizado da classe específica, caso queira
# Realizando a requisição GET para buscar logs de auditoria
params = {
    #caso não tenha será todas as informações date_from e ou date_to será todas as informações
    'date_from': date_from, # data inicial
    'date_to': date_to # data final
    # model_code ficaria aqui como ('model_code': model_code)
}
response_audit_logs = session.get(url_audit_logs, headers=headers, params=params)
if response_audit_logs.status_code == 200:
    try:
        audit_logs_data = response_audit_logs.json()
        print("Busca de logs de auditoria bem-sucedida:", audit_logs_data)
    except ValueError:
        print("Resposta recebida não é JSON válido:", response_audit_logs.text)
else:
    print(f"Erro ao buscar logs de auditoria: {response_audit_logs.status_code}", response_audit_logs.text)

