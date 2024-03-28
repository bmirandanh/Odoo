import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
login_url = f"{odooserver_url}/web/session/authenticate"

# Substitua pelo número de matrícula real que deseja usar para gerar o certificado
numero_matricula = "wwwww4014937"

generate_certificate_url = f"{odooserver_url}/api/generate_certificate/{numero_matricula}"  # Ajuste para o endpoint correto



# Dados de autenticação
login_data = {
    "jsonrpc": "2.0",
    "params": {
        "login": "admin",
        "password": "admin",
        "db": "devpostgresql001"
    }
}

# Iniciar sessão
session = requests.Session()

# Tentativa de login
response_login = session.post(login_url, json=login_data)
if response_login.status_code == 200 and response_login.json().get("result"):
    print("Login bem-sucedido!")

    # Substitua 'token_personalizado' pelo token real obtido após autenticação
    token_personalizado = "token"  # Substitua pelo seu token real
    headers = {
        "Token": token_personalizado,
    }

    # Realizando a requisição GET para gerar o certificado
    response_certificate = session.get(generate_certificate_url, headers=headers, stream=True)
    
    if response_certificate.status_code == 200:
        filename = f"certificado_{numero_matricula}.pdf"
        with open(filename, 'wb') as f:
            f.write(response_certificate.content)
        print(f"Certificado gerado com sucesso e salvo como {filename}")
    else:
        print(f"Erro ao gerar o certificado: {response_certificate.status_code}", response_certificate.text)
else:
    print("Falha no login:", response_login.text)
