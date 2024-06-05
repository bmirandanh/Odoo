import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
get_all_tipocancelamento_url = f"{odooserver_url}/api/tipocancelamento/all"
# Iniciar sessão
session = requests.Session()
# Certifique-se de que 'token_personalizado' é o token obtido da maneira correta após a autenticação
token_personalizado = "token"  # Substitua pelo seu token real
headers = {
    "Token": token_personalizado
}
# Realizando a requisição GET para buscar todos os tipos de cancelamento
response_tipocancelamento = session.get(get_all_tipocancelamento_url, headers=headers)
if response_tipocancelamento.status_code == 200:
    try:
        tipocancelamento_data = response_tipocancelamento.json()
        print("Busca de tipos de cancelamento bem-sucedida:", tipocancelamento_data)
    except ValueError:
        print("Resposta recebida não é JSON válido:", response_tipocancelamento.text)
else:
    print(f"Erro ao buscar tipos de cancelamento: {response_tipocancelamento.status_code}", response_tipocancelamento.text)