import requests
import os

api_key = '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'  # Substitua isso pela sua chave da API da OpenAI
headers = {'Authorization': f'Bearer {api_key}'}
file_id = 'file-DALbHoLXr11Yu50lai5nWJzB'  # Substitua isso pelo ID do arquivo que você quer recuperar

response = requests.get(f'https://api.openai.com/v1/files/{file_id}/content', headers=headers)

# A resposta será o conteúdo do arquivo
print(response.text)