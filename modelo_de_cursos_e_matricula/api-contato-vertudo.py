import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# URLs das APIs para buscar professores e alunos
url_professors = f"{odooserver_url}/api/professors/all"
url_students = f"{odooserver_url}/api/students/all"
# Iniciar sessão
session = requests.Session()
token_personalizado = "token"
headers = {
    "Token": token_personalizado
}
# Realizando a requisição GET para buscar todos os professores
response_professors = session.get(url_professors, headers=headers)
professors_data = response_professors.json()
print("Busca de professores bem-sucedida:", professors_data)

# Realizando a requisição GET para buscar todos os alunos
response_students = session.get(url_students, headers=headers)
students_data = response_students.json()
print("Busca de alunos bem-sucedida:", students_data)

