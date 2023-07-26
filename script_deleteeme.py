import requests
from xmlrpc import client
from unidecode import unidecode
from django.utils.text import slugify
import time

canigo = True
page = 80
totalitens = 0


def coursedata(courseid):
    url = "https://medflix.fgmed.org/api/v1/courses/" + \
        str(courseid)+"?include[]=course_image&access_token=vjzQWopnMFML5nGGUFNqQ7afpnPUSsWU2mkv7JLAi7TOPI2Av9ZuYzlmpBRg5NVw"
    toreturn = {'uuid': '', 'image': ''}
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            # print(item, data[item])
            uuid = data['uuid'] #unique
            image = data['image_download_url']#thumbnail
            toreturn['image'] = data['image_download_url']
            toreturn['uuid'] = data['uuid']
    return (toreturn)


def listcourses(page, totalitens):
    url = "https://medflix.fgmed.org/api/v1/search/all_courses?page=" + \
        str(page)+"&per_page=50"
    response = requests.get(url)
    results = 0
    if response.status_code == 200:
        data = response.json()
        for item in data:
            canvas_id = item['course']['id']#canvas_id
            name = item['course']['name']#name
            description = item['course']['public_description'][:5]#description
            descriptionA = unidecode(description)
            descriptionB = slugify(description)
            content_type = ''
            if descriptionB == "video":
                    content_type = 2
            else:
                    content_type = 1
            canvassecod = item['course']['self_enrollment_code']#canvas_secode
            coursedet = coursedata(item['course']['id'])
            thumbnail = coursedet['image']#thumbnail
            unique = coursedet['uuid']#unique


   # Conecte-se ao servidor Odoo
            while True: 
                try:
                    url = 'https://devst.fgmed.org'
                    db = 'devst.fgmed.org'
                    username = 'canvas.connector'
                    password = 'canvaspass'
                    common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
                    uid = common.authenticate(db, username, password, {})
                    models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                    break  # Saindo do loop se tudo foi bem-sucedido
                except ConnectionRefusedError:
                    print("Conexão recusada. Tentando novamente em 10 segundos...")
                    time.sleep(10)  # Aguardando 10 segundos antes de tentar reconectar

            
            id = models.execute_kw(db, uid, password, 'fgmed.canvas.content', 'create', 
            [{
                'name': name,
                'description': descriptionB,
                'total_time': 0,
                'custom_title': '',
                'content_type': content_type,
                'thumbnail': thumbnail,
                'canvas_secode':canvassecod,
                'canvas_id': canvas_id,
                'unique': unique   
                 
            }])
            del models
            del common

            
            print('Novo registro criado na classe Fgmed Canvas Content ')
            
            totalitens += 1
            results += 1                 
            
    else:
        print("Erro ao fazer a requisição: ", response.status_code)
    return (results)


while canigo == True:
    print("Pagina: "+str(page))
    results = listcourses(page, totalitens)
    if (results < 1):
        canigo = False
    page += 1