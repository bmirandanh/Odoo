import requests
import json

ODOO_URL = 'http://odooserver:8069'
DATABASE = 'devpostgresql43'
USERNAME = 'admin'
PASSWORD = 'admin'

def authenticate_odoo():
    url = ODOO_URL + '/web/session/authenticate'
    headers = {"Content-Type": "application/json"}
    data = {
        "params": {
            "db": DATABASE,
            "login": USERNAME,
            "password": PASSWORD
        }
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.cookies['session_id']

def call_odoo_method(model, method, args=[], kwargs={}):
    url = ODOO_URL + '/web/dataset/call_kw'
    headers = {
        "Content-Type": "application/json",
        "Cookie": f'session_id={authenticate_odoo()}'
    }
    data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": model,
            "method": method,
            "args": args,
            "kwargs": kwargs
        },
        "id": None,
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.json()

# Chamada ao método get_sale_order_info no modelo api.sale.order.info com o ID 21
response_data = call_odoo_method("api.sale.order.info", "get_sale_order_info", [21])
print(response_data)
