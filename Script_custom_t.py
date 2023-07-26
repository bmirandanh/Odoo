import requests
from xmlrpc import client
from unidecode import unidecode
from django.utils.text import slugify
import time
import random
import textwrap
from PIL import Image, ImageDraw, ImageFont
import math
import warnings
import hashlib
import os



canigo = True
page = 1
totalitens = 0


def hash_filename(filename):
    sha256 = hashlib.sha256()
    sha256.update(filename.encode('utf-8'))
    return sha256.hexdigest()

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
    url = "https://medflix.fgmed.org/api/v1/search/all_courses?page=" + str(page)+"&per_page=50"
    response = requests.get(url)
    results = []
    if response.status_code == 200:
        data = response.json()
        for item in data:
            name = item['course']['name']#name
            cores = ["#F2C4AF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#F2A694","#F2A6A0","#F29A83","#F2B4B4","#F2C8C8","#F2D7D7","#F2DDD9","#F2F2C2","#F2F2DC","#F2F2ED","#F2F2F2","#F5DEB3","#F5E3C5","#F5E5D5","#F5F5DC","#F7CAC9","#F7D1C4","#F7E7CE","#F7E7D1","#F7E9CF","#F7F2E1","#F7F2E8","#FA8072","#FAA460","#FAB9A8","#FADADD","#FADBD8","#FADCE4","#FADCE7","#FAE5D3","#FAE7B5","#FAE7BB","#FAE7CB","#FAE7DC","#FAEBD7","#FAEBE4","#FAF0E6","#FAFAD2","#FBAFAF","#FBC1C1","#FBE7B2","#FBE7CB","#FBE7DC","#FBEC5D","#FBF2DB","#FCB4D5","#FCD5CE","#FCDAE8","#FCDEBE","#FCF0C0","#FCF2D7","#FCF4D0","#FCF4DC","#FCF5D8","#FCF8CC","#FCFBF3","#FCFBE3","#FDE9E0","#FDF5E6","#FDFD96","#FDFDCE","#FE6F5E","#FEA904","#FEBAAD","#FEDBB1","#FEE5AC","#FEE5CD","#FEE5E1","#FEEEEE","#FEF2C0","#FEF5E7","#FEF7DE","#FEFCFF","#FF00FF","#FF1493","#FF2400","#FF3E96","#FF4040","#FF4500","#FF6347","#FF69B4","#FF6A6A","#FF6EB4","#FF7F50","#FF8C69","#FFA07A","#FFA500","#FFAEB9","#FFB347","#FFC0CB","#FFC1C1","#FFC7B6","#FFC8B4","#FFCBA4","#FFDAB9","#FFDEAD","#FFE1FF","#FFE4B5","#FFE4C4","#FFE4E1","#FFE7BA","#FFEBCD","#FFEFD5","#FFF0F5","#FFF5EE","#FFF68F","#FFF8DC","#FFFACD","#FFFAF0","#FFFAFA","#FFFBDC","#FFFBF0","#FFFC99","#FFFCF0","#FFFD5E","#FFFD8F","#FFFAED","#d1eecc", "#ade8f4", "#a7e8b4", "#7fd1c9", "#bee7d5", "#b5e5f5", "#b5e5c8", "#87bba2", "#9cd3d3", "#8cd0d3", "#6cb2ba", "#69c1c1", "#5ec7c0", "#74c6b8", "#5fa39e", "#84c5be", "#5e8c8d", "#5f9ea0", "#6ca19e", "#2d6b67", "#5f7c8a", "#49796b", "#4c6f73", "#416d8c", "#4e7da3", "#3f888f", "#478c8c", "#2a6b7c", "#005d8f", "#0077be", "#006699", "#007fff", "#0067a5", "#004b49", "#007ba7", "#0047ab", "#0066cc", "#33a1c9", "#00bfff", "#48d1cc", "#20b2aa", "#008080", "#00ced1", "#40e0d0", "#2f4f4f", "#008080", "#48d1cc", "#40e0d0", "#b0e0e6", "#008b8b", "#5f9ea0", "#8deeee", "#add8e6", "#87cefa", "#8fbc8f", "#2e8b57", "#3cb371", "#00fa9a", "#98fb98", "#00ff7f", "#66cdaa", "#7fffd4", "#7cfc00", "#556b2f", "#9acd32", "#6b8e23", "#3cb371", "#32cd32", "#228b22", "#8fbc8f", "#006400", "#00ff00", "#7fff00", "#90ee90", "#98fb98", "#00ff7f", "#2e8b57", "#3cb371", "#20b2aa", "#2f4f4f", "#008080", "#40e0d0", "#48d1cc", "#00ced1", "#87cefa", "#add8e6", "#b0e0e6", "#1e90ff", "#4169e1", "#6a5acd", "#483d8b", "#4b0082", "#9370db", "#7b68ee", "#e6e6fa", "#d8bfd8", "#ee82ee", "#da70d6", "#ff00ff", "#ba55d3", "#9400d3", "#9932cc", "#8a2be2", "#800080", "#4b0082", "#6a5acd", "#483d8b", "#7b68ee", "#4169e1", "#1e90ff", "#007fff", "#00bfff", "#87cefa", "#add8e6", "#b0e0e6", "#5f9ea0", "#66cdaa", "#8deeee", "#00ff7f", "#7cfc00", "#9acd32", "#228b22", "#006400", "#f5f5f5", "#ededed", "#e5e5e5", "#d7d7d7", "#c7c7c7", "#b7b7b7", "#a7a7a7", "#979797", "#868686", "#757575", "#636363", "#515151", "#3e3e3e", "#2b2b2b", "#181818", "#f2f2f2", "#e6e6e6", "#d9d9d9", "#cccccc", "#bfbfbf", "#b2b2b2", "#a6a6a6", "#999999", "#8c8c8c", "#808080", "#737373", "#666666", "#595959", "#4d4d4d", "#404040", "#f9f9f9", "#f2f2f2", "#ebebeb", "#e5e5e5", "#dedede", "#d7d7d7", "#d0d0d0", "#c9c9c9", "#c2c2c2", "#bcbcbc", "#b5b5b5", "#aeaeae", "#a7a7a7", "#a0a0a0", "#999999", "#f2fafd", "#e7f5fa", "#dceef7", "#d0e8f3", "#c3e1f0", "#b6daed", "#aad3ea", "#9dcbE7", "#90c4e4", "#83bde1", "#76b6de", "#6ab0db", "#5da9d8", "#50a2d5", "#439bd2", "#3695cf", "#f0f8f7", "#d9ebea", "#c2dfd9", "#abc2c8", "#95b6b8", "#7ea9a7", "#678c86", "#506e66", "#395046", "#222322", "#e5f6f4", "#c7e6db", "#a9d7c1", "#8bc7a8", "#6db892", "#4fa97a", "#318a61", "#236d4a", "#154f33", "#07311d", "#e4f4f3", "#c8e3e3", "#abd3d3", "#8ec3c3", "#72b3b3", "#55a3a3", "#389393", "#237474", "#104a4a", "#002424", "#e6f1f1", "#cce3e3", "#b3d6d6", "#99c9c9", "#80bcbc", "#66afaf", "#4d9e9e", "#357f7f", "#1c6060", "#003f3f", "#edf8f8", "#d2e9e9", "#b6dbdb", "#9acccc", "#7ebfbe", "#63aeae", "#4c9595", "#3a7a7a","#FFFFFF", "#FEFEFE", "#FDFDFD", "#FCFCFC", "#FBFBFB", "#FAFAFA", "#F9F9F9", "#F8F8F8", "#F7F7F7", "#F6F6F6", "#F5F5F5", "#F4F4F4", "#F3F3F3", "#F2F2F2", "#F1F1F1", "#F0F0F0", "#EFEFEF", "#EEEEEE", "#ECECEC", "#EBEBEB", "#EAEAEA", "#E9E9E9", "#E8E8E8", "#E7E7E7", "#E6E6E6", "#E5E5E5", "#E4E4E4", "#E3E3E3", "#E2E2E2", "#E1E1E1", "#E0E0E0", "#DFDFDF", "#DEDEDE", "#DDDDDD", "#DCDCDC", "#DBDBDB", "#DADADA", "#D9D9D9", "#D8D8D8", "#D7D7D7", "#D6D6D6", "#D5D5D5", "#D4D4D4", "#D3D3D3", "#D2D2D2", "#D1D1D1", "#D0D0D0", "#CFCFCF", "#CECECE", "#CDCDCD", "#CCCCCC", "#CBCBCB", "#CACACA", "#C9C9C9", "#C8C8C8","#C7C7C7", "#C6C6C6", "#C5C5C5", "#C4C4C4", "#C3C3C3", "#C2C2C2", "#C1C1C1", "#C0C0C0", "#BFBFBF", "#BEBEBE", "#BDBDBD", "#BCBCBC", "#BBBBBB", "#B9B9B9", "#B8B8B8", "#B7B7B7", "#B6B6B6", "#B5B5B5", "#B4B4B4", "#B3B3B3", "#B2B2B2", "#B1B1B1", "#B0B0B0", "#AFAFAF", "#AEAEAE", "#ADADAD", "#ACACAC", "#ABABAB", "#AAAAAA", "#A9A9A9", "#A8A8A8", "#A7A7A7", "#A6A6A6", "#A5A5A5", "#A4A4A4", "#A3A3A3", "#A2A2A2"]
            fontes = []
            caminho_fontes = "/custom/fontes/"  # caminho da pasta de fontes"

            for nome_fonte in os.listdir(caminho_fontes):
                if nome_fonte.endswith(".ttf"):  # filtrar apenas arquivos com extensão ".ttf"
                    fontes.append(nome_fonte)
            texto = name
            nome_arquivo = hash_filename(texto) + '.png'
            cor = random.choice(cores)
            fonte = random.choice(fontes)
            font = '/custom/fontes/'+fonte
            caminho_arquivo = r"/custom/" + nome_arquivo
            results.append((texto, font, cor, caminho_arquivo)) # armazena os resultados na lista
    return results # retorna a lista completa de resultados

