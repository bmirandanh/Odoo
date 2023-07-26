import os
import re
import requests
from pdf2image import convert_from_path
from PIL import Image


def get_pdf_url(course_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    base_url = 'https://medflix.fgmed.org'
    url = f'{base_url}/api/v1/courses/{course_id}/pages/home'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        content = data.get("body", "")

        print(content)

        if content:
            pdf_url_pattern = re.compile(r'data-url="([^"]+)"')
            match = pdf_url_pattern.search(content)

            if match:
                pdf_url = match.group(1)
            
                # Verificar se o 'data-url' contém um link do YouTube ou não possui ".pdf"
                if 'youtube' in pdf_url or '.pdf' not in pdf_url:
                    print('Vídeo do YouTube ou URL inválida')
                    return None

                # Remover o prefixo https://medflix.fgmed.org
                pdf_url = pdf_url.replace('https://medflix.fgmed.org', '')

                return pdf_url
            else:
                print('Atributo "data-url" não encontrado.')
                return None
        else:
            print("Conteúdo não encontrado no JSON.")
            return None
    else:
        print(f"Erro ao fazer a requisição: {response.status_code}")
        return None


def download_pdf(pdf_url, destination):
    headers = {'Referer': 'https://medflix.fgmed.org'}
    response = requests.get(pdf_url, headers=headers)

    if response.status_code == 200: 
        with open(destination, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Erro ao baixar o arquivo PDF: {response.status_code}")
        return False

    return True


def pdf_page_to_image(pdf_file, output_folder, output_format, page_number=0):
    output_filename = os.path.splitext(os.path.basename(pdf_file))[0] + f'.{output_format}'
    output_path = os.path.join(output_folder, output_filename)

    pages = convert_from_path(pdf_file, dpi=300, first_page=page_number+1, last_page=page_number+1, poppler_path='C:/poppler/bin')
    image = pages[0]

    image.save(output_path, format=output_format)
    print(f"Imagem salva como {output_path}")


if __name__ == "__main__":
    access_token = 'vjzQWopnMFML5nGGUFNqQ7afpnPUSsWU2mkv7JLAi7TOPI2Av9ZuYzlmpBRg5NVw'
    output_folder = 'ImagemPDF'
    output_format = 'webp'
    page_number = 0

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for course_id in range(4452, 10001):
        print(f"Processando o curso ID: {course_id}")

        pdf_url = get_pdf_url(course_id, access_token)

        if pdf_url:
            full_pdf_url = f'https://fgmedflix.b-cdn.net/{pdf_url}'

            pdf_filename = os.path.basename(pdf_url)
            pdf_filename = pdf_filename[:215]

            destination = os.path.join(output_folder, pdf_filename)
            
            success = download_pdf(full_pdf_url, destination)

            if not success:
                continue

            pdf_page_to_image(destination, output_folder, output_format, page_number)

            # Excluir o arquivo PDF baixado
            os.remove(destination)
        else:
            print(f"Não foi possível obter a URL do PDF para o curso ID: {course_id}")