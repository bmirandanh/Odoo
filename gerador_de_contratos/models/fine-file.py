import requests

url = 'https://api.openai.com/v1/files'
headers = {
    'Authorization': 'Bearer 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'
}

data = {
    'purpose': 'fine-tune'
}

with open('\addons\gerador_de_contratos\models\treinamento_tuning.jsonl', 'rb') as f:
    files = {
        'file': f
    }
    response = requests.post(url, headers=headers, data=data, files=files)

print(response.json())