def imageGenerator(text,fontname,color,filename):
    imagew = int(1280 * 1.5)
    imageh = int(740 * 1.5)
    imagearea = imagew * imageh
    textlen = len(text)
    chararea = imagearea // textlen
    charsqrt = int(math.sqrt(chararea))
    linelen = int(imagew / (charsqrt * 0.45))
    lines = textwrap.wrap(text, width = linelen)
    font = ImageFont.truetype(fontname, int(charsqrt * 0.85) )
    container = Image.new('RGBA', (650, 260), color=(0, 0, 0, 0))
    image = Image.new('RGBA', (imagew, imageh), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    x = 0
    y = 0
    maxwidth = 0
    for line in lines:
        pixelsize = draw.textsize(line, font=font)
        if(pixelsize[0] > maxwidth):
            maxwidth = pixelsize[0]

    for line in lines:
        pixelsize = draw.textsize(line, font=font)
        tempx = (int(maxwidth/2)) - (int(pixelsize[0] / 2))
        draw.text((tempx, y), line, font=font, fill=color)
        y += pixelsize[1]
    image = image.crop((0, 0, maxwidth, y))
    image.thumbnail((650, 260), Image.ANTIALIAS)
    pastey = 260 - image.height
    container.paste(image, (0, pastey))
    container.save(filename)



canigo = True
page = 1
totalitens = 0

while canigo:
    print("Pagina: "+str(page))
    results = listcourses(page, totalitens)
    if not results:
        canigo = False
    else:
        for result in results:
            texto, font, cor, caminho_arquivo = result
            imageGenerator(texto,font,cor,caminho_arquivo)
        page += 1
