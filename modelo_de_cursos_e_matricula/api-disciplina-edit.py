import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
cod_disciplina = "tes33"  # Substitua pelo código da disciplina que deseja atualizar
attribute = None  # Atributo específico a ser atualizado, se aplicável
# Substitua 'seu_token_aqui' pelo valor real do token
token_personalizado = "token"
# Montando a URL da API para atualização da disciplina
update_disciplina_url = f"{odooserver_url}/api/disciplina/update/{cod_disciplina}" + (f"/{attribute}" if attribute else "")
# Preparando os dados para atualização
update_data = {
    "name": "Nova Nome da Disciplina",  # Ajuste conforme necessário
    # Adicione outros campos de acordo com os requisitos
}
# Iniciar sessão
session = requests.Session()
headers = {
    "Token": token_personalizado,  # Enviando o token personalizado para autenticação
}
# Realizando a requisição PUT para atualizar a disciplina, Usando data= ao invés de json=
response_update = session.put(update_disciplina_url, headers=headers, data=json.dumps(update_data))  
print("Atualização da disciplina bem-sucedida:", response_update.json())
