import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua com os valores corretos
numero_matricula = "21d24017569"
cod_disciplina = "23423ffffffffff"
nova_nota = "7"  # nota como string, ajuste conforme o esperado pela API, ou seja seu ID no Odoo
# Iniciar sessão
session = requests.Session()
# Substitua 'token' pelo valor real do token
token_personalizado = "token"
# Montando a URL da API para atualização da nota do registro de disciplina
edit_nota_url = f"{odooserver_url}/api/registrodisciplina/editnota/{numero_matricula}/{cod_disciplina}/{nova_nota}"
# Preparando os dados para atualização
headers = {
    "Token": token_personalizado,  # Enviando o token personalizado para autenticação
}
# Preparando os dados para atualização
update_data = {
    "numero_matricula": numero_matricula,
    "cod_disciplina": cod_disciplina,
    "nova_nota": nova_nota,
}
# Realizando a requisição PUT para atualizar a nota
response_update = session.put(edit_nota_url, headers=headers, json=update_data)
if response_update.status_code == 200:
    print("Atualização da nota bem-sucedida:", response_update.json())
else:
    print(f"Erro ao atualizar a nota: {response_update.status_code}", response_update.text)