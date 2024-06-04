import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
token = "token"
headers = {"Content-Type": "application/json", "Token": token}
# Iniciar sessão
session = requests.Session()
# Configuração para edição
RA = "2024010697"
edit_partner_url = f"{odooserver_url}/api/res_partner/edit_by_registro/{RA}" 
# OU edit_partner_url = f"{odooserver_url}/api/res_partner/edit_by_cod_professor/{cod_professor}"
# Dados para atualização
data_to_update = {
    "name": "Nome Atualizado 666",  # Exemplo de atualização de nome
    "email": "novoemail@dominio.com"  # Exemplo de atualização de email
    # Inclua outros campos que deseja atualizar
}
# Executar requisição POST para editar o contato
response_edit = session.put(edit_partner_url, headers=headers, json=data_to_update)
print("Edição de parceiro bem-sucedida!", response_edit.json())