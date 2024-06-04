import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"
# Atualize o URL para o correto, conforme definido na rota da API para buscar registros de disciplina por matrícula
numero_matricula = "qqwwwwwwwwwwww4012710"  # Substitua pelo número real da matrícula desejada
get_registro_disciplina_url = f"{odooserver_url}/api/registrodisciplina/{numero_matricula}"
# Iniciar sessão
session = requests.Session()
# Substitua 'token' pelo token real obtido após autenticação
token_personalizado = "token"  # Substitua pelo seu token real
headers = {
    "Token": token_personalizado
}
# Realizando a requisição GET para buscar os registros de disciplina da matrícula especificada
response_registros = session.get(get_registro_disciplina_url, headers=headers)
# Verificar a resposta
if response_registros.status_code == 200:
    try:
        registros_data = response_registros.json()
        print("Busca de registros de disciplina bem-sucedida:", registros_data)
    except ValueError:
        print("Resposta recebida não é JSON válido:", response_registros.text)
else:
    print(f"Erro ao buscar registros de disciplina: {response_registros.status_code}", response_registros.text)
