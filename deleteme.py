import requests
canigo = True
page = 1
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
            print(str(totalitens) +
                  " - - - - - - - - - - - - - - - - - - - - - - - - - -")
            print(item['course']['id'])#canvas_id
            print(item['course']['name'])#name
            print(item['course']['public_description'])#description
            print(item['course']['self_enrollment_code'])#canvas_secode
            coursedet = coursedata(item['course']['id'])
            print(coursedet['image'])#thumbnail
            print(coursedet['uuid'])#unique
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
