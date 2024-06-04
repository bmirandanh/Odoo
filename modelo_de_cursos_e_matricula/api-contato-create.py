import requests

# Dados de autenticação
create_partner_url = "http://odooserver:8069/api/res_partner/create"
# Token de autenticação para a API customizada
token = "token"
# Cabeçalhos para a requisição
headers = {
    "Content-Type": "application/json",
    "Token": token  # Incluindo o token no cabeçalho
}
# Executando a requisição de login
session = requests.Session()
# Dados do parceiro a ser criado
partner_data = {
    "l10n_br_cnpj_cpf_formatted": "09842964094",
    "aluno": True,
    "professor": False,
    "name": "Aluno5",
    "email": "email@dominio.com"
}
response_partner = session.post(create_partner_url, headers=headers, json=partner_data)
print("Criação de parceiro bem-sucedida!", response_partner.json())
