import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua pelo código real do currículo que deseja buscar
cod_curriculo = "CURR001"  # Substitua pelo valor correto
get_curriculo_url = f"{odooserver_url}/api/curriculo/{cod_curriculo}"
# Iniciar sessão
session = requests.Session()

# Assumindo que o token personalizado é um Bearer token esperado no cabeçalho Authorization
token_personalizado = "token"  # Substitua pelo seu token real
headers = {
    "Token": token_personalizado  # Inclua o token personalizado aqui
}
# Realizando a requisição GET para buscar o currículo específico
response_curriculo = session.get(get_curriculo_url, headers=headers)
curriculo_data = response_curriculo.json()
print("Busca do currículo bem-sucedida:", curriculo_data)

