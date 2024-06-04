import requests
import json
    
# Configuração inicial
odooserver_url = "http://odooserver:8069"
cod_curriculo = "CURR001"  # Substitua pelo código da disciplina que deseja atualizar
attribute = None  # Atributo específico a ser atualizado, se aplicável
# Substitua 'seu_token_aqui' pelo valor real do token
token_personalizado = "token"
# Montando a URL da API para atualização da disciplina
update_curriculo_url = f"{odooserver_url}/api/curriculo/update/{cod_curriculo}" + (f"/{attribute}" if attribute else "")
# Preparando os dados para atualização
update_data = {
    "name": "Novo curr",  # Ajuste conforme necessário
    # Adicione outros campos de acordo com os requisitos
}
# Iniciar sessão
session = requests.Session()
headers = {
    "Token": token_personalizado,  # Enviando o token personalizado para autenticação
}
# Realizando a requisição PUT para atualizar o currículo
response_update = session.put(update_curriculo_url, headers=headers, data=json.dumps(update_data))
print("Atualização do currículo bem-sucedida:", response_update.json())
