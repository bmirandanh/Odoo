import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
numero_matricula = "21e2e4011895"  # Substitua pelo número da matrícula que deseja atualizar
# Substitua 'token' pelo valor real do token
token_personalizado = "token"
# Montando a URL da API para atualização da matrícula
update_matricula_url = f"{odooserver_url}/api/matricula/update/{numero_matricula}"
# Preparando os dados para atualização
update_data = {
    "nome_do_aluno": 33,  # Ajuste conforme necessário
    # Adicione outros campos de acordo com os requisitos
}
# Iniciar sessão
session = requests.Session()
headers = {
    "Token": token_personalizado,  # Enviando o token personalizado para autenticação
}
# Realizando a requisição PUT para atualizar a matrícula
response_update = session.put(update_matricula_url, headers=headers, data=json.dumps(update_data))
if response_update.status_code == 200:
    print("Atualização da matrícula bem-sucedida:", response_update.json())
else:
    print(f"Erro ao atualizar a matrícula: {response_update.status_code}", response_update.text)

