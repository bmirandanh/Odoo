import codecs
import json
import chardet

with open(r'\\odooserver\samba\addons\gerador_de_contratos\models\treinamento_fine_tuning.jsonl', 'rb') as f:
    result = chardet.detect(f.read())

with codecs.open(r'\\odooserver\samba\addons\gerador_de_contratos\models\treinamento_fine_tuning.jsonl', 'r', encoding=result['encoding']) as f:
    lines = f.readlines()

with codecs.open(r'\\odooserver\samba\addons\gerador_de_contratos\models\treinamento_fine_tuning_utf8.jsonl', 'w', 'utf-8') as f:
    for line in lines:
        f.write(line)