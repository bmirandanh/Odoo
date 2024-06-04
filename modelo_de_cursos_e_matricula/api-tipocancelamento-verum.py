import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua pelo código real do tipo de cancelamento que deseja buscar
cod_cancelamento = "ESTO2394"  # Substitua pelo valor correto
get_tipocancelamento_url = f"{odooserver_url}/api/tipocancelamento/{cod_cancelamento}"
# Assumindo que o token personalizado é um Bearer token esperado no cabeçalho Authorization
token_personalizado = "token"  # Substitua pelo seu token real
# Iniciar sessão
session = requests.Session()
headers = {
    "Token": token_personalizado  # Inclua o token personalizado aqui
}
# Realizando a requisição GET para buscar o tipo de cancelamento específico
response_tipocancelamento = session.get(get_tipocancelamento_url, headers=headers)
if response_tipocancelamento.status_code == 200:
    try:
        tipo_cancelamento_data = response_tipocancelamento.json()
        print("Busca do tipo de cancelamento bem-sucedida:", tipo_cancelamento_data)
    except ValueError:
        print("Resposta recebida não é JSON válido:", response_tipocancelamento.text)
else:
    print(f"Erro ao buscar o tipo de cancelamento: {response_tipocancelamento.status_code}", response_tipocancelamento.text)
