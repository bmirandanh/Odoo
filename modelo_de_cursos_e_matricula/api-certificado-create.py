import requests

# Configuração inicial
odooserver_url = "http://odooserver:8069"
# Substitua pelo número de matrícula real que deseja usar para gerar o certificado
numero_matricula = "we2e1111114015872"
generate_certificate_url = f"{odooserver_url}/api/generate_certificate/{numero_matricula}"  # Ajuste para o endpoint correto
# Dados de autenticação
# Iniciar sessão
session = requests.Session()
 # Substitua 'token_personalizado' pelo token real obtido após autenticação
token_personalizado = "token"  # Substitua pelo seu token real
headers = {
        "Token": token_personalizado,
}
# Realizando a requisição GET para gerar o certificado
response_certificate = session.get(generate_certificate_url, headers=headers, stream=True)
    
filename = f"certificado_{numero_matricula}.pdf"
with open(filename, 'wb') as f:
    f.write(response_certificate.content)
    print(f"Certificado gerado com sucesso e salvo como {filename}")

