import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua pelo código real da variante do currículo que deseja buscar
cod_variante = "VAR001"  # Substitua pelo valor correto
get_curriculo_var_url = f"{odooserver_url}/api/curriculovariant/{cod_variante}"
# Iniciar sessão
session = requests.Session()
# Assumindo que o token personalizado é um Bearer token esperado no cabeçalho Authorization
token_personalizado = "token"  # Substitua pelo seu token real
headers = {
    "Token": token_personalizado  # Inclua o token personalizado aqui
}
# Realizando a requisição GET para buscar a variante do currículo específica
response_curriculo_var = session.get(get_curriculo_var_url, headers=headers)
curriculo_var_data = response_curriculo_var.json()
print("Busca da variante do currículo bem-sucedida:", curriculo_var_data)

