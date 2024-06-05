import requests
import json

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua 'token' pelo valor real do token
token_personalizado = "token"
# Substitua pelo número real da matrícula que deseja deletar
numero_matricula = "MATR123456"  # Ajuste este valor conforme necessário
delete_matricula_url = f"{odooserver_url}/api/matricula/{numero_matricula}"
# Iniciar sessão
session = requests.Session()
# Headers para incluir o token personalizado
headers = {
    "Token": token_personalizado  # Token da sessão após login bem-sucedido
}
# Realizando a requisição DELETE para deletar a matrícula específica
response_delete = session.delete(delete_matricula_url, headers=headers)
if response_delete.status_code == 200:
    try:
        result = response_delete.json()
        print("Deleção da matrícula bem-sucedida:", result)
    except ValueError as e:
        print("Resposta recebida não é JSON válido:", response_delete.text)
else:
    print(f"Erro ao deletar a matrícula: {response_delete.status_code}", response_delete.text)

