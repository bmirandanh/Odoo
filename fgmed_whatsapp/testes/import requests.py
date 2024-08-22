import requests
import json

# Informações de envio
url = "https://graph.facebook.com/v14.0/235907209613582/messages"
access_token = "EAAS74FYKa3ABO9BNfOtPlZCA9ITVmRbj7GZAZAA7IztxQLwZAepI5YcxIJxm0idlKJ3jrzZB74hnrNIadK0YFhjI2wR2LzdvpPdZAbaEtiZChcDRXfZC8jZCDSyaJHdlZCMhnZAZCcEN45JteGGxasg8Rg0skVfdHjJQ1C5ZC2t6D4pYdehDReZAkFXaxxWHfe7mM9tApr"
recipient_phone_number = "5551989681135"
message_text = "Olá! Esta é uma mensagem de teste."

# Cabeçalhos da requisição
headers = {
    "Authorization": f"Bearer {access_token}",
}

# Corpo da requisição
data = {
    "messaging_product": "whatsapp",
    "to": recipient_phone_number,
    "type": "text",
    "text": {
        "body": message_text
    }
}

# Enviando a requisição
response = requests.post(url, headers=headers, data=json.dumps(data))

# Verificando a resposta
if response.status_code == 200:
    print("Mensagem enviada com sucesso!")
else:
    print("Falha ao enviar a mensagem.")
    print(f"Status Code: {response.status_code}")
    print(f"Resposta: {response.text}")
