import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
get_all_tipoingresso_url = f"{odooserver_url}/api/tipoingresso/all"
# Iniciar sessão
session = requests.Session()
# Certifique-se de que 'token_personalizado' é o token obtido da maneira correta após a autenticação
token_personalizado = "token"
headers = {
    "Token": token_personalizado
}
# Realizando a requisição GET para buscar todos os tipos de ingresso
response_tipoingresso = session.get(get_all_tipoingresso_url, headers=headers)
if response_tipoingresso.status_code == 200:
    try:
        tipoingresso_data = response_tipoingresso.json()
        print("Busca de tipos de ingresso bem-sucedida:", tipoingresso_data)
    except ValueError:
        print("Resposta recebida não é JSON válido:", response_tipoingresso.text)
else:
    print(f"Erro ao buscar tipos de ingresso: {response_tipoingresso.status_code}", response_tipoingresso.text)
