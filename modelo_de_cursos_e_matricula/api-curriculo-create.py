import requests
# Configuração inicial
odooserver_url = "http://odooserver:8069"
# URLs para a operação de DELETE
delete_by_matricula_url_template = f"{odooserver_url}/api/res_partner/delete_by_matricula/{{matricula}}"
delete_by_cod_professor_url_template = f"{odooserver_url}/api/res_partner/delete_by_cod_professor/{{cod_professor}}"
# Token da sessão (assumindo que você tenha uma forma de obter esse token)
token = "token"
# Iniciar sessão
session = requests.Session()
# Defina um dos seguintes valores, dependendo do que deseja deletar
matricula_aluno = "2024012446"  # Substitua pelo código de matrícula real
cod_professor = None  # Substitua pelo código do professor real
# Seleciona a URL apropriada
if matricula_aluno:
    delete_url = delete_by_matricula_url_template.format(matricula=matricula_aluno)
elif cod_professor:
    delete_url = delete_by_cod_professor_url_template.format(cod_professor=cod_professor)
else:
    print("Nenhum parâmetro de identificação fornecido.")
    exit()
# Cabeçalhos para a requisição DELETE, incluindo o token de autenticação
headers = {
    "Token": token
}
# Realizando a requisição DELETE
response_delete = session.delete(delete_url, headers=headers)
result = response_delete.json()
print("Parceiro deletado com sucesso:", result)
