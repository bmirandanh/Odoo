import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
# Identificadores para busca específica
rp_professor = "FG202477644"  # Identificador do professor
ra_student = "2024018337"  # Identificador do aluno
# URLs das APIs para buscar professor e aluno específicos
get_professor_url = f"{odooserver_url}/api/professor/{rp_professor}"
get_student_url = f"{odooserver_url}/api/student/{ra_student}"
# Iniciar sessão
session = requests.Session()
print("Login bem-sucedido!")
token_personalizado = "token"  # Substitua pelo seu token real
# Headers para incluir o token personalizado
headers = {
    "token": token_personalizado
}
response_professor = session.get(get_professor_url, headers=headers)
professor_data = response_professor.json()
print("Busca do professor bem-sucedida:", professor_data)
# Realizando a requisição GET para buscar o aluno específico
response_student = session.get(get_student_url, headers=headers)
student_data = response_student.json()
print("Busca do aluno bem-sucedida:", student_data)