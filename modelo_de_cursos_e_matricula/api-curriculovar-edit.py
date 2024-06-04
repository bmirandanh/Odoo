import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
token_personalizado = "token"  # Substitua pelo seu token real
# Substitua pelo código real da variante do currículo que deseja atualizar
cod_variante = "VAR001"
update_variant_url = f"{odooserver_url}/api/curriculovariant/update/{cod_variante}"
# Preparando os dados para atualização
update_data = {
    "name": "Nova Variante Atualizada",  # Exemplo de atualização
    # Adicione outros campos conforme necessário
}
# Iniciar sessão e realizar login
session = requests.Session()
# Headers para incluir o token personalizado
headers = {
    "Content-Type": "application/json",
    "Token": token_personalizado
}
# Realizando a requisição PUT para atualizar a variante do currículo
response_update = session.put(update_variant_url, headers=headers, data=json.dumps(update_data))
print("Atualização da variante do currículo bem-sucedida:", response_update.json())

