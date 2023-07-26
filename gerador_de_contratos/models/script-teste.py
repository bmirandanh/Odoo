import requests
import json
import copy

ODOO_URL = 'http://odooserver:8069'
DATABASE = 'devpostgresql40'
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
    print(response.json()) 
    return response.cookies['session_id']

def call_odoo_method():
    url = ODOO_URL + '/web/dataset/call_kw'
    headers = {
        "Content-Type": "application/json",
        "Cookie": f'session_id={authenticate_odoo()}'
    }
    
    data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": 'contract.contract',
            "method": 'get_sales_contract',
            "args": [[21], 21],  # 'sale_id' como argumento de args e de posição
            "kwargs": {}
        },
    
        "id": None
    }

    
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.json())

call_odoo_method()
